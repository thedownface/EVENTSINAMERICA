import json

class Variable:
    def get(variable_name):
        with open(f'{variable_name}.json','r') as json_file:
            Variable_dict=json.load(json_file)
            return Variable_dict
    
    def set(variable_name,updated_value:dict):
        with open(f'{variable_name}.json', "w") as json_file:
            json.dump(updated_value, json_file)
    
