"""
Data Integration Service for StockSteward AI
Integrates multiple data sources including NSE Historical, Kaggle datasets, and public datasets
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging
from pathlib import Path
import requests
from kiteconnect import KiteConnect
from app.core.config import settings
from app.services.kite_service import kite_service

logger = logging.getLogger(__name__)

class DataIntegrationService:
    """
    Service to integrate multiple data sources:
    - NSE Historical data via KiteConnect
    - Kaggle datasets
    - Public financial datasets
    - Custom data sources
    """
    
    def __init__(self):
        self.kite = kite_service
        self.data_sources = {
            'nse': self.fetch_nse_data,
            'kaggle': self.fetch_kaggle_data,
            'alpha_vantage': self.fetch_alpha_vantage_data,
            'yfinance': self.fetch_yfinance_data,
            'custom': self.fetch_custom_data
        }
    
    async def fetch_nse_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime, 
        interval: str = "day",
        exchange: str = "NSE"
    ) -> pd.DataFrame:
        """
        Fetch historical data from NSE via KiteConnect
        """
        try:
            # Get instrument token
            quote = self.kite.get_quote(symbol, exchange)
            if not quote or 'error' in quote:
                logger.warning(f"Could not get quote for {symbol}: {quote.get('error', 'No data')}")
                return pd.DataFrame()
            
            instrument_token = quote.get('instrument_token')
            if not instrument_token:
                logger.error(f"No instrument token found for {symbol}")
                return pd.DataFrame()
            
            # Fetch historical data
            historical_data = self.kite.get_historical(
                symbol=symbol,
                from_date=start_date.strftime('%Y-%m-%d'),
                to_date=end_date.strftime('%Y-%m-%d'),
                interval=interval,
                exchange=exchange
            )
            
            if not historical_data:
                logger.warning(f"No historical data found for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            if df.empty:
                return df
            
            # Rename columns to standard format
            df.rename(columns={
                'date': 'timestamp',
                'open': 'open_price',
                'high': 'high_price',
                'low': 'low_price',
                'close': 'close_price',
                'volume': 'volume'
            }, inplace=True)
            
            # Add symbol column
            df['symbol'] = symbol
            df['exchange'] = exchange
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching NSE data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def fetch_kaggle_data(
        self, 
        dataset_path: str, 
        symbol: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch data from local Kaggle dataset
        """
        try:
            if not os.path.exists(dataset_path):
                logger.error(f"Kaggle dataset not found: {dataset_path}")
                return pd.DataFrame()
            
            # Determine file type and read accordingly
            if dataset_path.endswith('.csv'):
                df = pd.read_csv(dataset_path)
            elif dataset_path.endswith('.parquet'):
                df = pd.read_parquet(dataset_path)
            elif dataset_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(dataset_path)
            else:
                logger.error(f"Unsupported file format: {dataset_path}")
                return pd.DataFrame()
            
            # Standardize column names if needed
            column_mapping = {
                'Date': 'timestamp',
                'Timestamp': 'timestamp',
                'Open': 'open_price',
                'High': 'high_price', 
                'Low': 'low_price',
                'Close': 'close_price',
                'Volume': 'volume',
                'Adj Close': 'adj_close_price'
            }
            
            df.rename(columns=column_mapping, inplace=True)
            
            # Convert timestamp to datetime if it exists
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Add symbol if provided
            if symbol:
                df['symbol'] = symbol
                
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Kaggle data from {dataset_path}: {e}")
            return pd.DataFrame()
    
    async def fetch_alpha_vantage_data(
        self, 
        symbol: str, 
        api_key: str,
        function: str = "TIME_SERIES_DAILY",
        outputsize: str = "full"
    ) -> pd.DataFrame:
        """
        Fetch data from Alpha Vantage API
        """
        try:
            if not api_key:
                logger.error("Alpha Vantage API key not provided")
                return pd.DataFrame()
            
            base_url = "https://www.alphavantage.co/query"
            params = {
                'function': function,
                'symbol': symbol,
                'apikey': api_key,
                'outputsize': outputsize
            }
            
            response = requests.get(base_url, params=params)
            data = response.json()
            
            # Check for errors
            if "Error Message" in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return pd.DataFrame()
            
            if "Note" in data:
                logger.warning(f"Alpha Vantage note: {data['Note']}")
                return pd.DataFrame()
            
            # Extract time series data
            time_series_key = [key for key in data.keys() if 'Time Series' in key][0]
            time_series = data[time_series_key]
            
            # Convert to DataFrame
            df = pd.DataFrame(time_series).T
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            
            # Rename columns
            df.columns = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
            df = df.astype({'open_price': float, 'high_price': float, 'low_price': float, 'close_price': float, 'volume': int})
            
            df.reset_index(inplace=True)
            df.rename(columns={'index': 'timestamp'}, inplace=True)
            df['symbol'] = symbol
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def fetch_yfinance_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetch data from Yahoo Finance using yfinance
        """
        try:
            import yfinance as yf
            
            # Format symbol for Yahoo Finance (e.g., RELIANCE.NS for NSE)
            if '.' not in symbol:
                yf_symbol = f"{symbol}.NS"  # NSE suffix
            else:
                yf_symbol = symbol
            
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                logger.warning(f"No data found for {yf_symbol}")
                return pd.DataFrame()
            
            # Reset index to make date a column
            df.reset_index(inplace=True)
            
            # Rename columns to match our standard
            df.rename(columns={
                'Date': 'timestamp',
                'Datetime': 'timestamp',
                'Open': 'open_price',
                'High': 'high_price',
                'Low': 'low_price',
                'Close': 'close_price',
                'Volume': 'volume',
                'Adj Close': 'adj_close_price'
            }, inplace=True)
            
            df['symbol'] = symbol.split('.')[0]  # Remove exchange suffix
            df['exchange'] = 'NSE' if '.NS' in yf_symbol else 'OTHER'
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def fetch_custom_data(
        self, 
        file_path: str, 
        symbol: str,
        date_column: str = 'date',
        open_column: str = 'open',
        high_column: str = 'high',
        low_column: str = 'low',
        close_column: str = 'close',
        volume_column: str = 'volume'
    ) -> pd.DataFrame:
        """
        Fetch data from custom CSV/Excel file
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Custom data file not found: {file_path}")
                return pd.DataFrame()
            
            # Determine file type
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
            else:
                logger.error(f"Unsupported file format: {file_path}")
                return pd.DataFrame()
            
            # Rename columns to standard format
            column_mapping = {
                date_column: 'timestamp',
                open_column: 'open_price',
                high_column: 'high_price',
                low_column: 'low_price',
                close_column: 'close_price',
                volume_column: 'volume'
            }
            
            df.rename(columns=column_mapping, inplace=True)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Add symbol
            df['symbol'] = symbol
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching custom data from {file_path}: {e}")
            return pd.DataFrame()
    
    async def fetch_combined_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        data_source: str = 'nse',
        **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data from multiple symbols using specified data source
        """
        results = {}
        
        for symbol in symbols:
            if data_source == 'nse':
                df = await self.fetch_nse_data(symbol, start_date, end_date, **kwargs)
            elif data_source == 'kaggle':
                dataset_path = kwargs.get('dataset_path', '')
                df = await self.fetch_kaggle_data(dataset_path, symbol)
            elif data_source == 'alpha_vantage':
                api_key = kwargs.get('api_key', '')
                df = await self.fetch_alpha_vantage_data(symbol, api_key, **kwargs)
            elif data_source == 'yfinance':
                df = await self.fetch_yfinance_data(symbol, start_date, end_date)
            elif data_source == 'custom':
                file_path = kwargs.get('file_path', '')
                df = await self.fetch_custom_data(file_path, symbol, **kwargs)
            else:
                logger.error(f"Unknown data source: {data_source}")
                continue
            
            if not df.empty:
                results[symbol] = df
            else:
                logger.warning(f"No data retrieved for symbol: {symbol}")
        
        return results
    
    async def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data for ML/AI models
        """
        if df.empty:
            return df
        
        # Sort by timestamp
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Calculate additional technical indicators
        if 'close_price' in df.columns:
            # Moving averages
            df['sma_20'] = df['close_price'].rolling(window=20).mean()
            df['sma_50'] = df['close_price'].rolling(window=50).mean()
            df['ema_12'] = df['close_price'].ewm(span=12).mean()
            df['ema_26'] = df['close_price'].ewm(span=26).mean()
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # RSI
            delta = df['close_price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['bb_middle'] = df['close_price'].rolling(window=20).mean()
            bb_std = df['close_price'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            
            # Volatility
            df['volatility'] = df['close_price'].rolling(window=20).std()
            
            # Price change percentage
            df['price_change_pct'] = df['close_price'].pct_change() * 100
        
        # Fill NaN values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(method='ffill').fillna(0)
        
        return df
    
    async def get_features_for_llm(
        self,
        df: pd.DataFrame,
        lookback_days: int = 30
    ) -> Dict[str, Union[float, str, List[Dict]]]:
        """
        Prepare features for LLM consumption
        """
        if df.empty:
            return {}
        
        # Get recent data
        recent_df = df.tail(lookback_days) if len(df) > lookback_days else df
        
        # Calculate key metrics
        latest_price = recent_df['close_price'].iloc[-1] if 'close_price' in recent_df.columns else 0
        price_change_pct = recent_df['price_change_pct'].iloc[-1] if 'price_change_pct' in recent_df.columns else 0
        
        # Prepare market context for LLM
        context = {
            'latest_price': float(latest_price),
            'price_change_pct': float(price_change_pct),
            'trend': 'bullish' if price_change_pct > 0 else 'bearish' if price_change_pct < 0 else 'neutral',
            'volatility': float(recent_df['volatility'].iloc[-1]) if 'volatility' in recent_df.columns else 0,
            'rsi': float(recent_df['rsi'].iloc[-1]) if 'rsi' in recent_df.columns else 50,
            'macd': float(recent_df['macd'].iloc[-1]) if 'macd' in recent_df.columns else 0,
            'recent_high': float(recent_df['high_price'].max()) if 'high_price' in recent_df.columns else 0,
            'recent_low': float(recent_df['low_price'].min()) if 'low_price' in recent_df.columns else 0,
            'volume_avg': float(recent_df['volume'].mean()) if 'volume' in recent_df.columns else 0,
            'sma_20': float(recent_df['sma_20'].iloc[-1]) if 'sma_20' in recent_df.columns else 0,
            'sma_50': float(recent_df['sma_50'].iloc[-1]) if 'sma_50' in recent_df.columns else 0,
            'data_points': len(recent_df),
            'date_range': {
                'start': recent_df['timestamp'].iloc[0].isoformat() if 'timestamp' in recent_df.columns else '',
                'end': recent_df['timestamp'].iloc[-1].isoformat() if 'timestamp' in recent_df.columns else ''
            }
        }
        
        # Add recent price movements
        if 'close_price' in recent_df.columns:
            recent_prices = recent_df['close_price'].tail(7).tolist()
            context['recent_price_movements'] = [
                {
                    'date': row['timestamp'].isoformat() if 'timestamp' in row else '',
                    'price': float(row['close_price']) if 'close_price' in row else 0,
                    'change_pct': float(row['price_change_pct']) if 'price_change_pct' in row else 0
                }
                for _, row in recent_df.tail(7).iterrows()
            ]
        
        return context

# Global instance
data_integration_service = DataIntegrationService()