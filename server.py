from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import prompt_executor
import prompt_patcher

app = FastAPI()


@app.post("/prompt")
async def prompt(request: Request):
    data = await request.json()
    workflow = prompt_patcher.get_patched_json(data)
    result = prompt_executor.execute_workflow(workflow)
    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
