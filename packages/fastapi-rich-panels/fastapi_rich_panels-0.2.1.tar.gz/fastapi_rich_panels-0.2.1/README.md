# FastAPI Rich Logging

[![PyPI version](https://img.shields.io/pypi/v/fastapi-rich-panels.svg)](https://pypi.org/project/fastapi-rich-panels/)
[![GitHub release](https://img.shields.io/github/v/release/Danish903/fastapi-rich-panels.svg)](https://github.com/Danish903/fastapi-rich-panels/releases/latest)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-rich-panels.svg)](https://pypi.org/project/fastapi-rich-panels/)

Beautiful FastAPI request/response logging middleware with Rich panels and colors.

## ✨ Features

- 🎨 **Beautiful Rich panels** - Colorful, formatted request/response logs
- ⚡ **High performance** - Minimal overhead on your FastAPI application
- 🔧 **Highly configurable** - Control what gets logged and how
- 🛡️ **Security focused** - Automatically masks sensitive headers
- 📊 **Request timing** - Track response times for performance monitoring
- 🎯 **Easy integration** - One line to add to your FastAPI app

## 📦 Installation

```bash
pip install fastapi-rich-panels
```

## 🚀 Quick Start

```python
from fastapi import FastAPI
from fastapi_rich_panels import RichLoggingMiddleware

app = FastAPI()

# Add the Rich logging middleware
app.add_middleware(RichLoggingMiddleware)

@app.get("/")
async def hello():
    return {"message": "Hello World!"}
```

That's it! Your FastAPI app now has beautiful request/response logging.

## 🎨 What it looks like

When you make requests to your API, you'll see beautiful panels in your terminal:

```sh
┌─ 🚀 Incoming Request ──────────────────────────────────────┐
│ Method      GET                                            │
│ URL         http://localhost:8000/users/123?active=true    │
│ Path        /users/123                                     │
│ Client      127.0.0.1:54321                               │
│ Query       active=true                                    │
└────────────────────────────────────────────────────────────┘

┌─ ✅ Request Completed ─────────────────────────────────────┐
│ Status      200                                            │
│ Method      GET                                            │
│ Path        /users/123                                     │
│ Duration    0.0234s                                        │
│ Content-Type application/json                              │
└────────────────────────────────────────────────────────────┘
```

## ⚙️ Configuration

```python
from fastapi import FastAPI
from fastapi_rich_panels import RichLoggingMiddleware

app = FastAPI()

app.add_middleware(
    RichLoggingMiddleware,
    show_headers=True,      # Show request headers
    show_query_params=True, # Show query parameters
    logger=my_logger,       # Use custom logger
)
```

## 📝 Advanced Usage

### Simple Logging

For minimal, clean logs:

```python
from fastapi_rich_panels import SimpleRichLoggingMiddleware

app.add_middleware(SimpleRichLoggingMiddleware)
```

### Custom Console

Use your own Rich console:

```python
from rich.console import Console
from fastapi_rich_panels import RichLoggingMiddleware

console = Console(width=120, style="bold blue")

app.add_middleware(
    RichLoggingMiddleware,
    console=console
)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Designed for [FastAPI](https://github.com/tiangolo/fastapi) applications
- Inspired by the need for better development logging experience
