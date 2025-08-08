"""
Data models for TSFM Client
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np


class TimeSeriesData(BaseModel):
    """Time series data structure"""
    values: np.ndarray = Field(..., description="Time series values as numpy array (1D for univariate, 2D for multivariate)")
    timestamps: Optional[List[str]] = Field(None, description="Optional timestamps")
    frequency: Optional[str] = Field(None, description="Frequency of the time series (e.g., '1H', '1D')")
    
    class Config:
        arbitrary_types_allow = True  # Allow numpy arrays in Pydantic
    
    @classmethod
    def from_pandas(cls, data: Union[pd.Series, pd.DataFrame], frequency: Optional[str] = None) -> "TimeSeriesData":
        """Create TimeSeriesData from pandas Series or DataFrame"""
        # Use numpy array directly (no conversion to list)
        values = data.values
        
        timestamps = None
        
        if hasattr(data.index, 'strftime'):
            timestamps = data.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
        elif not pd.api.types.is_numeric_dtype(data.index):
            timestamps = data.index.astype(str).tolist()
        
        return cls(
            values=values,
            timestamps=timestamps,
            frequency=frequency
        )
    
    @classmethod
    def from_numpy(cls, values: np.ndarray, timestamps: Optional[List[str]] = None, frequency: Optional[str] = None) -> "TimeSeriesData":
        """Create TimeSeriesData from numpy array (most efficient)"""
        return cls(
            values=values,
            timestamps=timestamps,
            frequency=frequency
        )
    
    @classmethod
    def from_list(cls, values: Union[List[float], List[List[float]]], timestamps: Optional[List[str]] = None, frequency: Optional[str] = None) -> "TimeSeriesData":
        """Create TimeSeriesData from list of values (univariate or multivariate)"""
        return cls(
            values=np.array(values),
            timestamps=timestamps,
            frequency=frequency
        )
    
    def to_pandas(self) -> Union[pd.Series, pd.DataFrame]:
        """Convert to pandas Series (univariate) or DataFrame (multivariate)"""
        if self.timestamps:
            index = pd.to_datetime(self.timestamps)
        else:
            index = range(len(self.values))
        
        # Check if multivariate (2D array)
        if self.values.ndim == 2:
            # Multivariate - return DataFrame
            return pd.DataFrame(self.values, index=index)
        else:
            # Univariate - return Series
            return pd.Series(self.values, index=index)
    
    def get_values(self) -> np.ndarray:
        """Get the underlying numpy array values"""
        return self.values


class PredictionRequest(BaseModel):
    """Prediction request structure"""
    data: TimeSeriesData = Field(..., description="Input time series data")
    forecast_horizon: int = Field(12, description="Number of steps to forecast", ge=1)
    confidence_intervals: Optional[List[float]] = Field(None, description="List of confidence levels (e.g., [0.8, 0.95] for 80% and 95%)")
    quantiles: Optional[List[float]] = Field(None, description="Quantiles to compute")
    num_samples: Optional[int] = Field(None, description="Number of samples to generate", ge=1)
    time_interval_seconds: Optional[int] = Field(None, description="Time interval between data points in seconds", ge=1)
    
    @classmethod
    def model_validate(cls, v):
        """Validate the prediction request"""
        if hasattr(v, 'quantiles') and v.quantiles:
            for q in v.quantiles:
                if not 0 <= q <= 1:
                    raise ValueError("Quantiles must be between 0 and 1")
        
        if hasattr(v, 'data') and len(v.data.values) == 0:
            raise ValueError("Input data cannot be empty")
        
        # Additional validation for confidence intervals
        if hasattr(v, 'confidence_intervals') and v.confidence_intervals:
            for ci in v.confidence_intervals:
                if ci <= 0 or ci >= 1:
                    raise ValueError(f"Confidence interval {ci} must be between 0 and 1 (exclusive)")
        
        # Additional validation for time interval
        if hasattr(v, 'time_interval_seconds') and v.time_interval_seconds and v.time_interval_seconds <= 0:
            raise ValueError("Time interval seconds must be positive")
        
        return v


class PredictionResponse(BaseModel):
    """Prediction response structure"""
    model_name: str = Field(..., description="Name of the model used")
    forecast: List[float] = Field(..., description="Forecasted values")
    confidence_intervals: Optional[Dict[str, Dict[str, List[float]]]] = Field(None, description="Confidence intervals")
    quantiles: Optional[Dict[str, List[float]]] = Field(None, description="Quantile forecasts")
    warnings: Optional[List[str]] = Field(None, description="Warnings about the prediction")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def to_pandas(self) -> pd.DataFrame:
        """Convert forecast to pandas DataFrame"""
        df = pd.DataFrame({
            'forecast': self.forecast
        })
        
        if self.confidence_intervals:
            for level, bounds in self.confidence_intervals.items():
                df[f'lower_{level}'] = bounds['lower']
                df[f'upper_{level}'] = bounds['upper']
        
        if self.quantiles:
            for quantile, values in self.quantiles.items():
                df[quantile] = values
        
        return df
    
    def get_forecast_array(self) -> np.ndarray:
        """Get forecast as numpy array"""
        return np.array(self.forecast)


class UserInfo(BaseModel):
    """User information structure"""
    user_id: str
    name: str
    scopes: List[str]
    daily_limit: int
    minute_limit: int
    model_access: List[str]


class ModelInfo(BaseModel):
    """Model information structure"""
    name: str
    is_loaded: bool
    has_compiled_model: bool
    max_forecast_horizon: Optional[int] = None
    device: Optional[str] = None
    default_confidence_level: Optional[float] = None


# Exception classes
class TSFMException(Exception):
    """Base exception for TSFM client"""
    pass


class AuthenticationError(TSFMException):
    """Authentication failed"""
    pass


class RateLimitError(TSFMException):
    """Rate limit exceeded"""
    pass


class ModelNotFoundError(TSFMException):
    """Model not found"""
    pass


class APIError(TSFMException):
    """General API error"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code