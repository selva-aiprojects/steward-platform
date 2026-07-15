"""
Lightweight LSTM Price Movement Predictor for portfolio candidate scoring.

Architecture:
- 2-layer LSTM with 64-128 hidden units
- Input: 60-day OHLCV window
- Output: Predicted next-5-day return direction & confidence
- Runs on CPU in <100ms per symbol (no GPU required)

This model is used as one component of the AI ensemble (30% weight)
to predict short-to-medium term price movements for portfolio allocation.
"""
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Check for PyTorch
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logger.warning("PyTorch not installed. LSTM predictor will run in fallback statistical mode.")


# ----------- PyTorch Model Definition (if available) -----------

if HAS_TORCH:
    class _PriceLSTM(nn.Module):
        """2-layer LSTM for price movement prediction."""
        def __init__(self, input_size: int = 5, hidden_size: int = 64, num_layers: int = 2, dropout: float = 0.2):
            super().__init__()
            self.lstm = nn.LSTM(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0
            )
            self.fc = nn.Sequential(
                nn.Linear(hidden_size, 32),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(32, 1)  # Single output: predicted return
            )

        def forward(self, x):
            # x shape: (batch, seq_len, input_size)
            lstm_out, (hidden, _) = self.lstm(x)
            # Use last hidden state
            last_hidden = hidden[-1]  # (batch, hidden_size)
            return self.fc(last_hidden)  # (batch, 1)
else:
    # Placeholder when PyTorch is not available
    class _PriceLSTM:
        """Placeholder — PyTorch not installed."""
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required for _PriceLSTM")
        def forward(self, x):
            raise ImportError("PyTorch is required for _PriceLSTM")


# ----------- LSTM Predictor Engine -----------

