#!/usr/bin/env python3
"""
Run the FastAPI backend server.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "sds_digest.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

