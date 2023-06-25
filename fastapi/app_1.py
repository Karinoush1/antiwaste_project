import uvicorn 
import pandas as pd
from pydantic import BaseModel
import mlflow
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO

## configurations
description = """
This is your app description, written in markdown code 
# This is a title 
* This is a bullet point 
"""

tags_metadata = [
    {
        "name": "Name_1",
        "description": "LOREM IPSUM NEC."
    }
]

# will contain the functionalities of the application
app = FastAPI(
    title="🪐 Antiwaste API",
    description=description,
    version="0.1",
    contact={
        "name": "Antiwaste app",
        "url": "http://app-antiwaste.herokuapp.com/",
    },
    openapi_tags=tags_metadata
)

@app.post("/predict")
async def predict(file: bytes = File(...)):
    # get image from bytes
    input_image = get_image_from_bytes(file)


    yoloF = "YOLO_best_frederic_25062023.pt"
    model = YOLO(f'model/{yoloF}')

    # model predict
    predictions = model.predict(input_image, save=True, imgsz=320, conf=0.3, show=True, save_conf=True, save_crop=False, boxes=True, project="results")
    predictions = transform_predict_to_df(predictions, model.model.names)


    #predict = detect_sample_model(input_image)

    # add bbox on image
    final_image = add_bboxs_on_img(image = input_image, predict = predict)

    # return image in bytes format
    return StreamingResponse(content=get_bytes_from_image(final_image), media_type="image/jpeg")


## define endpoints
# a specific url an API user will use to get a specific information from the API

# get + adress parameter ?name="..." with default value
@app.get("/custom-greetings")
async def custom_greetings(name:str="Mr (or Miss) Nobody"):
    greetings = {
        "Message" : f"Hello {name} user"
    }

    return greetings

# python instructions
"""
import requests
r = requests.get("http://localhost:4001/custom-greetings", params={"name":"gringo"})
r.content
"""

# get + path parameter
# the user specify the parameter blog_id
@app.get("/blog-articles/{blog_id}")
async def read_blog_article(blog_id: int):
    articles = pd.read_csv("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/articles.csv")
    if blog_id > len(articles):
        response = {
            "msg": "We don't have that many articles!"
        }
    else:
        article = articles.iloc[blog_id, :]
        response = {
            "title": article.title,
            "content": article.content, 
            "author": article.author
        }

    return response


# post + pydantic (BaseModel)
class BlogArticles(BaseModel):
    title: str
    content: str
    author: str = "Anonymous Author"
    avg_reading_time: int #Union[int, float] # Average reading time which can be a int or float
    category: Literal["Tech", "Environment", "Politics"] = "Tech" # Literal representing a category that can be only between "Tech", "Environment", "Politics". Default is "Tech"
    tags: List[str] = None # Accepts only a list of strings, and default is None (meaning nothing)

@app.post("/create-blog-article")
async def create_blog_article(blog_article: BlogArticles):
    df = pd.read_csv("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/articles.csv")
    new_article = pd.Series({
        'id': len(df)+1,
        'title': blog_article.title,
        'content': blog_article.content,
        'author': blog_article.author,
        'average_reading_time': blog_article.avg_reading_time,
        'category': blog_article.category, 
        'tags': blog_article.tags 
    })

    df = pd.concat([df, new_article])

    return df.to_json()

# simple post endpoint
@app.post("/another-post-endpoint")
async def another_post_endpoint(blog_article: BlogArticles):
    example_data = {
        'title': blog_article.title,
        'content': blog_article.content,
        'author': blog_article.author
    }
    return example_data


# get + tags to categorize the endpoint as Name_1
@app.get("/", tags=["Name_1"]) # here we categorized this endpoint as part of "Name_1" tag
async def index():
    message = "Hello world! This `/` is the most simple and default endpoint. If you want to learn more, check out documentation of the api at `/docs`"
    return message

# get + tags + documentation defined by """... """
@app.get("/", tags=["Introduction Endpoints"])
async def index():
    """
    Simply returns a welcome message!
    """
    message = "Hello world! This `/` is the most simple and default endpoint. If you want to learn more, check out documentation of the api at `/docs`"
    return message
if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4001)