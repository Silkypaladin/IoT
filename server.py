import uuid
import random
import time
import datetime
import csv
import glob
import itertools


unregistered_cards = {}


def fetch_data_from_db(filename):
    # kolejność danych w pliku pracownikow: emp_id, card_id, name, surname
    # kolejność danych w pliku kart: card_id, emp_id, enter_time, leave_time, work_time
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
    if (emp_id in employees):
        card_id = employees[emp_id][0]
    else:
        return False
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
        if (employees[emp_id][0] == "-1" and cards[card_id][0] == "-1"):
            employees[emp_id][0] = card_id
            cards[card_id][0] = emp_id
            return True
        elif (cards[card_id][0] == "-1"):
            cards[employees[emp_id][0]][0] = "-1"
            employees[emp_id][0] = card_id
            cards[card_id][0] = emp_id
            return True
        else:
            return False

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


def print_cards(cards):
    for key in cards:
        print(f"Id karty: {key}")
    print("Wybierz kartę: ")
    return get_user_input()


def print_free_cards(cards):
    for key in cards:
        if (cards[key][0] == "-1"):
            print(f"Id wolnej karty: {key}")
    print("Podaj id karty, którą chcesz przypisać: ")
    return get_user_input()


def print_employees_ids(employees):
    print("Wybierz pracownika")
    for key in employees:
        print(f"Id pracownika: {key} - {employees[key][1]} {employees[key][2]}, id karty: {employees[key][0]}")
    return get_user_input()


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
        value[3] = "0"


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
    card_id = print_cards(cards)
    if (isinstance(card_id, int)):
        card_id = str(card_id)
    if card_id in cards:
        card = cards[card_id]
    else:
        return False
    if (card[0] != "-1"):
        if(card[1] == '0'):
            # pracownik odbija się po raz pierwszy
            card[1] = format_time(time.localtime())
            print(f"Pracownik o id: {card[0]} wszedł o godzinie: {card[1]}")
        else:
            # Pracownik odbija się drugi raz - wychodzi
            end_time = format_time(time.localtime())
            print(f"Pracownik o id: {card[0]} wychodzi o godzinie: {end_time}")
            work_time = calculate_worktime(card[1], end_time)
            card[2] = end_time
            card[3] = work_time
    else:
        print(f"Karta niezarejestrowana! Id: {card[0]}")


def generate_logs(cards, users):
    today = datetime.datetime.now()
    date = today.strftime("%d-%m-%Y_%H:%M.txt")
    filename = "./logs/log_"+date
    print(f"{filename} log generated.")
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


def generate_work_report(emp_id, employees):
    lines = []
    flat_lines = list()
    elems = []
    if (isinstance(emp_id, int)):
        emp_id = str(emp_id)
    if emp_id not in employees:
        print("Brak takiego użytkownika!Sprawdź id i spróbuj ponownie.")
        return False
    filename = f"report_{employees[emp_id][1]}_{employees[emp_id][2]}.csv"
    with open(filename, 'w+') as report:
        writer = csv.writer(report)
        writer.writerow([f'{employees[emp_id][1]}', f'{employees[emp_id][2]}', datetime.date.today()])
        writer.writerow(['Id karty', 'Godzina wejścia','Godzina wyjścia', 'Ilość przepracowanych godzin'])
        for log in glob.glob("./logs/*.txt"):
            with open(log, 'r') as read_log:
                lines.append(read_log.readlines())
        flat_lines = list(itertools.chain.from_iterable(lines))
        for line in flat_lines:
            elems = line.rstrip('\t\n').split(';')
            if elems[0] == emp_id:
                writer.writerow([elems[1], elems[4], elems[5], elems[6]])
    return True


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
          '\n4 - usunięcnie karty pracownikowi'
          '\n5 - wygenerowanie raportu czasu pracy dla pracownika'
          '\n0 - zakończenie działania programu')


def get_user_input():
    while True:
        try:
            choice = int(input('>'))
            break
        except ValueError:
            print('Podaj liczbę we właściwym formacie')
    return choice


if __name__ == "__main__":
    employees, cards = startUp("cards.txt", "employees.txt")
    display_menu()
    while True:
        choice = get_user_input()

        if choice == 1:
            add_new_user(employees)
        elif choice == 2:
            cid = print_free_cards(cards)
            eid = print_employees_ids(employees)
            if not add_RFID(employees, cards, eid, cid):
                print("Coś poszło nie tak! Sprawdź id i spróbuj ponownie.")
            print(employees)
            print(cards)
        elif choice == 3:
            read_card(cards)
        elif choice == 4:
            eid = print_employees_ids(employees)
            if not delete_RFID(employees, cards, eid):
                print("Coś poszło nie tak! Sprawdź id i spróbuj ponownie.")
        elif choice == 5:
            eid = print_employees_ids(employees)
            generate_work_report(eid, employees)
        elif choice == 0:
            generate_logs(cards, employees)
            reset_cards_timers(cards)
            save_data_to_db("employees.txt", employees)
            save_data_to_db("cards.txt", cards)
            break
        else:
            print('Ta opcja nie widnieje w menu')
