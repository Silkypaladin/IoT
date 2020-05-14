import paho.mqtt.client as mqtt
import tkinter
import sqlite3
import time

# Instancja klienta, potrzebne id, funkcja pozwalajaca odbic karte,
# Terminal id, any string
terminal_id = "T2"

# broker name or ip
broker = "PC"
port = 8883

client = mqtt.Client()
window = tkinter.Tk()
db_name = "employees.db"


def analyze_server_response(client, userdata, message):
    response = str(message.payload.decode('utf-8'))
    print(response)
    if response == "Not registered.":
        print("Please wait for the server to add you to the database and connect again.")
    elif response == "Registered.":
        print("Terminal registered. Attempting to connect.")
        call_emp("Client reconnected")
    elif response == "Refused.":
        print("Registering refused. Disconnecting")
        client.disconnect()
        window.quit()

def show_users_and_cards():
    cards_window = tkinter.Tk()
    cards_window.title(" Available cards")
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    employees = cursor.execute("SELECT * FROM employees;").fetchall()
    connection.close()
    buttons = []
    for i in range(0, len(employees)):
        e = employees[i]
        buttons.append(tkinter.Button(cards_window, text=f"{e[1]} {e[2]}",
                                      command=lambda i=i: call_emp(str(employees[i][3]))))
        buttons[i].pack()
    unknown_card = tkinter.Button(cards_window, text="Unknown card", command=lambda: call_emp("-10"))
    unknown_card.pack()
    exit = tkinter.Button(cards_window, text="Close", command=cards_window.destroy)
    exit.pack()
    cards_window.mainloop()


def create_client_window():
    window.geometry("400x300")
    window.title("Client " + terminal_id)
    button_card = tkinter.Button(window, text="Use card",
                                 command=lambda: show_users_and_cards())
    button_exit = tkinter.Button(window, text="Exit", command=lambda:disconnect_from_broker())
    button_card.pack(fill=tkinter.X)
    button_exit.pack(fill=tkinter.X)


def connect_to_broker():
    # Connect to the broker.
    client.tls_set("C:\\Program Files\\mosquitto\\certs\\ca.crt") # provide path to certification
    # Authenticate
    client.username_pw_set(username='client', password='client')
    # Connect to the broker.
    client.connect(broker, port) # modify connect call by adding port
    client.on_message = analyze_server_response
    client.loop_start()
    client.subscribe("server/info")
    # Send message about connection.
    call_emp("Client connected")


def call_emp(card_id):
    client.publish("employee/name", card_id + "." + terminal_id,)


def reconnect_to_broker():
    # Connect to the broker.
    client.username_pw_set(username='client', password='client')
    client.connect(broker, port) # modify connect call by adding port
    client.on_message = analyze_server_response
    client.loop_start()
    client.subscribe("server/info")
    call_emp("Client reconnected")


def disconnect_from_broker():
    # Send message about disconenction.
    call_emp("Client disconnected")
    window.quit()
    # Disconnect the client.
    client.disconnect()


if __name__ == '__main__':
    connect_to_broker()
    create_client_window()
    window.mainloop()
    disconnect_from_broker()
