import os
import sqlite3
from config import Config

print Config.SQLALCHEMY_DATABASE_URI
connection = sqlite3.connect('sqlite3.db', check_same_thread=False)

connection.row_factory = sqlite3.Row

def sql_query(query):
    cur = connection.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows

def sql_edit_insert(query, var):
    cur = connection.cursor()
    cur.execute(query, var)
    connection.commit()

def sql_delete(query, var):
    cur = connection.cursor()
    cur.execute(query, var)

def sql_query2(query, var):
    cur = connection.cursor()
    cur.execute(query, var)
    rows = cur.fetchall()
    return rows
