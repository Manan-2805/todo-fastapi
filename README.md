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
│   ├── conftest.py                  # Test fixtures & DB setup
│   ├── test_auth.py                 # Authentication tests
│   ├── test_todos_crud.py           # Todo CRUD operation tests
│   └── test_user_data_isolation.py  # User data isolation tests
├── docker-compose.yml   # Docker services
├── Dockerfile          # Container image
├── pytest.ini          # Pytest configuration
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

The project includes a comprehensive test suite with production-grade coverage:

**Test Coverage:**
- **Authentication Tests** (`test_auth.py`) - Register, login, logout behavior, and `/me` endpoint
- **CRUD Tests** (`test_todos_crud.py`) - Create, read, update, delete operations for todos
- **Data Isolation Tests** (`test_user_data_isolation.py`) - User-specific data access and cross-user protection

**Run all tests:**
```bash
pytest tests/
```

**Run specific test file:**
```bash
pytest tests/test_auth.py
```

**Run with verbose output:**
```bash
pytest tests/ -v
```

The test suite uses an isolated SQLite database with automatic setup and teardown for each test, ensuring clean and reproducible test runs.

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
