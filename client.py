import paho.mqtt.client as mqtt
import tkinter

# Instancja klienta, potrzebne id, funkcja pozwalajaca odbic karte,
# Terminal id, any string
terminal_id = "T0"

# broker name or ip
broker = "localhost"

client = mqtt.Client()
window = tkinter.Tk()


def analyze_server_response(client, userdata, message):
    response = str(message.payload.decode('utf-8'))
    if response == "Not registered.":
        print("Please wait for the server to add you to the database and connect again.")
        client.disconnect()


def create_client_window():
    window.geometry("800x600")
    window.title("Client " + terminal_id)

    intro_label = tkinter.Label(window, text="Select employee:")
    intro_label.grid(row=0, columnspan=5)


def connect_to_broker():
    # Connect to the broker.
    client.connect(broker)
    client.on_message = analyze_server_response
    # Send message about connection.
    call_emp("Client connected")


def call_emp(card_id):
    client.publish("employee/name", card_id + "." + terminal_id,)


def disconnect_from_broker():
    # Send message about disconenction.
    call_emp("Client disconnected")
    # Disconnet the client.
    client.disconnect()
