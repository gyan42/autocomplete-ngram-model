from fastapi import Depends, FastAPI, HTTPException, status, Request
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from model import AutoCorrectModel
from starlette.responses import Response, JSONResponse


auto_correct_model = AutoCorrectModel()
auto_correct_model.load_from_json("data/trigram-autocompleter.json")


class Text(BaseModel):
    text: str


app = FastAPI(
    # root_path="/api/v1",
    title="AutoComplete API Service",
    description="""Visit http://0.0.0.0:8088/docs for the API interface.""",
    version="0.0.1"
)


ALLOWED_ORIGINS = ["*"]

app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# https://github.com/tiangolo/fastapi/issues/1663
def check_routes(request: Request):
    # Using FastAPI instance
    url_list = [
        route.path
        for route in request.app.routes
        if "rest_of_path" not in route.path
    ]

# Handle CORS preflight requests
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str) -> Response:
    response = check_routes(request)
    if response:
        return response

    response = Response(
        content="OK",
        media_type="text/plain",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )
    return response


# Add CORS headers
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = check_routes(request)
    if response:
        return response

    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


@app.get("/")
def read_root(request: Request):
    return {"message": "Hello, Welcome to AutoComleter API.", "root_path": request.scope.get("root_path")}


@app.post("/suggestions")
def suggestions(data: Text):
  
    start_with = None
    tokens = data.text.split(" ")


    # tokens = filter(lambda s: len(s) > 0, tokens)

    # Add start tokens if numner of tokens are less than trianed ngram 
    if len(tokens) < auto_correct_model._ngram:
        tokens = ['<s>'] * (auto_correct_model._ngram - len(tokens)) + tokens
    
    print("Inputs", tokens)

    # TODO this is bit of a overkill for our simple exploration ;)
    # start_with = tokens[-1].strip()
    # print("start_with", start_with)
    # start_with = start_with if len(start_with) > 0 else None

    
    res = auto_correct_model.suggestions(tokens, num_suggestions=10, start_with=start_with)

    print("Sugestions", res)
    return {"tokens": res}



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8088, reload=True)