# QForum - Community Discussion Platform
## Project Link - qforum.vercel.app
### https://roadmap.sh/projects/blogging-platform-api
A modern web-based forum application built with **FastAPI** and **SQLAlchemy**, enabling users to create, discuss, and engage with forum posts and comments.

---
## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | FastAPI |
| **Web Server** | Uvicorn |
| **Database** | Postgres (via SQLAlchemy ORM) |
| **Authentication** | Session-based with Werkzeug password hashing |
| **Frontend Templates** | Jinja2 |
| **Frontend Styling** | CSS3 |
| **CORS** | FastAPI CORSMiddleware |
| **Environment Management** | python-dotenv |

---

## ✨ Features

### Core Functionality
- **User Authentication**: Secure user registration and login with password hashing
- **Post Management**: Create, read, and manage forum posts with titles, content, and topics
- **Comments System**: Add comments to posts for community discussions
- **Search Functionality**: Advanced search to find posts by keywords across topics, titles, and content
- **User Profiles**: View and manage individual user profiles
- **Pagination**: Browse posts with efficient pagination (4 posts per page)
- **Session Management**: Secure session-based authentication with CORS support

### User Experience
- **Responsive UI**: Clean HTML templates with custom CSS styling
- **Static Asset Management**: Organized static files for CSS, JavaScript, and images
- **RESTful API**: Well-structured API endpoints for all operations



## 🔌 API Routes

### Authentication Routes (`/`)
- `GET /login` - Display login page
- `POST /login` - Authenticate user
- `POST /logout` - End user session
- `GET /register` - Display registration page
- `POST /register` - Create new user account
- `GET /user/{username}` - View user profile

### Content Routes
- `GET /search` - Search posts by keyword
- `GET /create-post` - Display post creation form
- `POST /create-post` - Create new forum post
- `POST /posts/{post_id}/comments` - Add comment to post

### Post Display Routes (`/`)
- `GET /` - Display homepage with post feed
- `GET /posts/{post_id}` - Display single post with comments
- `POST /posts/{post_id}/comments` - Add or edit comments
- `DELETE /posts/{post_id}` - Delete post (owner only)
- `DELETE /comments/{comment_id}` - Delete comment (author only)

---


