# Worktime Monitor

Worktime Monitor simulates worktime monitoring system, similar to those used in big companies, with employees' cards and terminals to scan them.

## Prerequisites

To make the project run properly you need some additional things:

[Mosquitto](https://mosquitto.org/download/) - MQTT broker, check out the page for additional information

Or on Linux based systems, for example (for Ubuntu):
```
sudo apt install mosquitto mosquitto-clients
```
And then enable the broker:
```
sudo systemctl enable mosquitto
```
You can check the status by running:
```
sudo systemctl status mosquitto
```
[Paho MQTT](https://pypi.org/project/paho-mqtt/) - MQTT Python client library

Run:
```
pip install paho-mqtt
```
to install.
[Tkinter](https://docs.python.org/3/library/tk.html) - Graphical User Interfaces library for python

Run:
```
sudo apt install python3-tk
```
to install.

The newest version of the project has security implemented. It uses OpenSSL along with ACL list and authorization. An additional file with configuration instructions is under creation, should appear
in repo soon. The code won't work without those things configured. To test no security version, switch to *older-v* branch. Usage instructions given below will work fine then.

## Usage

To test the code, first run:
```
python3 create_database.py
```
It will create an sqlite3 database called *employees.db*. Then, in separate terminals, run:
```
python3 server.py
```
```
python3 client.py
```
After that, you should be ready to go. At the start, a prompt message asking to add client to the database might pop up in the server terminal. Enter *1* to add it. Then just use both GUIs to use the functionalities.
To change terminal's id, edit *terminal_id* variable in *client.py*.
```python
terminal_id = "T1"
```

## Testing

To prepare your own system, simply edit *employees.txt* and *cards.txt*, following data format given in those two.

## Issues
Feel free to message me about any major issues. The project is still in development phase.
