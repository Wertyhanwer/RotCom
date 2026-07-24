import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "rotcom")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345")

dbname = DB_NAME
ip = DB_HOST
port = DB_PORT
user = DB_USER
password = DB_PASSWORD
