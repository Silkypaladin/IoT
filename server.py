
import uuid


def fetch_data_from_db (filename):
    #kolejność danych w pliku pracownikow: emp_id, card_id, name, surname
    #kolejność danych w pliku kart: card_id, emp_id, enter_time, work_time
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
    if (isinstance(emp_id,int)):
        emp_id = str(emp_id)
    card_id = employees[emp_id][0]
    if (isinstance(card_id, int)):
        card_id = str(card_id)
    if (emp_id in employees):
        if (employees[emp_id][0] == -1):
            return True
        else:
            employees[emp_id][0] = -1
            cards[card_id][0] = -1
            return True
    else:
        return False


def add_RFID(employees, cards, emp_id, card_id):
    if (isinstance(emp_id,int)):
        emp_id = str(emp_id)
    if (isinstance(card_id, int)):
        card_id = str(card_id)
    if (emp_id in employees and card_id in cards):
        if (employees[emp_id][0] != -1 or cards[card_id][0] != -1):
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



def startUp(card_file, emp_file):
    #Tworzymy sobie dwa slowniki na ktorych bedziemy dzialac (to tylko żeby cos bylo, pozniej skonfigurujesz baze danych)
    #glowna petla tutaj, przypisanie i usuniecie karty po indeksach(?)
    employees = fetch_data_from_db(emp_file)
    cards = fetch_data_from_db(card_file)
    delete_RFID(employees, cards, 1)
    print(employees)
    print(cards)
    add_RFID(employees, cards, 1, 10)
    print(employees)
    print(cards)
    return (employees, cards)

def loop(data):
    employees = data[0]
    cards = data[1]


if __name__ == "__main__":

    data = startUp("cards.txt", "employees.txt")
