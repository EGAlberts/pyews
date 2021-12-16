import requests
import pyews.global_vars
from pyews.global_vars import settings

def http_get(dir):
    "Uses 'requests' to HTTP GET request the given directory of the defined global IP."
    response = requests.get(settings["IP"] + dir)
    if response.status_code != 200:
        print("Something went wrong w/ GET")
    return response

def http_post(dir, json_text):
    "Uses 'requests' to HTTP POST to the given directory of the defined global IP, the given json_text."
    response = requests.post(settings["IP"] + dir, json=json_text)
    if(response.status_code == 200):
        print("HTTP POST to " + str(dir) + " successful")


def print_relation_list(rel_list):
    "Prints a given list of Relation objects."
    list_len = len(rel_list)
    print("#############################")
    print("There are " + str(list_len) + " relations:")
    print("#############################")
    if(list_len == 0):
        print("Tried to print empty relation list")
    else:
        for rel_index in range(list_len):
            print(str(rel_index) + ": " + rel_list[rel_index].description())

def print_tree(tree_obj, indexing = True):
    "Prints given the tree list structure returned by the arborification function of the Configuration object."

    tree_struct = tree_obj.structure
    if(indexing):
        for i in range(len(tree_struct)):
            print("\nLayer [" + str(i) + "]:", end = ' ')
            for sub_item in tree_struct[i]:
                print(sub_item[0].get_name() + ":" + str(sub_item[1]), end = ',')

            print("\n")
    else:
        for i in range(len(tree_struct)):
            print("\nLayer [" + str(i) + "]:", end = ' ')
            for sub_item in tree_struct[i]:
                print(sub_item.get_name(), end = ',')

            print("\n")
        
        
def print_comp_list(comp_list):
    "Prints a given list of Component objects."
    list_len = len(comp_list)
    print("#############################")
    print("There are " + str(list_len) + " components:")
    print("#############################")
    for comp_index in range(list_len):
        print(str(comp_index) + ":" + comp_list[comp_index].get_name(), end=', ')
    print("\n")

def show_configs(local_configuration_list):
    "Facilitates the printing of the components, relations, or tree of a given list of configurations."
    config_comm = ""
    print("There are " + str(len(local_configuration_list)) + " configurations")
    
    config_num = int(input("Select config 0-" + str(len(local_configuration_list)) + "\n"))
    while(config_comm != "exit"):
        config_comm = input("print_comp, print_conn, arb, or exit\n")
        if(config_comm == "print_comp"):
            print_comp_list(local_configuration_list[config_num].get_components())
        elif(config_comm == "print_conn"):
            print_relation_list(local_configuration_list[config_num].get_relations())
        elif(config_comm == "arb"):
            print_tree(local_configuration_list[config_num].arborification())


def create_file(file_name, directory = ""):
    """Given a file name and a directory optionally, creates that file there."""
    new_file = open(directory + file_name,"w")
    new_file.close()

def append_to_file(file_name, content, directory = ""):
    """Given a file_name, the content (list or primitives) to be appended, and optionally a directory, appends to that file."""
    append_file = open(directory + file_name,"a")

    if type(content) == list:
        for item in content:
            append_file.write(str(item) + "\n")

    else:
        append_file.write(str(content) + "\n")

    append_file.close()

def print_dict(given_dict):
    "Given a dictionary prints it out"
    for keys,values in given_dict.items():
        print(keys, end = " "),
        print(": ", end = " "),
        print(values)
        print("")