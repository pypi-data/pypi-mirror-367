# logutil

A simple logging library that can replace builtin logging and other structural logging libaries. logutil writes logs to:
- Console
- Local file
- Datadog

## Basic Usage

```python
from logutil import log

log.info("hello", a=1, b="foo")
```

By default, logs appear in:
- Your console
- Append to `/tmp/app.log`

## Configuration

You can customize logutil by calling `init_logger`:

```python
from logutil import init_logger

init_logger(
    # Turn console logging on/off
    console=True,  
    
    # Change file logging settings
    file={
        "enabled": True,
        "path": "/tmp/app.log"
    },
    
    # Enable Datadog logging
    datadog={
        "api_key": "your_api_key",
        "site": "US3",
        "service": "your_service_name",
        "tags": {"env": "dev"}
    }
)
```

## Datadog Configuration

To use Datadog logging, you must provide:
1. Your Datadog API key
2. The Datadog site you use

Valid Datadog sites:
- US1
- US3
- US5
- EU1
- US1-FED

You can find your site in the URL when you log in to the Datadog web portal.
