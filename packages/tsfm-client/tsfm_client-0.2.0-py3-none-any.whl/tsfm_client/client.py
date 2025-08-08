"""
TSFM Client - Main client class for interacting with TSFM Inference Platform
"""

import httpx
import os
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin
import pandas as pd
import numpy as np

from .models import (
    TimeSeriesData,
    PredictionRequest,
    PredictionResponse,
    UserInfo,
    ModelInfo,
    TSFMException,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    APIError
)


class TSFMClient:
    """Client for TSFM Inference Platform"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.faim.it.com",
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """
        Initialize TSFM client
        
        Args:
            api_key: API key for authentication (or set TSFM_API_KEY environment variable)
            base_url: Base URL of the TSFM API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        # Get API key from parameter or environment variable
        if api_key is None:
            api_key = os.getenv("TSFM_API_KEY")
        
        if api_key is None:
            raise ValueError(
                "API key is required. Provide it as a parameter or set the TSFM_API_KEY environment variable."
            )
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Setup HTTP client
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=timeout
        )
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()
    
    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate exceptions"""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code == 403:
            raise AuthenticationError("Insufficient permissions")
        elif response.status_code == 404:
            raise ModelNotFoundError("Model not found")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        else:
            try:
                error_data = response.json()
                message = error_data.get("error", f"HTTP {response.status_code}")
            except:
                message = f"HTTP {response.status_code}"
            raise APIError(message, response.status_code)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make HTTP request with retry logic"""
        url = urljoin(self.base_url, endpoint)
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.request(method, url, **kwargs)
                return self._handle_response(response)
            except httpx.RequestError as e:
                if attempt == self.max_retries:
                    raise APIError(f"Request failed: {str(e)}")
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def predict(
        self,
        model_name: str = "chronos-t5-small",
        data: Union[TimeSeriesData, pd.Series, List[float], List[List[float]], np.ndarray] = None,
        forecast_horizon: int = 12,
        confidence_intervals: Optional[List[float]] = None,
        quantiles: Optional[List[float]] = None,
        num_samples: Optional[int] = None,
        time_interval_seconds: Optional[int] = None
    ) -> PredictionResponse:
        """
        Make time series prediction
        
        Args:
            model_name: Name of the model to use
            data: Time series data (TimeSeriesData, pandas Series, list of floats, list of lists for multivariate, or numpy array)
            forecast_horizon: Number of steps to forecast
            confidence_intervals: List of confidence levels (e.g., [0.8, 0.95] for 80% and 95% CIs, None for point estimate only)
            quantiles: Quantiles to compute
            num_samples: Number of samples to generate
            time_interval_seconds: Time interval between data points in seconds
            
        Returns:
            PredictionResponse with forecasts and metadata
        """
        if data is None:
            raise ValueError("Data is required for prediction")
        
        # Convert input data to TimeSeriesData
        if isinstance(data, pd.Series):
            ts_data = TimeSeriesData.from_pandas(data)
        elif isinstance(data, np.ndarray):
            # Handle numpy arrays - most efficient, no conversion needed
            if data.ndim == 1 or data.ndim == 2:
                ts_data = TimeSeriesData.from_numpy(data)
            else:
                raise ValueError("Numpy arrays must be 1D (univariate) or 2D (multivariate)")
        elif isinstance(data, list):
            # Convert lists to numpy arrays using from_list method
            ts_data = TimeSeriesData.from_list(data)
        elif isinstance(data, TimeSeriesData):
            ts_data = data
        else:
            raise ValueError("Data must be TimeSeriesData, pandas Series, list of floats, list of lists (multivariate), or numpy array")
        
        # Create request
        request = PredictionRequest(
            data=ts_data,
            forecast_horizon=forecast_horizon,
            confidence_intervals=confidence_intervals,
            quantiles=quantiles,
            num_samples=num_samples,
            time_interval_seconds=time_interval_seconds
        )
        
        # Make API call
        response_data = self._make_request(
            "POST",
            f"/api/v1/predict/{model_name}",
            json=request.model_dump()
        )
        
        return PredictionResponse(**response_data)
    
    def list_models(self) -> List[str]:
        """
        List available models
        
        Returns:
            List of model names
        """
        response_data = self._make_request("GET", "/api/v1/models")
        return response_data
    
    def get_model_info(self, model_name: str) -> ModelInfo:
        """
        Get information about a specific model
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelInfo with model details
        """
        response_data = self._make_request("GET", f"/api/v1/models/{model_name}/info")
        return ModelInfo(**response_data)
    
    def get_models_status(self) -> Dict[str, ModelInfo]:
        """
        Get status of all available models
        
        Returns:
            Dictionary mapping model names to ModelInfo
        """
        response_data = self._make_request("GET", "/api/v1/models/status")
        return {name: ModelInfo(**info) for name, info in response_data.items()}
    
    def load_model(self, model_name: str) -> Dict[str, str]:
        """
        Load a specific model
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            Status message
        """
        response_data = self._make_request("POST", f"/api/v1/models/{model_name}/load")
        return response_data
    
    def get_user_info(self) -> UserInfo:
        """
        Get current user information
        
        Returns:
            UserInfo with user details
        """
        response_data = self._make_request("GET", "/api/v1/me")
        return UserInfo(**response_data)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health
        
        Returns:
            Health status information
        """
        response_data = self._make_request("GET", "/health")
        return response_data


# Global client instance for convenience
_global_client = None

def predict(
    data: Union[TimeSeriesData, pd.Series, List[float], List[List[float]], np.ndarray],
    api_key: Optional[str] = None,
    model: str = "chronos-t5-small",
    forecast_horizon: int = 12,
    confidence_intervals: Optional[List[float]] = None,
    quantiles: Optional[List[float]] = None,
    num_samples: Optional[int] = None,
    time_interval_seconds: Optional[int] = None,
    base_url: str = "http://localhost:8000"
) -> PredictionResponse:
    """
    Convenience function for quick predictions
    
    Args:
        data: Time series data (univariate list, multivariate list of lists, pandas Series, or numpy array)
        api_key: API key for authentication (or set TSFM_API_KEY environment variable)
        model: Name of the model to use
        forecast_horizon: Number of steps to forecast
        confidence_intervals: List of confidence levels (e.g., [0.8, 0.95] for 80% and 95% CIs, None for point estimate only)
        quantiles: Quantiles to compute
        num_samples: Number of samples to generate
        time_interval_seconds: Time interval between data points in seconds
        base_url: Base URL of the TSFM API
        
    Returns:
        PredictionResponse with forecasts
    """
    global _global_client
    
    # Get API key from parameter or environment variable
    if api_key is None:
        api_key = os.getenv("TSFM_API_KEY")
    
    if api_key is None:
        raise ValueError(
            "API key is required. Provide it as a parameter or set the TSFM_API_KEY environment variable."
        )
    
    # Create or reuse client
    if _global_client is None:
        _global_client = TSFMClient(api_key=api_key, base_url=base_url)
    
    return _global_client.predict(
        model_name=model,
        data=data,
        forecast_horizon=forecast_horizon,
        confidence_intervals=confidence_intervals,
        quantiles=quantiles,
        num_samples=num_samples,
        time_interval_seconds=time_interval_seconds
    )


def clear_cache():
    """Clear the global client cache"""
    global _global_client
    if _global_client:
        _global_client.close()
        _global_client = None