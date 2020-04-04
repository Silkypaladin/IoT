import uuid
import sqlite3
import time
import datetime
import csv
import glob
import itertools
import paho.mqtt.client as mqtt
import tkinter

db_name = "employees.db"
broker = "localhost"

client = mqtt.Client()
window = tkinter.Tk()


def generate_uuid():
    return uuid.uuid1().hex


def delete_RFID(emp_id):
    try:
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE employees SET card_id=-1 WHERE emp_id={emp_id}")
        connection.commit()
    except sqlite3.Error as error:
        print("Failed to update sqlite table", error)
    finally:
        if (connection):
            connection.close()


def add_RFID(emp_id, card_id):
    try:
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        # Tuple (1,) if exists (0,) if not
        card_ex = cursor.execute(
            f"SELECT EXISTS (SELECT 1 from cards WHERE card_id={card_id});").fetchone()[0]
        card_reg = cursor.execute(
            f"SELECT EXISTS (SELECT 1 FROM employees WHERE card_id={card_id});").fetchone()[0]
        if card_ex and not card_reg:
            cursor.execute(
                f"UPDATE employees SET card_id={card_id} WHERE emp_id={emp_id}")
            connection.commit()
        elif card_ex and card_reg:
            print("Card already registered! Choose another one")
        else:
            print("No such card in the database!")
    except sqlite3.Error as error:
        print("Failed to update sqlite table", error)
    finally:
        if (connection):
            connection.close()


def get_employee(card_id):
    # If there is no employee under the card, it returns empty array
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM employees WHERE card_id = {card_id}")
    employee = cursor.fetchall()
    connection.close()
    return employee


def get_current_time():
    return time.localtime()


def verify_card(card_id):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    card_ex = cursor.execute(
        f"SELECT EXISTS (SELECT 1 from cards WHERE card_id={card_id});").fetchone()[0]
    connection.close()
    return card_ex


def format_time(wtime):
    """
    param wtime: time as struct_time instance
    """
    return time.strftime("%H:%M:%S", wtime)


def add_new_user(users):
    name = input('Podaj imię nowego użytkownika: ')
    surname = input('Podaj nazwisko nowego użytkownika: ')
    user_id = uuid.uuid1().hex
    users[user_id] = ['-1', name, surname]
    print(
        f'ID nowego uzytkownika to: {user_id}\nPomyślnie dodano użytkownika {name} {surname}')


def process_message(client, userdata, message):
    """TODO-Verify if the terminal is
     in the db and send proper message to it
     """
    emp_id = 0
    message = (str(message.payload.decode("utf-8"))).split(".")
    if message[0] != "Client connected" and message[0] != "Client disconnected":
        if (verify_card(message[0])):
            emp_id = get_employee(message[0])[0]
            connection = sqlite3.connect(db_name)
            cursor = connection.cursor()
            log_time = format_time(time.localtime())
            cursor.execute(f"INSERT INTO attendance VALUES(?, ?, ?, ?);",
                           (emp_id, message[1], log_time, datetime.date.today(),))
            cursor.commit()
            connection.close()
        else:
            print("That card is not attached to anyone! Attach it to activate.")
    else:
        print(message[0] + " : " + message[1])


def connect_to_broker():
    client.connect(broker)
    client.on_message = process_message
    client.loop_start()
    client.subscribe("worker/name")


def disconnect_from_broker():
    # Disconnet the client.
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    print(verify_card(9))
    print(get_employee(9))
