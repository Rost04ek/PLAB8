from task_manager.api import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("task_manager.api:app", host="127.0.0.1", port=8000, reload=True)
