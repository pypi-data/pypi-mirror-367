# auth_api

Reusable FastAPI authentication component with JWT.

## Install

```bash
pip install git+https://github.com/yourusername/auth_api.git
```

## Use

```python
from fastapi import FastAPI
from auth_api import router as auth_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="", port=, reload=True)

```
