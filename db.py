FILENAME = "money.txt"

#  Read the text file


def read_money():
    with open(FILENAME, "r") as file:
        line = file.readline()

    return float(line)


#  Write (update) the money in text file
def write_money(money):
    with open(FILENAME, "w") as file:
        file.write(str(money))