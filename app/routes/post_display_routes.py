from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import templates
from app.models import Comment, Post
from app.routes.auth_routes import get_logged_in_user

router = APIRouter()

PAGE_SIZE = 4


def get_post_feed(db: Session, offset: int):
    safe_offset = max(offset, 0)
    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .offset(safe_offset)
        .limit(PAGE_SIZE)
        .all()
    )
    total_posts = db.query(Post).count()
    remaining_posts = total_posts - safe_offset
    next_offset = safe_offset + PAGE_SIZE if remaining_posts > PAGE_SIZE else None
    return posts, next_offset


@router.get("/")
def home(request: Request, db: Session = Depends(get_db), offset: int = 0):
    user = get_logged_in_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    posts, next_offset = get_post_feed(db, offset)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"posts": posts, "user": user, "next_offset": next_offset},
    )


@router.get("/user-profile")
def user_profile(request: Request, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    comments = db.query(Comment).filter(Comment.author_id == user.username).all()
    user_posts = db.query(Post).filter(Post.author_id == user.username).order_by(Post.created_at.desc()).all()
    return templates.TemplateResponse(
        request,
        "user-profile.html",
        {"user": user, "user_posts": user_posts, "comments": comments},
    )


@router.get("/older-posts")
def older_posts(request: Request, db: Session = Depends(get_db), offset: int = 0):
    user = get_logged_in_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    posts, next_offset = get_post_feed(db, offset)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"posts": posts, "user": user, "next_offset": next_offset},
    )


@router.get("/post/{post_id}")
def view_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return templates.TemplateResponse(
        request,
        "comments.html",
        {
            "post": post,
            "user": user.username,
            "current_user": user,
            "comments": comments,
            "can_manage_post": post.author_id == user.username,
        },
    )
