from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import templates
from app.models import User

router = APIRouter()


def get_logged_in_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def require_user(request: Request, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_owner(user: User, owner_name: str):
    if user.username != owner_name:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/login")
def login_page(request: Request, db: Session = Depends(get_db), error: str | None = None):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"db": db, "error": error},
    )


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == username).first()
    if not user or not user.check_password(password):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid username or password"},
        )

    request.session["user_id"] = user.id
    request.session["username"] = user.username
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/signup")
def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if not username or not email or not password:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "All fields are required"},
        )

    if len(password) < 6:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Password must be at least 5 characters"},
        )

    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Username already exists"},
        )

    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Email already registered"},
        )

    try:
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        request.session["user_id"] = new_user.id
        request.session["username"] = new_user.username
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as exc:
        db.rollback()
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": f"Error creating account: {str(exc)}"},
        )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
