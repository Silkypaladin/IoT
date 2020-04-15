import uuid
import sqlite3
import time
import datetime
import paho.mqtt.client as mqtt
import tkinter
import csv

db_name = "employees.db"
broker = "localhost"

client = mqtt.Client()
window = tkinter.Tk()


def delete_RFID(emp_id):
    try:
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE employees SET card_id=NULL WHERE emp_id={emp_id}")
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
            print("RFID card added.")
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
    cursor.execute(f"INSERT INTO unknown_cards (card_id, terminal_id, date) VALUES(?, ?, ?)", (card_id, terminal_id, format_time(time.localtime()),))
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


def get_user_input():
    while True:
        try:
            choice = int(input('>'))
            break
        except ValueError:
            print('Wrong format! Try again.')
    return choice


def process_message(client, userdata, message):
    message = (str(message.payload.decode("utf-8"))).split(".")
    # print(message)
    if not verify_terminal(message[1]):
        client.publish("terminal/info", "Not registered.")
        print(f"Do you want to register new terminal with id: {message[1]}")
        if get_user_input() == 1:
            add_terminal(message[1])
            client.publish("terminal/info", "Registered.")
            print("Registered new terminal.")
        else:
            client.publish("terminal/info", "Refused.")
    else:
        if message[0] != "Client connected" and message[0] != "Client disconnected" and message[0] != "Client reconnected":
            if verify_card(message[0]) == 1:
                # emp to pracownik, na i=0 jest jego id
                emp = get_employee(message[0])
                if emp != []:
                    emp = emp[0]
                    connection = sqlite3.connect(db_name)
                    cursor = connection.cursor()
                    log_time = format_time(time.localtime())
                    cursor.execute(f"INSERT INTO attendance (emp_id, terminal_id, log_time, date) VALUES(?, ?, ?, ?);",
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
    if user_logs == []:
        print("No logs for that user!")
        return
    cursor.execute(f"SELECT * FROM employees WHERE emp_id={emp_id}")
    user = cursor.fetchone()
    connection.close()
    # Date of log, based on that we write data to file
    date = user_logs[0][4]
    filename = f"report_{user[1]}_{user[2]}_{user[0]}.csv"
    with open(filename, 'w+') as report:
        writer = csv.writer(report)
        writer.writerow(["Raport", "czasu", "pracy", f"{user[1]}", f"{user[2]}"])
        writer.writerow(["Data", "Godzina odbicia karty", "Terminal"])
        for log in user_logs:
            if log[4] == date:
                writer.writerow([log[4], log[3], log[2]])
            else:
                date = log[4]
                writer.writerow([])
                writer.writerow([log[4], log[3], log[2]])


def add_terminal(terminal_id):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO terminals VALUES(?);", (terminal_id,))
    connection.commit()
    connection.close()


def remove_terminal(terminal_id):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM terminals WHERE terminal_id=?;", (terminal_id,))
    connection.commit()
    connection.close()
    print(f"Deleted terminal: id {terminal_id}.")


def connect_to_broker():
    client.connect(broker)
    client.on_message = process_message
    client.loop_start()
    client.subscribe("employee/name")


def disconnect_from_broker():
    # Disconnect the client.
    client.loop_stop()
    client.disconnect()


def generate_main_window():
    window.geometry("300x200")
    window.title("Server")
    add_rfid = tkinter.Button(window, text="Add RFID",command=lambda: add_RFID_window())
    del_rfid = tkinter.Button(window, text="Delete RFID", command=lambda: delete_RFID_window())
    del_term = tkinter.Button(window, text="Delete terminal", command=lambda: del_terminal_window())
    logs = tkinter.Button(window, text="Generate logs", command=lambda: generate_logs_window())
    exit = tkinter.Button(window, text="Exit", command=window.quit)
    add_rfid.pack()
    del_rfid.pack()
    del_term.pack()
    logs.pack()
    exit.pack()


def add_RFID_window():
    def click():
        e_id = emp.get()
        c_id = card.get()
        add_RFID(e_id, c_id)
    add_window = tkinter.Tk()
    add_window.title("Add RFID")
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    employees = cursor.execute("SELECT * FROM employees;").fetchall()
    cards = cursor.execute("SELECT * FROM cards;").fetchall()
    connection.close()
    emp_labels = []
    card_labels = []
    emp_info = tkinter.Label(add_window, text="Employees")
    emp_info.grid(row=0, column=0)
    card_info = tkinter.Label(add_window, text="Cards")
    card_info.grid(row=0, column=1)
    for i in range(0, len(employees)):
        emp = employees[i]
        emp_labels.append(tkinter.Label(add_window, text=f"{emp[0]}-{emp[1]} {emp[2]}: {emp[3]}"))
        emp_labels[i].grid(row=(i+1), column=0)
    for i in range(0,len(cards)):
        card = cards[i]
        card_labels.append(tkinter.Label(add_window, text=f"Card id: {card[0]}"))
        card_labels[i].grid(row=(i+1), column=1)
    l1 = tkinter.Label(add_window, text="Employee id")
    l2 = tkinter.Label(add_window, text="Card id")
    emp = tkinter.Entry(add_window)
    card = tkinter.Entry(add_window)
    l1.grid(columnspan=2)
    emp.grid(columnspan=2)
    l2.grid(columnspan=2)
    card.grid(columnspan=2)
    add = tkinter.Button(add_window, text="Add card", command=lambda: click())
    exit = tkinter.Button(add_window, text="Close", command=add_window.destroy)
    add.grid(columnspan=2)
    exit.grid(columnspan=2)
    add_window.mainloop()


def delete_RFID_window():
    cards_window = tkinter.Tk()
    cards_window.title("Delete RFID")
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    employees = cursor.execute("SELECT * FROM employees;").fetchall()
    connection.close()
    buttons = []
    for i in range(0, len(employees)):
        e = employees[i]
        buttons.append(tkinter.Button(cards_window, text=f"{e[1]} {e[2]}: {e[3]}",
                                      command=lambda i=i: delete_RFID(employees[i][0])))
        buttons[i].pack()
    exit = tkinter.Button(cards_window, text="Close", command=cards_window.destroy)
    exit.pack()
    cards_window.mainloop()


def generate_logs_window():
    log_window = tkinter.Tk()
    log_window.title("Logs")
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    employees = cursor.execute("SELECT * FROM employees;").fetchall()
    connection.close()
    buttons = []
    for i in range(0, len(employees)):
        e = employees[i]
        buttons.append(tkinter.Button(log_window, text=f"{e[1]} {e[2]}: {e[3]}",
                                      command=lambda i=i: generate_logs(employees[i][0])))
        buttons[i].pack()
    exit = tkinter.Button(log_window, text="Close", command=log_window.destroy)
    exit.pack()
    log_window.mainloop()


def del_terminal_window():
    term_window = tkinter.Tk()
    term_window.title("Delete terminal")
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    terminals = cursor.execute("SELECT * FROM terminals;").fetchall()
    connection.close()
    buttons = []
    for i in range(0, len(terminals)):
        t = terminals[i]
        buttons.append(tkinter.Button(term_window, text=f"Terminal id: {t[0]}",
                       command=lambda i=i: remove_terminal(terminals[i][0])))
        buttons[i].pack()
    exit = tkinter.Button(term_window, text="Close", command=term_window.destroy)
    exit.pack()
    term_window.mainloop()



if __name__ == "__main__":
    connect_to_broker()
    generate_main_window()
    window.mainloop()
    disconnect_from_broker()
