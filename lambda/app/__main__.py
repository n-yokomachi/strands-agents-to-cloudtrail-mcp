from .main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8080, log_level="critical", server_header=False) 