

def fetch_employees_from_db (filename):
    file = open(filename, "r")
    for line in file:
        fields = line.split(";")
        for field in fields:
            print(field)


def fetch_cards_from_db (filename):
    file = open(filename, "r")
    for line in file:
        fields = line.split(";")


if __name__ == "__main__":
    fetch_employees_from_db("employees.txt")
