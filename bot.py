from collections import UserDict
import datetime
import pickle
import re


file_name = 'data.bin'


class Field:
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if not value.startswith('+') or len(value) < 11:
            raise ValueError
        self.__value = value


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value
    
    @property
    def value(self):
        if self.__value is None:
            return None
        return self.__value.strftime('%d.%m.%Y')
    
    @value.setter
    def value(self, value):
        try:
            self.__value = datetime.datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Wrong format")
        

class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phones = [phone] if phone else []
        self.birthday = birthday

    def add_birthday(self, birthday):
        self.birthday = birthday

    def add_phone(self, phone):
        self.phones.append(phone)
        
    def change_phone(self, index, phone):
        self.phones[index] = phone
        
    def delete_phone(self, phone):
        self.phones.remove(phone)
    
    
class AddressBook(UserDict):
    def iterator(self, n):
        start = 0
        end = n
        counter = len(self)
        while counter > 0:
            lst = []
            for i in list(self.keys())[start:end]:
                record = self.data[i]
                bd = record.birthday.value if record.birthday else 'not indicated'
                lst.append(f'{i} : {", ".join(str(phone) for phone in record.phones)} : {bd}')
            yield "\n".join(lst)
            start += n
            end += n
            counter -= n
            
    def add_record(self, record):
        if self.get(record.name.value):
            return f'{record.name.value} is already in contacts'
        self.data[record.name.value] = record
        self.dump_file()
        
    def dump_file(self):
        with open(file_name, 'wb') as file:
            pickle.dump(self.data, file)

    @staticmethod
    def load_file():
        with open(file_name, 'rb') as file:
            unpacked = pickle.load(file)
            string = ''
            for name, recs in unpacked.items():
                phones = [str(p) for p in recs.phones]
                bd = recs.birthday if recs.birthday else None
                string += f'{name} : {phones} : {bd} \n'
            return string


contacts = AddressBook()


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except ValueError:
            return "Number is incorrect"
        except KeyError:
            return "There is no contact with that name"
        except IndexError:
            return "Give me a name and phone please"
    return wrapper


def help(*args):
    return """
help: To see this message
add <Name> <phone> <birthday>: add contact
change <Name> <new_phone>: change contact's name of phone
show all: List of contacts
hello: hello
phone <Name>: To see phone number of <Name>
exit: If you want to exit
birthday <name>: To see when birthday
"""


def hello(*args):
    return "How can I help you?"


@input_error
def add(*args):
    obj = args[0].split()
    name = Name(obj[0])
    p = Phone(obj[1])
    try:
        bd = Birthday(obj[2])
        record = Record(name, p, bd)
        contacts.add_record(record)
        return f"Added <{name.value}> with phone <{p.value}>. Birthday: {bd.value}"
    except ValueError:
        record = Record(name, p)
        contacts.add_record(record)
        return f"Added <{name.value}> with phone <{p.value}>"


@input_error
def phone(*args):
    name = args[0]
    record = contacts.get(name)
    bd = record.birthday
    if bd is None:
        bd = "not indicated"
    if record:
        return f"{name} : {', '.join(str(p) for p in record.phones)} : {bd}"
    raise KeyError         


@input_error
def change(*args):
    obj = args[0].split()
    name = Name(obj[0])
    p = Phone(obj[1])
    record = contacts[name.value]
    record.change_phone(0, p)
    return f"Changed phone <{p}>, with name <{name}>"


@input_error
def show_all(*args):
    obj = args[0].split()
    lst = []
    if len(contacts.data) == 0:
        return "list of contacts is empty..."
    if len(obj) > 0:
        n = obj[0]
        n = int(n)
        res = contacts.iterator(n)
        for i in res:
            lst.append(f"[{i}]")
        return f"{' '.join(lst)}"
    else:
        load = contacts.load_file()
        return load
        # for k, v in contacts.data.items():
        #     record = contacts.data[k]
        #     bd = record.birthday
        #     if bd == None:
        #         bd = "not indicated"
        #     list.append(f"{k}: {', '.join(str(phone) for phone in record.phones)} : {bd}")
        # return "\n".join([f"{item}"for item in list])


@input_error
def exit(*args):
    return "Good bye"


@input_error
def unknown_command(*args):
    return "Invalid command"


@input_error    
def birthday(*args):
    name = args[0]
    record = contacts.get(name, "not indicated")
    bd = record.birthday
    if record:
        return f"Birthday: {bd}"


def find(*args):
    if len(args) != 1:
        return "Enter one parameter"
    pattern = args[0].lower()
    result = []
    for name, recs in contacts.data.items():
        match_name = re.findall(pattern, name.lower())
        match_phones = [re.findall(pattern, str(phone)) for phone in recs.phones]
        match_birthday = re.findall(pattern, str(recs.birthday.value))
        if match_name or any(match_phones) or match_birthday:
            phones = [str(p) for p in recs.phones]
            result.append(f"{name} : {phones} : {recs.birthday}")
    if result:
        return "\n".join(result)
    return "No matches found"


def days_to_birthday(*args):
    birthday = args[0]
    if not birthday:
        return f"Not indicated"
    bd = datetime.datetime.date(birthday)
    now = datetime.datetime.now()
    if bd.month >= now.month:
        if bd.day >= now.day:
            if bd.day == 0:
                return "Happy birthday today"
            else:
                return f"Days left: {bd.day}"
        else:
            difference = (now - bd).days
            return f"Days left {difference}"
    else:
        difference = (now - bd).days
        return f"Days left {difference}"


COMMANDS = {
    help: "help",
    hello: "hello",
    add: "add",
    phone: "phone",
    change: "change",
    show_all: "show all",
    exit: "exit",
    birthday: "birthday",
    find: "find",
    days_to_birthday: "days left",
}


def handler(string):
    for key, value in COMMANDS.items():
        if string.startswith(value):
            return key, string.replace(value, "").strip()
    return unknown_command, contacts


def main():
    while True:
        user_input = input("Enter command: ")
        command, data = handler(user_input)
        print(command(data))
        if command == exit:
            break


if __name__ == "__main__":
    print(hello() + " Type <help> if you need help.")
    main()
    