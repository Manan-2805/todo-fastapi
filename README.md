# Todo App - FastAPI

A modern, full-stack todo application built with FastAPI and vanilla JavaScript. Features user authentication, user-specific task management, and a beautiful responsive UI.

## ✨ Features

- 🔐 **User Authentication** - Secure registration and login with JWT tokens
- 📝 **Task Management** - Create, read, update, and delete tasks
- ✅ **Task Completion** - Mark tasks as complete/incomplete
- 👤 **User-Specific Tasks** - Each user sees only their own tasks
- 🎨 **Modern UI** - Beautiful, responsive design with gradient themes
- 💾 **Persistent Storage** - PostgreSQL database for reliable data storage
- 🔄 **Real-time Updates** - Instant UI updates after actions

## 🛠️ Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - SQL toolkit and ORM
- PostgreSQL - Database
- Passlib + Bcrypt - Password hashing
- Python-JOSE - JWT token handling
- Uvicorn - ASGI server

**Frontend:**
- Vanilla JavaScript
- HTML5 & CSS3
- LocalStorage for token persistence

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (for PostgreSQL)
- pip (Python package manager)

## 🚀 Quick Start

### 1. Clone the repository

```bash
cd todo-fastapi
```

### 2. Create virtual environment

```bash
python -m venv env
```

### 3. Activate virtual environment

**Windows:**
```bash
.\env\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source env/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start PostgreSQL database

```bash
docker-compose up -d postgres
```

This will start PostgreSQL on port 5433.

### 6. Run the application

```bash
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5433/tododb"
uvicorn app.main:app --reload
```

### 7. Access the application

Open your browser and go to: **http://localhost:8000**

## 📁 Project Structure

```
todo-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & endpoints
│   ├── auth.py          # Authentication & JWT
│   ├── crud.py          # Database operations
│   ├── database.py      # Database configuration
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── static/
│       └── index.html   # Frontend UI
├── tests/
│   └── test_main.py     # Tests
├── docker-compose.yml   # Docker services
├── Dockerfile          # Container image
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | Login and get JWT token |
| GET | `/me` | Get current user info |

### Tasks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/todos` | Create new task | ✅ |
| GET | `/todos` | Get all user tasks | ✅ |
| GET | `/todos/{id}` | Get specific task | ✅ |
| PUT | `/todos/{id}` | Update task | ✅ |
| DELETE | `/todos/{id}` | Delete task | ✅ |

## 💡 Usage

1. **Register** - Create a new account with username and password
2. **Login** - Sign in to access your tasks
3. **Add Tasks** - Create new tasks with title and optional description
4. **Manage Tasks** - Mark tasks as complete or delete them
5. **Logout** - Securely log out when done

## 🐳 Docker Deployment

To run the entire application in Docker:

```bash
docker-compose up -d
```

This will start both PostgreSQL and the FastAPI application.

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@postgres:5432/tododb` |
| `SECRET_KEY` | JWT secret key | (change in production) |

## 📝 Database Schema

**Users Table:**
- `id` - Primary key
- `username` - Unique username
- `hashed_password` - Bcrypt hashed password

**Todos Table:**
- `id` - Primary key
- `title` - Task title
- `description` - Task description (optional)
- `completed` - Boolean status
- `owner_id` - Foreign key to users

## 🧪 Testing

```bash
pytest tests/
```

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- CSRF protection
- SQL injection prevention via SQLAlchemy ORM
- XSS protection with HTML escaping

## 📜 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📞 Support

For questions or issues, please create an issue in the repository.

---

**Made with ❤️ using FastAPI**
