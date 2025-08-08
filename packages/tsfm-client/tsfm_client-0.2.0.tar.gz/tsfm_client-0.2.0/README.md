# TSFM Python Client

A Python client library for the TSFM (Time Series Foundation Model) Inference Platform. Supports both univariate and multivariate time series forecasting with confidence intervals.

## Installation

```bash
pip install tsfm-client
```

## Quick Start

```python
import os
import numpy as np
from tsfm_client import TSFMClient

# Set your API key
os.environ['TSFM_API_KEY'] = 'your_api_key_here'

# Create client
client = TSFMClient(api_key=os.getenv('TSFM_API_KEY'))

# Make prediction with confidence intervals
data = np.array([10, 12, 13, 15, 17, 16, 18, 20, 22, 25])
response = client.predict(
    data=data,
    forecast_horizon=5,
    num_samples=100,
    confidence_intervals=[0.8, 0.95]
)

print(f"Forecast: {response.forecast}")
print(f"80% CI: {response.confidence_intervals['80%']}")
print(f"95% CI: {response.confidence_intervals['95%']}")

client.close()
```

## Supported Models

- **chronos-t5-small**: Fast univariate time series forecasting model
- **toto-open-base-1.0**: Advanced multivariate time series forecasting model with confidence intervals

## Supported Input Formats

The client accepts multiple data formats for maximum flexibility:

- **Numpy arrays**: `np.array([1, 2, 3])` (most efficient)
- **Python lists**: `[1, 2, 3]` or `[[1, 10], [2, 11]]` (multivariate)
- **Pandas Series**: `pd.Series([1, 2, 3])`
- **Pandas DataFrame**: For multivariate data

## Features

- ✅ **Native numpy support**: No conversions needed, maximum efficiency
- ✅ **Multiple confidence intervals**: Get 80%, 90%, 95% intervals in single request
- ✅ **Multivariate forecasting**: Predict with multiple related time series
- ✅ **Flexible sampling**: Control uncertainty estimation with num_samples
- ✅ **Error handling**: Comprehensive exception handling for API errors
- ✅ **Context manager**: Automatic resource cleanup

## Advanced Usage

### Multivariate Prediction
```python
# 2D numpy array: time steps × variables
multivariate_data = np.array([[20, 65], [21, 63], [22, 61], [19, 67]])
response = client.predict(
    model_name='toto-open-base-1.0',
    data=multivariate_data,
    forecast_horizon=10,
    confidence_intervals=[0.8, 0.9, 0.95],
    num_samples=100
)
```

### Context Manager
```python
with TSFMClient() as client:
    response = client.predict(data=np.array([1, 2, 3, 4, 5]))
    print(response.forecast)
```

### Error Handling
```python
from tsfm_client import TSFMClient, AuthenticationError, APIError

try:
    client = TSFMClient()
    response = client.predict(data=np.array([1, 2, 3]))
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error: {e}")
```

## Examples

For comprehensive examples including visualization and model comparison, see the [demo notebook](https://github.com/S-FM/tsfm-python-client/blob/main/examples/demo.ipynb).

## Requirements

- Python >= 3.10
- Valid TSFM API key
- Dependencies: numpy, pandas, httpx, pydantic

## API Reference

### TSFMClient.predict()

```python
predict(
    model_name: str = "chronos-t5-small",
    data: Union[np.ndarray, pd.Series, List[float], List[List[float]]],
    forecast_horizon: int = 12,
    confidence_intervals: Optional[List[float]] = None,
    num_samples: Optional[int] = None,
    time_interval_seconds: Optional[int] = None
) -> PredictionResponse
```

**Parameters:**
- `model_name`: Model to use ('chronos-t5-small' or 'toto-open-base-1.0')
- `data`: Time series data (1D for univariate, 2D for multivariate)
- `forecast_horizon`: Number of steps to predict
- `confidence_intervals`: List of confidence levels (e.g., [0.8, 0.95])
- `num_samples`: Number of samples for uncertainty estimation
- `time_interval_seconds`: Time between data points in seconds

**Returns:**
- `PredictionResponse` with forecast, confidence intervals, and metadata

## License

MIT License