class LSTMPredictor:
    """
    LSTM-based price movement predictor.

    Handles both PyTorch mode and statistical fallback mode.
    Provides direction prediction + confidence for portfolio scoring.
    """

    def __init__(self, sequence_length: int = 60, forecast_days: int = 5, hidden_size: int = 64):
        self.sequence_length = sequence_length
        self.forecast_days = forecast_days
        self.hidden_size = hidden_size
        self.model = None
        self.is_trained = False
        self.input_size = 5  # OHLCV

        if HAS_TORCH:
            self.model = _PriceLSTM(input_size=self.input_size, hidden_size=hidden_size)
            logger.info(f"LSTM predictor initialized (seq_len={sequence_length}, forecast={forecast_days}d)")
        else:
            logger.info("LSTM predictor running in statistical fallback mode (no PyTorch)")

    # ----------- Feature Engineering -----------

    def _prepare_features(self, ohlcv_data: List[Dict[str, Any]]) -> Optional[np.ndarray]:
        """
        Convert raw OHLCV data into normalized feature matrix.
        Expected keys: open, high, low, close, volume (or timestamp, open, high, low, close, volume)
        """
        if not ohlcv_data or len(ohlcv_data) < self.sequence_length + 5:
            return None

        # Extract OHLCV
        try:
            closes = np.array([d.get("close", d.get(4, 0)) for d in ohlcv_data], dtype=np.float64)
            highs = np.array([d.get("high", d.get(2, 0)) for d in ohlcv_data], dtype=np.float64)
            lows = np.array([d.get("low", d.get(3, 0)) for d in ohlcv_data], dtype=np.float64)
            opens = np.array([d.get("open", d.get(1, 0)) for d in ohlcv_data], dtype=np.float64)
            volumes = np.array([d.get("volume", d.get(5, 0)) for d in ohlcv_data], dtype=np.float64)
        except (IndexError, KeyError, TypeError) as e:
            logger.error(f"Failed to parse OHLCV data: {e}")
            return None

        # Guard against zero/constant prices
        if np.std(closes) < 0.01:
            return None

        # Compute returns-based features (stationary)
        close_returns = np.diff(closes) / closes[:-1]
        high_low_pct = (highs - lows) / closes
        open_close_pct = (opens - closes) / closes
        volume_change = np.diff(volumes) / (volumes[:-1] + 1e-10)

        # Normalize: z-score
        def _normalize(arr):
            std = np.std(arr)
            if std < 1e-10:
                return np.zeros_like(arr)
            return (arr - np.mean(arr)) / std

        # Build feature matrix (need same length = len(close_returns))
        min_len = min(len(close_returns), len(high_low_pct[1:]), len(open_close_pct[1:]), len(volume_change))
        if min_len < self.sequence_length:
            return None

        features = np.column_stack([
            _normalize(close_returns[-min_len:]),
            _normalize(high_low_pct[-min_len:]),
            _normalize(open_close_pct[-min_len:]),
            _normalize(volume_change[-min_len:]),
            _normalize(closes[-min_len:] / closes[-min_len-1] - 1 if min_len < len(closes) else close_returns[-min_len:])
        ])

        return features

    def _compute_actual_future_return(self, ohlcv_data: List[Dict]) -> Optional[float]:
        """Compute actual return over forecast_days from the end of the data."""
        if len(ohlcv_data) < self.forecast_days + 1:
            return None
        closes = np.array([d.get("close", d.get(4, 0)) for d in ohlcv_data], dtype=np.float64)
        start_price = closes[-(self.forecast_days + 1)]
        end_price = closes[-1]
        if start_price <= 0:
            return None
        return (end_price - start_price) / start_price

    # ----------- Training -----------

    def train(self, historical_data_map: Dict[str, List[Dict[str, Any]]],
              epochs: int = 50, lr: float = 0.001) -> Dict[str, Any]:
        """
        Train the LSTM on historical OHLCV data for multiple symbols.

        Args:
            historical_data_map: {symbol: [OHLCV_dict, ...]} — each list must be long enough
            epochs: Number of training epochs
            lr: Learning rate

        Returns:
            Training summary dict
        """
        if not HAS_TORCH:
            logger.warning("PyTorch not available. Cannot train LSTM. Using fallback mode.")
            return {"trained": False, "reason": "PyTorch not available", "epochs": 0}

        if self.model is None:
            self.model = _PriceLSTM(input_size=self.input_size, hidden_size=self.hidden_size)

        # Prepare training data
        X_list, y_list = [], []
        for symbol, data in historical_data_map.items():
            features = self._prepare_features(data)
            if features is None or len(features) < self.sequence_length + 1:
                continue

            # Create sliding windows
            for i in range(len(features) - self.sequence_length):
                window = features[i:i + self.sequence_length]
                # Target: actual return over next forecast_days
                future_return = 0
                end_idx = i + self.sequence_length + self.forecast_days
                if end_idx < len(features):
                    future_return = np.mean(features[end_idx - 1, 0])  # use close return as target
                else:
                    continue

                X_list.append(window)
                y_list.append(future_return)

        if len(X_list) < 10:
            logger.warning(f"Insufficient training samples ({len(X_list)}). Skipping training.")
            return {"trained": False, "reason": "Insufficient samples", "samples": len(X_list)}

        X = torch.tensor(np.array(X_list), dtype=torch.float32)
        y = torch.tensor(np.array(y_list), dtype=torch.float32).unsqueeze(1)

        # Train
        self.model.train()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.MSELoss()

        dataset_size = len(X)
        batch_size = min(64, dataset_size)

        for epoch in range(epochs):
            # Shuffle
            perm = torch.randperm(dataset_size)
            X_shuffled, y_shuffled = X[perm], y[perm]

            epoch_loss = 0.0
            for i in range(0, dataset_size, batch_size):
                batch_X = X_shuffled[i:i + batch_size]
                batch_y = y_shuffled[i:i + batch_size]

                optimizer.zero_grad()
                predictions = self.model(batch_X)
                loss = criterion(predictions, batch_y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()

                epoch_loss += loss.item()

            if (epoch + 1) % 10 == 0:
                logger.info(f"LSTM Epoch {epoch + 1}/{epochs} — Loss: {epoch_loss / (dataset_size / batch_size):.6f}")

        self.is_trained = True
        logger.info(f"LSTM training complete. Samples: {dataset_size}, Epochs: {epochs}")
        return {"trained": True, "samples": dataset_size, "epochs": epochs}

    # ----------- Inference / Prediction -----------

    def predict(self, ohlcv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict next-forecast_days price movement for a single symbol.

        Args:
            ohlcv_data: List of OHLCV dicts for the symbol (ordered by date ascending).
                        Must be at least sequence_length + 5 entries long.

        Returns:
            Dict with predicted_return, direction, confidence, volatility_forecast
        """
        # Default fallback result
        fallback = {
            "predicted_return": 0.0,
            "direction": "NEUTRAL",
            "confidence": 0.5,
            "volatility_forecast": 0.0,
            "model": "fallback_statistical"
        }

        # Statistical fallback: use momentum and volatility
        if not HAS_TORCH or self.model is None:
            return self._statistical_predict(ohlcv_data)

        features = self._prepare_features(ohlcv_data)
        if features is None or len(features) < self.sequence_length:
            return self._statistical_predict(ohlcv_data)

        # Get the last sequence
        last_sequence = features[-self.sequence_length:]
        input_tensor = torch.tensor(last_sequence, dtype=torch.float32).unsqueeze(0)  # (1, seq_len, features)

        # Predict
        self.model.eval()
        with torch.no_grad():
            predicted_return = self.model(input_tensor).item()

        # Compute confidence based on prediction magnitude and model certainty
        abs_return = abs(predicted_return)
        confidence = min(0.95, 0.5 + abs_return * 5)  # Higher prediction = higher confidence

        # Volatility forecast from recent data
        volatility = self._compute_volatility(ohlcv_data)

        direction = "UP" if predicted_return > 0.01 else ("DOWN" if predicted_return < -0.01 else "NEUTRAL")

        return {
            "predicted_return": round(predicted_return, 4),
            "direction": direction,
            "confidence": round(confidence, 4),
            "volatility_forecast": round(volatility, 4),
            "model": "lstm_pytorch" if self.is_trained else "lstm_untrained"
        }

    # ----------- Statistical Fallback -----------

    def _statistical_predict(self, ohlcv_data: List[Dict]) -> Dict[str, Any]:
        """Fallback prediction using classical technical statistics."""
        if not ohlcv_data or len(ohlcv_data) < 20:
            return {
                "predicted_return": 0.0,
                "direction": "NEUTRAL",
                "confidence": 0.3,
                "volatility_forecast": 0.0,
                "model": "fallback_statistical"
            }

        closes = np.array([d.get("close", d.get(4, 0)) for d in ohlcv_data], dtype=np.float64)

        if len(closes) < 2 or np.std(closes) < 0.01:
            return {
                "predicted_return": 0.0,
                "direction": "NEUTRAL",
                "confidence": 0.3,
                "volatility_forecast": 0.0,
                "model": "fallback_statistical"
            }

        # Momentum: recent 5-day vs 20-day average
        short_window = min(5, len(closes) - 1)
        long_window = min(20, len(closes) - 1)
        short_ma = np.mean(closes[-short_window:])
        long_ma = np.mean(closes[-long_window:])

        # Price momentum
        short_return = (closes[-1] - closes[-short_window]) / closes[-short_window]
        momentum_score = (short_ma - long_ma) / long_ma

        # Predicted return = blend of momentum + short-term trend
        predicted_return = (short_return * 0.6 + momentum_score * 0.4)

        # Confidence based on trend strength
        trend_strength = abs(momentum_score) / (np.std(closes[-long_window:]) / np.mean(closes[-long_window:]) + 1e-10)
        confidence = min(0.7, 0.3 + trend_strength * 2)

        volatility = self._compute_volatility(ohlcv_data)
        direction = "UP" if predicted_return > 0.01 else ("DOWN" if predicted_return < -0.01 else "NEUTRAL")

        return {
            "predicted_return": round(predicted_return, 4),
            "direction": direction,
            "confidence": round(confidence, 4),
            "volatility_forecast": round(volatility, 4),
            "model": "fallback_statistical"
        }

    # ----------- Helpers -----------

    def _compute_volatility(self, ohlcv_data: List[Dict]) -> float:
        """Compute annualized volatility from daily returns."""
        if not ohlcv_data or len(ohlcv_data) < 10:
            return 0.0
        closes = np.array([d.get("close", d.get(4, 0)) for d in ohlcv_data], dtype=np.float64)
        returns = np.diff(closes) / closes[:-1]
        if len(returns) < 2 or np.std(returns) < 1e-10:
            return 0.0
        daily_vol = np.std(returns)
        return daily_vol * np.sqrt(252)  # Annualized

    def predict_batch(self, ohlcv_map: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """Run predictions for multiple symbols in batch."""
        results = {}
        for symbol, data in ohlcv_map.items():
            results[symbol] = self.predict(data)
        return results


# Singleton instance for global use
lstm_predictor = LSTMPredictor()
