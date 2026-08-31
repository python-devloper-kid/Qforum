from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import templates
from app.models import Comment, Post
from app.routes.auth_routes import get_logged_in_user, require_owner, require_user

router = APIRouter()


@router.get("/search")
def search(request: Request, search: str = "", db: Session = Depends(get_db)):
    keyword = (search or "").strip()
    if not keyword:
        return templates.TemplateResponse(request, "search-result.html", {"results": [], "query": keyword})

    keywords = keyword.split()
    columns = [Post.topic, Post.title, Post.body]
    conditions = []
    for word in keywords:
        pattern = f"%{word}%"
        conditions.append(or_(*[col.ilike(pattern) for col in columns]))

    results = db.query(Post).filter(or_(*conditions)).all()
    return templates.TemplateResponse(
        request,
        "search-result.html",
        {"results": results, "query": keyword},
    )


@router.get("/create-post")
def create_post_page(request: Request, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "create-post.html", {"user": user})


@router.post("/create-post")
def create_post(
    request: Request,
    title: str = Form(...),
    body: str = Form(""),
    topic: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_logged_in_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    if title:
        new_post = Post(title=title, body=body, topic=topic, author_id=user.username)
        db.add(new_post)
        db.commit()

    return RedirectResponse(url="/", status_code=303)


@router.get("/post/{post_id}/edit")
def edit_post_page(request: Request, post_id: int, db: Session = Depends(get_db)):
    user = require_user(request, db)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    require_owner(user, post.author_id)
    return templates.TemplateResponse(
        request,
        "create-post.html",
        {"user": user, "post": post, "editing": True},
    )


@router.post("/post/{post_id}/edit")
def edit_post(
    request: Request,
    post_id: int,
    title: str = Form(...),
    body: str = Form(""),
    topic: str = Form(""),
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    require_owner(user, post.author_id)

    if title:
        post.title = title
        post.body = body
        post.topic = topic
        db.commit()

    return RedirectResponse(url=f"/post/{post_id}", status_code=303)


@router.post("/post/{post_id}/delete")
def delete_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    user = require_user(request, db)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    require_owner(user, post.author_id)

    db.delete(post)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/post/{post_id}/create")
def create_comment(
    request: Request,
    post_id: int,
    comment: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_logged_in_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if comment:
        new_comment = Comment(body=comment, post_id=post_id, author_id=user.username)
        db.add(new_comment)
        db.commit()

    return RedirectResponse(url=f"/post/{post_id}", status_code=303)


@router.get("/post/{post_id}/comment/{comment_id}/edit")
def edit_comment_page(request: Request, post_id: int, comment_id: int, db: Session = Depends(get_db)):
    user = require_user(request, db)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    require_owner(user, comment.author_id)

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
            "editing_comment_id": comment.id,
            "editing_comment_body": comment.body,
        },
    )


@router.post("/post/{post_id}/comment/{comment_id}/edit")
def edit_comment(
    request: Request,
    post_id: int,
    comment_id: int,
    comment: str = Form(...),
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment_record = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not comment_record:
        raise HTTPException(status_code=404, detail="Comment not found")
    require_owner(user, comment_record.author_id)

    if comment:
        comment_record.body = comment
        db.commit()

    return RedirectResponse(url=f"/post/{post_id}", status_code=303)


@router.post("/post/{post_id}/comment/{comment_id}/delete")
def delete_comment(request: Request, post_id: int, comment_id: int, db: Session = Depends(get_db)):
    user = require_user(request, db)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    require_owner(user, comment.author_id)

    db.delete(comment)
    db.commit()
    return RedirectResponse(url=f"/post/{post_id}", status_code=303)
