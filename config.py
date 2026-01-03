import os

class Config:
    SECRET_KEY = "supersecretkey"
    SQLALCHEMY_DATABASE_URI = "postgresql://sachin:sachin123@localhost:5432/myblog"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
