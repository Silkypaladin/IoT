import uuid
import sqlite3
import time
import datetime
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


def save_unregistered_card(card_id, terminal_id):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO unknown_cards VALUES(?, ?, ?)", (card_id, terminal_id, format_time(time.localtime()),))
    connection.commit()
    connection.close()


def verify_terminal(terminal_id):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    terminal_registered = cursor.execute(f"SELECT EXISTS (SELECT 1 FROM terminals WHERE terminal_id=?);", (terminal_id,)).fetchone()[0]
    connection.close()
    return terminal_registered


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
    """TODO-Add terminal gui function, verify if the card is attached"""
    message = (str(message.payload.decode("utf-8"))).split(".")
    print(message)
    if not verify_terminal(message[1]):
        client.publish("terminal/info", "Not registered.")
    else:
        if message[0] != "Client connected" and message[0] != "Client disconnected":
            if verify_card(message[0]) == 1:
                # emp to pracownik, na i=0 jest jego id
                emp = get_employee(message[0])
                if emp != []:
                    emp = get_employee(message[0])[0]
                    connection = sqlite3.connect(db_name)
                    cursor = connection.cursor()
                    log_time = format_time(time.localtime())
                    cursor.execute(f"INSERT INTO attendance VALUES(?, ?, ?, ?);",
                               (emp[0], message[1], log_time, datetime.date.today(),))
                    print("added log")
                    connection.commit()
                    connection.close()
                else:
                    print("Card not attached to anyone! Please attach it before usage.")
            else:
                print("Card not registered!")
                save_unregistered_card(message[0], message[1])
        else:
            print(message[0] + " : " + message[1])


# finish
def generate_logs(emp_id):
    connection = sqlite3.Connection(db_name)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM attendance WHERE emp_id={emp_id}")
    # user_logs is a list of touples (id,terminal,time,date)
    user_logs = cursor.fetchall()
    connection.close()
    time_date = []
    worktime = 0
    for log in user_logs:
        time_date.append((log[2], log[3]))
    for i in range (0, len(time_date)):
        #jezeli data sie zgadza to skaczemy o dwa i dodajemy
        pass


def add_terminal(terminal_id):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO terminals VALUES(?);", (terminal_id,))
    connection.commit()
    connection.close()
    print("Dodano nowy terminal.")


def remove_terminal(terminal_id):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM terminals WHERE terminal_id=?;", (terminal_id,))
    connection.commit()
    connection.close()
    print(f"Usunięto terminal o id {terminal_id}.")


def connect_to_broker():
    client.connect(broker)
    client.on_message = process_message
    client.loop_start()
    client.subscribe("employee/name")


def disconnect_from_broker():
    # Disconnect the client.
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    connect_to_broker()
    window.mainloop()
    disconnect_from_broker()
