"""Development server entrypoint for Lab 01."""

from __future__ import annotations

import os

import uvicorn

from src.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3001"))
    uvicorn.run(app, host="127.0.0.1", port=port)
