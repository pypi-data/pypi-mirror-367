from .base import _BaseClient
from .stocks import Stocks
import pandas as pd
import logging
from fmpxx.utils import round_raw_data

logger = logging.getLogger(__name__)

class Financials(_BaseClient):
    """Client for FMP Company Fundamentals API endpoints."""

    def __init__(self, api_key: str|None, timeout: int = 10, debug: bool = False):
        super().__init__(api_key, timeout)
        self.debug = debug
        if debug and not logger.handlers:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    def get_financials(
        self,
        symbol: str,
        statement: str,
        limit: int = 10,
        period: str = 'quarter',
        **query_params: dict[str, object]
    ) -> pd.DataFrame:
        """
        Fetch specific type of financial statement data.

        Args:
            symbol: Stock ticker symbol
            statement: Statement type ('income', 'balance', 'cash', 'ratios', 'enterprise-value', 'key-metrics', 'financial-growth')
            limit: Number of records to return
            period: Reporting period ('annual' or 'quarter')
            **query_params: Additional query parameters

        Returns:
            pd.DataFrame: Financial statement data

        Raises:
            ValueError: If statement parameter is invalid
        """
        endpoint_map = {
            "income": "income-statement",
            "balance": "balance-sheet-statement", 
            "cash": "cash-flow-statement"
        }

        if statement not in endpoint_map:
            raise ValueError(f"Invalid statement type: {statement}")

        params = {"limit": limit, "period": period, **query_params}
        data = self._make_request(f"{endpoint_map[statement]}/{symbol}", params)
        
        df = self._process_response(data)
        return self._ensure_dataframe(df)

    def get_merged_financials(self, symbol: str, limit: int = 40, period: str = 'quarter') -> pd.DataFrame | None:
        """
        Merge cash flow, income statement, and balance sheet financial statements.

        Args:
            symbol: Stock ticker symbol
            limit: Number of records to return
            period: Reporting period ('annual' or 'quarter')

        Returns:
            Optional[pd.DataFrame]: Merged financial statements DataFrame, None if data is invalid

        Note:
            - Uses inner join to ensure complete data across all three statements
            - Handles special stock data anomalies
            - Checks data continuity and completeness
        """
        # Get three financial statements
        income = self.get_financials(symbol, statement="income", period=period, limit=limit)
        balance = self.get_financials(symbol, statement="balance", period=period, limit=limit)
        cash = self.get_financials(symbol, statement="cash", period=period, limit=limit)

        # Check data completeness
        if income.empty or balance.empty or cash.empty:
            logger.warning(f"{symbol}'s financial statement data is incomplete")
            return None

        # Define merge keys
        on_list = [
            "cik", "fillingDate", "date", "symbol", 
            "period", "calendarYear", "reportedCurrency"
        ]

        # Merge financial statements
        merged_df = pd.merge(
            pd.merge(income, balance, how="inner", on=on_list),
            cash, how="inner", on=on_list
        )

        # Data cleaning and transformation
        merged_df = (
            merged_df.rename(columns={
                "date": "period_date",
                "fillingDate": "date",
                "netIncome_x": "netIncome"
            })
            .sort_values(by=["date", "acceptedDate_x"], ignore_index=True)
            .drop_duplicates(subset=["date"], keep="first", ignore_index=True)
            .assign(period_date=lambda x: pd.to_datetime(x["period_date"]))
        )

        # Handle special stocks
        special_symbols = [
            "ADT", "ALTR", "ARNC", "BEAM", "CEG", "CSC", "CTLT", "FTV", 
            "HLT", "HPE", "LDOS", "LW", "MMI", "MRNA", "OTIS", "PLL", 
            "S", "TWTR", "VNT"
        ]
        
        if symbol in special_symbols:
            merged_df = merged_df.drop([0]).reset_index(drop=True)

        # Check data continuity
        merged_df["verify"] = merged_df["period_date"].diff()
        if symbol == "CSC":
            return None

        # Validate reporting period
        for days in merged_df["verify"].tolist()[1:]:
            if days.days > 150:  # Normal interval is about 91 days
                logger.warning(f"{symbol} abnormal reporting period, incomplete data")
                return None

        # Final cleanup
        return (
            merged_df.drop(columns=["verify"])
            .fillna(value=0)
        )

    def get_stock_performance(self, symbol: str, limit: int = 12, period: str = 'quarter') -> pd.DataFrame | None:
        """
        Get comprehensive stock performance metrics using actual available financial data columns.
        
        Args:
            symbol (str): Stock ticker symbol
            limit (int): Number of quarters to return, default 8 quarters
            period (str): Reporting period, 'annual' or 'quarter'
            
        Returns:
            Optional[pd.DataFrame]: DataFrame containing comprehensive performance metrics, returns None if data invalid
        """
        # Get merged financial statements
        merged_df = self.get_merged_financials(symbol, limit=limit, period=period)
        if merged_df is None or merged_df.empty:
            return None
            
        # Based on actual available columns from AAPL.csv
        performance_df = merged_df[[
            'period_date', 'date', 'symbol', 'calendarYear', 'period',
            'revenue', 'grossProfitRatio', 'epsdiluted', 'operatingIncomeRatio', 
            'operatingIncome', 'freeCashFlow', 'totalDebt', 'totalAssets'
        ]].copy()
        
        # Calculate quality metrics
        performance_df['freeCashFlowMargin'] = performance_df['freeCashFlow'] / performance_df['revenue']
        performance_df['debtToAssetRatio'] = performance_df['totalDebt'] / performance_df['totalAssets']
        
        # Calculate year-over-year growth rates (annual YoY comparison)
        performance_df['period_date'] = pd.to_datetime(performance_df['period_date'])
        performance_df['year'] = performance_df['period_date'].dt.year
        performance_df['quarter'] = performance_df['period_date'].dt.quarter
        
        # Sort by date to ensure chronological order for YoY calculation
        performance_df = performance_df.sort_values('period_date')
        
        # Calculate year-over-year growth rates (annual YoY - periods=4 quarters = 1 year)
        performance_df['revenue_growth_rate'] = performance_df['revenue'].pct_change(periods=4)
        performance_df['operatingIncome_growth_rate'] = performance_df['operatingIncome'].pct_change(periods=4)
        performance_df['eps_diluted_growth_rate'] = performance_df['epsdiluted'].pct_change(periods=4)
        
        # Sort by date (oldest first)
        # performance_df = performance_df.sort_values('period_date', ascending=True)
        
        # Select final required columns
        result_df = performance_df[[
            'period_date', 'date', 'symbol', 'calendarYear', 'period',
            # Quality metrics
            'grossProfitRatio',
            'operatingIncomeRatio',
            'freeCashFlowMargin',
            'debtToAssetRatio',
            # Growth metrics
            'revenue', 'revenue_growth_rate',
            'operatingIncome', 'operatingIncome_growth_rate',
            # Valuation metrics
            'epsdiluted', 'eps_diluted_growth_rate'
        ]].copy()
        
        # Data cleaning
        return result_df.fillna(value=0).round(2)

    def get_earnings_his(self, symbol: str, period: int = 3) -> pd.DataFrame:
        """
        Fetch historical earnings calendar for a given symbol.

        Args:
            symbol: Stock ticker symbol
            period: Number of years to retrieve data for, defaults to 3

        Returns:
            pd.DataFrame: Historical earnings data
        """
        endpoint = f"historical/earning_calendar/{symbol}"
        params = {"limit": period * 4 + 4}  # Typically 4 empty records max
        
        data = self._make_request(endpoint, params)
        df = self._ensure_dataframe(self._process_response(data))
        
        if df.empty:
            return df
            
        # Process date adjustments for AMC (after market close) reports
        if 'date' in df.columns:
            df['date_adj'] = pd.to_datetime(df['date'])
            if 'time' in df.columns:
                df.loc[df['time'] == 'amc', 'date_adj'] += pd.Timedelta(days=1)
            
            df = (df
                  .drop(columns=['date'])
                  .rename(columns={'date_adj': 'date'})
                  .assign(is_fiscal=True)
                  .pipe(self._standardize_date_format)
                  .sort_values('date', ascending=False)
                  .reset_index(drop=True))
        
        return df

    def merge_eps_his(self, symbol: str, period: int = 3, enable_logging: bool = True) -> pd.DataFrame:
        """
        Generate PE and historical time series data.
        Note: If used after earnings release, need to wait for market open data, otherwise no close, latest epsttm will be deleted
        
        Args:
            symbol (str): Stock ticker symbol
            period (int): Number of years to retrieve historical data
            enable_logging (bool): Whether to enable logging, defaults to True
            
        Returns:
            pd.DataFrame: DataFrame containing PE calculation results
        """
        # 获取历史盈利数据
        eps_df = self.get_earnings_his(symbol, period)
        if eps_df.empty:
            logger.warning(f"No earnings data found for {symbol}")
            return pd.DataFrame()
            
        eps_df = eps_df.sort_values(by='date', ascending=True, ignore_index=True)
        
        if enable_logging:
            logger.info(f"Earnings data shape: {eps_df.shape}")
            logger.info(f"Earnings columns: {list(eps_df.columns)}")
        
        # 处理EPS数据
        eps_df['forward'] = eps_df.get('eps', pd.Series()).isnull()
        eps_df['eps'] = eps_df.get('eps', pd.Series()).fillna(eps_df.get('epsEstimated', pd.Series()))
        eps_df['eps_ttm'] = eps_df['eps'].rolling(4).sum()

        # 获取历史价格数据
        stocks_client = Stocks(self.api_key, self.timeout)
        his_df = stocks_client.historical_price_full(symbol, period=period)
        his_df = self._ensure_dataframe(his_df)
        
        if his_df.empty or 'date' not in his_df.columns or 'close' not in his_df.columns:
            logger.warning(f"No valid price data found for {symbol}")
            return pd.DataFrame()
            
        his_df = his_df[['date', 'close']].copy()

        # 确保日期格式一致
        eps_df_temp = pd.DataFrame(eps_df)
        eps_df = self._standardize_date_format(df=eps_df_temp)
        his_df_temp = pd.DataFrame(his_df)
        his_df = self._standardize_date_format(df=his_df_temp)
        
        # 合并数据
        merged_df = pd.merge(eps_df, his_df, on='date', how='outer', sort=True)
        
        if enable_logging:
            logger.info(f"Merged data shape: {merged_df.shape}")
        
        # 填充数据
        merged_df['eps_ttm'] = merged_df['eps_ttm'].backfill().forward_fill()
        merged_df['forward'] = merged_df['forward'].backfill()
        merged_df = merged_df.round(2)
        
        # 计算市盈率(PE)
        merged_df['pe'] = merged_df.apply(
            lambda row: row['close'] / row['eps_ttm'] if row['eps_ttm'] > 0 else 0, 
            axis=1
        )
        
        # 选择需要的列并删除没有收盘价的行
        selected = merged_df[
            ['date', 'eps_ttm', 'pe', 'close', 'eps', 'forward']
        ].dropna(subset=['close'])
        
        return selected


    def get_fiscal_close_chg(self, symbol: str, period: int = 3, enable_logging: bool = False) -> pd.DataFrame:
        """
        分析发布财报后close的变动
        
        Args:
            symbol (str): 股票代码
            period (int): 获取历史数据的年数
            enable_logging (bool): 是否启用日志记录，默认为False
            
        Returns:
            pd.DataFrame: 包含财报发布后收盘价变动的DataFrame
        """
        # 获取历史价格数据
        stocks_client = Stocks(self.api_key, self.timeout)
        his_df = stocks_client.historical_price_full(symbol, period=period)
        his_df = self._ensure_dataframe(his_df)
        
        if his_df.empty or 'date' not in his_df.columns or 'close' not in his_df.columns:
            logger.warning(f"No valid price data found for {symbol}")
            return pd.DataFrame()
            
        his_df = his_df[['date', 'close']].copy()

        # 获取历史盈利数据
        eps_df = self.get_earnings_his(symbol, period)
        if eps_df.empty:
            logger.warning(f"No earnings data found for {symbol}")
            return pd.DataFrame()
            
        eps_df = eps_df.sort_values(by='date', ascending=True, ignore_index=True)
        
        # 确保日期格式一致
        eps_df = self._standardize_date_format(eps_df)
        his_df = self._standardize_date_format(his_df)
        
        # 合并数据
        merged_df = pd.merge(eps_df, his_df, on='date', how='outer', sort=True)
        
        if enable_logging:
            logger.info(f"Merged data shape: {merged_df.shape}")
            logger.info(f"Merged data:\n{merged_df.head()}")
        
        # 可能会有周五盘后发布财报的情况，比如clsk，使用前值填充
        merged_df['close'] = merged_df['close'].forward_fill()
        
        if enable_logging:
            logger.info(f"After ffill:\n{merged_df.head()}")
        
        # 删除掉预估数据：删除date日期大于今天的行
        merged_df['date'] = pd.to_datetime(merged_df['date'])
        merged_df = merged_df[merged_df['date'] <= pd.Timestamp.now()]
        
        if enable_logging:
            logger.info(f"After filtering future dates:\n{merged_df.head()}")
        
        # 计算is_fiscal=True时的close变动比率，考虑盘后发布财报的情况
        merged_df['fiscal_chg'] = merged_df['close'].pct_change()
        
        if enable_logging:
            logger.info(f"After calculating fiscal_chg:\n{merged_df.head()}")
        
        # 只保留 is_fiscal 为 True 且不为 NA 的行
        if 'is_fiscal' in merged_df.columns:
            merged_df = merged_df[merged_df['is_fiscal'].notna() & merged_df['is_fiscal']]
        else:
            logger.warning("is_fiscal column not found")
            return pd.DataFrame()
            
        if enable_logging:
            logger.info(f"Final data:\n{merged_df}")
        
        # 后续根据导出情况，可以简化列
        return merged_df

    def revenue_by_segment(self, symbol: str, structure: str = 'product', period: str = 'quarter', limit: int = 10, output_format: str = 'json') -> dict | pd.DataFrame:
        """
        Fetch revenue breakdown by segment (geographic or product segments).
        
        Args:
            symbol: Stock ticker symbol
            structure: Segment type - 'geographic' for geographic segments, 'product' for product segments
            period: Reporting period ('annual' or 'quarter')
            limit: Number of records to return
            output_format: Output format - 'json' or 'pandas'. If None, uses instance default
            
        Returns:
            dict | pd.DataFrame: Revenue data segmented by specified structure
            
        Raises:
            ValueError: If structure parameter is invalid
        """
        if structure not in ['geographic', 'product']:
            raise ValueError(f"Invalid structure type: {structure}. Use 'geographic' or 'product'")
            
        # Use specified output format
        fmt = output_format
            
        # Use v4 API endpoint for revenue segmentation
        endpoint = f"revenue-{structure}-segmentation"
        params = {"symbol": symbol, "structure": "flat", "period": period, "limit": limit}
        
        # Temporarily override base URL for v4 endpoint
        original_base_url = self.BASE_URL
        self.BASE_URL = "https://financialmodelingprep.com/api/v4/"
        try:
            data = self._make_request(endpoint, params)
        finally:
            # Restore original base URL
            self.BASE_URL = original_base_url
            
        # Ensure we respect the limit even if API returns more data
        if isinstance(data, list) and len(data) > limit:
            data = data[:limit]
        
        # Handle special conversion for segment data structure
        if fmt == 'pandas':
            return self._convert_segment_data_to_df(data)
        else:
            return data

    def _convert_segment_data_to_df(self, data: list | dict) -> pd.DataFrame:
        """
        Convert nested segment revenue data to DataFrame format.
        
        Args:
            data: List of dictionaries with date as key and segment data as value
            
        Returns:
            pd.DataFrame: DataFrame with period_date as index and segments as columns
        """
        if not data:
            return pd.DataFrame()
            
        # Ensure data is a list
        if isinstance(data, dict):
            data = [data]
        
        # Convert to DataFrame directly
        rows = []
        for item in data:
            for date_str, segments in item.items():
                row = {'period_date': date_str}
                row.update(segments)
                rows.append(row)
        
        df = pd.DataFrame(rows)
        df['period_date'] = pd.to_datetime(df['period_date'])
        
        return df.sort_values('period_date', ascending=True).reset_index(drop=True)
