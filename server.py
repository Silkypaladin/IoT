
import uuid
import random
import time
import datetime

unregistered_cards = {}


def fetch_data_from_db(filename):
    # kolejność danych w pliku pracownikow: emp_id, card_id, name, surname
    # kolejność danych w pliku kart: card_id, emp_id, enter_time, work_time
    data_dict = dict()
    file = open(filename, "r")
    for line in file:
        fields = line.rstrip('\r\n').split(";")
        id = fields[0]
        data_dict[id] = fields[1:]
    return data_dict


def generate_uuid():
    return uuid.uuid1().hex


def delete_RFID(employees, cards, emp_id):
    if (isinstance(emp_id, int)):
        emp_id = str(emp_id)
    card_id = employees[emp_id][0]
    if (isinstance(card_id, int)):
        card_id = str(card_id)
    if (emp_id in employees):
        if (employees[emp_id][0] == "-1"):
            return True
        else:
            employees[emp_id][0] = "-1"
            cards[card_id][0] = "-1"
            return True
    else:
        return False


def add_RFID(employees, cards, emp_id, card_id):
    if (isinstance(emp_id, int)):
        emp_id = str(emp_id)
    if (isinstance(card_id, int)):
        card_id = str(card_id)
    if (emp_id in employees and card_id in cards):
        if (employees[emp_id][0] != "-1" or cards[card_id][0] != "-1"):
            return False
        else:
            employees[emp_id][0] = card_id
            cards[card_id][0] = emp_id
            return True
    else:
        return False


def get_employee(employees, emp_id):
    return employees[emp_id]


def save_data_to_db(filename, data):
    separator = ";"
    data_line = ""
    file = open(filename, "w+")
    for key, values in data.items():
        data_line += (key+separator)
        data_line += separator.join(values)
        file.write(data_line)
        file.write("\n")
        data_line = ""


def get_current_time():
    return time.localtime()


def calculate_worktime(start_time, end_time):
    """
    param start_time: start of work time in 'h:m:s' format
    param end_time: end of work time in 'h:m:s' format
    return: time spent working in 'h:m:s'
    """
    start = start_time.split(":")
    end = end_time.split(":")
    time = int(end[0]) * 60 + int(end[1]) - int(start[0]) * 60 - int(start[1])
    minutes = time % 60
    hours = int((time-minutes)/60)
    return "{}:{}".format(hours, minutes)


def reset_cards_timers(cards):
    for key, value in cards.items():
        value[1] = "0"
        value[2] = "0"


def format_time(wtime):
    """
    param wtime: time as struct_time instance
    """
    return time.strftime("%H:%M", wtime)


def add_new_user(users):
    name = input('Podaj imię nowego użytkownika: ')
    surname = input('Podaj nazwisko nowego użytkownika: ')
    user_id = uuid.uuid1().hex
    users[user_id] = ['-1', name, surname]
    print(f'ID nowego uzytkownika to: {user_id}\nPomyślnie dodano użytkownika {name} {surname}')


def read_card(cards):
    # card to krotka, zerowy element jest kluczem karty, pierwszy to tablica
    card = random.choice(list(cards.items()))
    if (card[1][0] != -1):
        if(card[1][1] == '0'):
            # pracownik odbija się po raz pierwszy
            card[1][1] = format_time(time.localtime())
            print(f"Pracownik o id: {card[1][0]} wszedł o godzinie: {card[1][1]}")
        else:
            # Pracownik odbija się drugi raz - wychodzi
            end_time = format_time(time.localtime())
            print(f"Pracownik o id: {card[1][0]} wychodzi o godzinie: {end_time}")
            work_time = calculate_worktime(card[1][1], end_time)
            card[1][2] = work_time
    else:
        print(f"Karta niezarejestrowana! Id: {card[0]}")


def generate_logs(cards, users):
    today = datetime.datetime.now()
    date = today.strftime("%d-%m-%Y_%H:%M")
    filename = "./logs/log_"+date
    print(filename)
    separator = ";"
    data_line = ""
    file = open(filename, "w+")
    for key, values in users.items():
        card_id = users[key][0]
        data_line += (key+separator)
        data_line += separator.join(values)
        data_line += (separator)
        data_line += separator.join(cards[card_id][1:])
        file.write(data_line)
        file.write("\n")
        data_line = ""


def generate_work_report(emp_id):
    pass


def startUp(card_file, emp_file):
    # Tworzymy sobie dwa slowniki na ktorych bedziemy dzialac
    employees = fetch_data_from_db(emp_file)
    cards = fetch_data_from_db(card_file)

    return (employees, cards)


def display_menu():
    print('Dostępne operacje. Wciśnij: '
          '\n1 - dodanie pracownika'
          '\n2 - przypisanie karty do pracownika'
          '\n3 - zbliżenie karty'
          '\n4 - usunięcnie katy pracownikowi'
          '\n5 - wygenerowanie raportu czasu pracy dla pracownika'
          '\n0 - zakończenie działania programu')


if __name__ == "__main__":
    data = startUp("cards.txt", "employees.txt")
    print(data)
    display_menu()
