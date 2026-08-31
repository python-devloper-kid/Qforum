import os                                                    #file commented for better understanding
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
load_dotenv()                                                     #load secret credentials
from app.database import get_db, init_db
from app.models import Comment, Post, User
BASE_DIR = Path(__file__).resolve().parent                       ### provide folder path directories to FASTAPI
app = FastAPI(title="QForum API")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))    

origins = ["http://localhost:3000", "http://127.0.0.1:3000"]    
app.add_middleware(                                              # CORS middleware allows access to the backend to a frontend serving on origins
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "yabadabadoo"))


@app.on_event("startup")              # older alternative to lifespan method for db initialization
def startup_event():
    init_db()


from app.routes.auth_routes import router as auth_router
from app.routes.content_routes import router as content_router
from app.routes.post_display_routes import router as post_display_router

app.include_router(auth_router)
app.include_router(post_display_router)
app.include_router(content_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)