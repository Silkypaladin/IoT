#!/usr/bin/env python3

import sqlite3
import time
import os


def create_database():
    if os.path.exists("employees.db"):
        os.remove("employees.db")
        print("An old database removed.")
    connection = sqlite3.connect("employees.db")
    cursor = connection.cursor()
    cursor.execute(""" CREATE TABLE attendance (
        emp_id INTEGER PRIMARY KEY,
        terminal_id TEXT,
        log_time TEXT,
        date TEXT
    );""")
    cursor.execute(""" CREATE TABLE employees (
        emp_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        card_id INTEGER UNIQUE

);""")
    cursor.execute(""" CREATE TABLE cards (
    card_id INTEGER PRIMARY KEY
);""")
    cursor.execute(""" CREATE TABLE terminals (
    terminal_id STRING PRIMARY KEY
);""")
    cursor.execute(""" CREATE TABLE unknown_cards (
        card_id INTEGER PRIMARY KEY,
        terminal_id TEXT,
        date TEXT
);""")
    insert_data_into_database("employees.txt", "cards2.txt", cursor)
    connection.commit()
    connection.close()
    print("The new database created.")


def insert_data_into_database(emp_file, card_file, cursor):
    # kolejność danych w pliku pracownikow: emp_id, card_id, name, surname
    # kolejność danych w pliku kart: card_id, enter_time, leave_time, work_time
    cards_file = open(card_file, "r")
    for line in cards_file:
        fields = line.rstrip('\r\n').split(";")
        cursor.execute(f"INSERT INTO cards VALUES(?);", (fields[0],))
    emp_file = open(emp_file, "r")
    for line in emp_file:
        fields = line.rstrip('\r\n').split(";")
        cursor.execute(f"INSERT INTO employees VALUES(?, ?, ?, ?);",
                       (fields[0], fields[2], fields[3], fields[1]))


if __name__ == "__main__":
    create_database()
