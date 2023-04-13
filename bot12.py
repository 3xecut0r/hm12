from collections import UserDict
import datetime
import json

file_name = "contacts.json"

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
        self.__value = None
        self.value = value
        
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if value is None:
            return value
    
        if not value.startswith('+') or len(value) < 11:
            raise ValueError
        self.__value = value

class Birthday(Field):
    def __init__(self, value):
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
        except:
            raise ValueError("Wrong format")
        

class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phones = [phone] if phone else []
        self.birthday = birthday

    def add_birthday(self, birthday):
        self.birthday = birthday
    
    def days_to_birthday(self):
        if not self.birthday:
            return None
        bd = datetime.datetime.date(self.birthday)
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
        self.data[record.name.value] = record
        self.dump_file()
    
    def dump_file(self):
        contact = {}
        with open(file_name, 'w') as file:
            for name, record in self.data.items():
                phone = [str(phone) for phone in record.phones]
                bd = record.birthday.value if record.birthday else 'not indicated'
                contact.update({'contacts':{
                    name:{
                    'phones':phone,
                    'birthday':bd,
                }}})
                json.dump(contact, file, indent=4)
                contact = {}
        
    def load_file(self):
        try:
            with open(file_name, 'r') as file:
                data = json.load(file)
                return data['contacts']
        except FileNotFoundError:
            pass
        
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
    phone = Phone(obj[1])
    try:
        bd = Birthday(obj[2])
        record = Record(name, phone, bd)
        contacts.add_record(record)
        return f"Added <{name.value}> with phone <{phone.value}>. Birthday: {bd.value}"
    except:
        record = Record(name, phone)
        contacts.add_record(record)
        return f"Added <{name.value}> with phone <{phone.value}>"

@input_error
def phone(*args):
    name = args[0]
    record = contacts.get(name)
    bd = record.birthday
    if bd == None:
        bd = "not indicated"
    if record:
        return f"{name} : {', '.join(str(phone) for phone in record.phones)} : {bd}"
    raise KeyError         

@input_error
def change(*args):
    obj = args[0].split()
    name = Name(obj[0])
    phone = Phone(obj[1])
    record = contacts[name.value]
    record.change_phone(0, phone)
    return f"Changed phone <{phone}>, with name <{name}>"

@input_error
def show_all(*args):
    obj = args[0].split()
    list = []
    if len(contacts.data) == 0:
        return "list of contacts is empty..."
    if len(obj)>0:
        n = obj[0]
        n = int(n)
        res = contacts.iterator(n)
        for i in res:
            list.append(f"[{i}]")
        return f"{' '.join(list)}"
    else:
        s = contacts.load_file()
        for name, recs in s.items():
            phones = []
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

COMMANDS = {
    help:"help",
    hello:"hello",
    add:"add",
    phone:"phone",
    change:"change",
    show_all:"show all",
    exit:"exit",
    birthday:"birthday"
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