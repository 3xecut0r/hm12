import json

data = {}
file_name = "contacts.json"



    # def dump_file(self):
        # with open(file_name, 'w') as fh:
        #     data = {
        #         'contacts': {name: {'phones': [str(phone) for phone in record.phones],
        #                             'birthday': record.birthday.value if record.birthday else None,}
        #                      for name, record in self.data.items()}}
        #     json.dump(data, fh, indent=4)
    
    # def load_file(self):
    #     try:
    #         with open(file_name, 'r') as fh:
    #             data = json.load(fh)['contacts']
    #             for name, record in data.items():
    #                 phones = [Phone(p) for p in record['phones']]
    #                 birthday = Birthday(record['birthday']) if record['birthday'] else None
    #                 self.add_record(Record(Name(name), phones, birthday))
    #     except FileNotFoundError:
    #         pass
