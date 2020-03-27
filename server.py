
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

def delete_RFID():
    pass

def add_RFID():
    pass

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
    emp = fetch_data_from_db(emp_file)
    cards = fetch_data_from_db(card_file)



if __name__ == "__main__":
