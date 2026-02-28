import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username:str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if user:
            print(user)
        else:
            print(f"User {username} not found")

@cli.command()
def get_all_users():
    with get_session() as db:
        users = db.exec(select(User)).all()
        for user in users:
            print(user)


@cli.command()
def change_email(username: str, new_email:str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if user:
            user.email = new_email
            db.commit()
            print(f"Email updated for {username}")
        else:
            print(f"User {username} not found")

@cli.command()
def create_user(username: str, email:str, password: str):
    try:
        with get_session() as db:
            new_user = User(username=username, email=email, password=password)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"User {username} created")
    except IntegrityError:
        print(f"User {username} or email {email} already exists")

@cli.command()
def delete_user(username: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if user:
            db.delete(user)
            db.commit()
            print(f"User {username} deleted")
        else:
            print(f"User {username} not found")


if __name__ == "__main__":
    cli()