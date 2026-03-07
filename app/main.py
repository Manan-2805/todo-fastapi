from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import engine, get_db, Base
from . import models, schemas, crud, auth

app = FastAPI(title="User-wise ToDo API")

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def frontend():
    return FileResponse("app/static/index.html")


@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/todos", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return crud.create_todo(db=db, todo=todo, user_id=current_user.id)


@app.get("/todos", response_model=list[schemas.Todo])
def read_todos(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return crud.get_todos(db=db, user_id=current_user.id)


@app.get("/todos/{todo_id}", response_model=schemas.Todo)
def read_todo(todo_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    todo = crud.get_todo(db=db, todo_id=todo_id, user_id=current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.put("/todos/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: int, todo: schemas.TodoCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    updated_todo = crud.update_todo(db=db, todo_id=todo_id, todo=todo, user_id=current_user.id)
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    deleted_todo = crud.delete_todo(db=db, todo_id=todo_id, user_id=current_user.id)
    if not deleted_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}


@app.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_user)):
    return current_user