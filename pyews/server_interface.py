import json
import requests
import pprint
from pyews.server_abstractions import Configuration, Perception, Relation, Component
from pyews.utilities import http_get, http_post
from pyews.global_vars import settings
#aligns with REsys.dn

class ewsRESTInterface:
    """Interfaces with the REST API of the emergent_web_server."""
    current_configuration = None
    config_objs = None # should be

    @staticmethod
    def initialize_server(main_component_path, proxy_JSON):
        """Initializes the EWS prior to its usage."""
        if(not settings["Initialized"]):
            settings["main_component_path"] = main_component_path
            ewsRESTInterface.set_main({"comp":settings["main_component_path"]})

            settings["proxy_JSON"] = proxy_JSON
            ewsRESTInterface.add_proxy(settings["proxy_JSON"])

            settings["Initialized"] = True
        else:
            print("Server already initialized")


    @staticmethod
    def set_main(main_component_JSON):
        """Assembles emergent_web_server based on component string argument."""
        http_post("meta/set_main", main_component_JSON)

    @staticmethod
    def set_config(arg):
        """Changes to configuration given as single-entry dict 'config : json_string'."""
        http_post("meta/set_config", arg)

    @staticmethod
    def get_config():
        """Returns current configuration of emergent_web_server as Configuration object"""
        current_config = Configuration(http_get("meta/get_config").json()["config"])
        return current_config

    @staticmethod
    def get_all_configs():
        """Returns all possible configuration of emergent_web_server as list of Configuration objects."""
        if(ewsRESTInterface.config_objs is None): #Does this check for a change in the total number of configs?
            configuration_list = []
            response = http_get("meta/get_all_configs")
            configs = eval(response.text)["configs"]

            for config in configs:
                new_config = Configuration(config)
                configuration_list.append(new_config)
            ewsRESTInterface.config_objs = configuration_list

        return list(ewsRESTInterface.config_objs)

    @staticmethod
    def get_perception():
        """Returns Perception object from get_perception of the emergent_web_server."""
        response = http_get("meta/get_perception")
        perception_json = None
        
        try:
            perception_json = response.json()
        except json.JSONDecodeError as jsonerror:
            print("Something went wrong parsing JSON")
            print("This is the document: ")
            print(jsonerror.doc)
            print("The error message:")
            print(jsonerror.msg)
            return None

        return Perception(perception_json[0])

    @staticmethod
    def get_proxies():
        """Gets proxies added to emergent_web_server, returns list."""
        response = http_get("meta/get_proxies")

        proxies_json = response.json()


        return proxies_json["proxies"]
    @staticmethod
    def add_proxy(arg):
        """Adds proxy to emergent_web_server given as single-entry dict 'exp : string'."""
        http_post("meta/add_proxy", arg)

    @staticmethod
    def add_comp(arg):
        """Adds a list of components by path to the EWS"""
        http_post("meta/remove_comp", arg)
        
    @staticmethod
    def remove_proxy(arg):
        """Removes a proxy, undoes what add_proxy does."""
        http_post("meta/add_proxy", arg)

    @staticmethod
    def remove_comp(arg):
        """Removes a list of components by path to the EWS"""
        http_post("meta/remove_comp", arg)
    @staticmethod
    def ip_list():
        """Not implemented."""
        pass

    @staticmethod
    def terminate():
        """The emergent_web_server stops running."""
        http_get("meta/terminate")

    ###As of this point functions do not originate in the REST interface i.e. do not align with REsys.dn

    @staticmethod
    def str_to_func(function_string):
        """Matches strings to functions."""

        func = {
            "set_main": ewsRESTInterface.set_main,
            "set_config": ewsRESTInterface.set_config,
            "get_config": ewsRESTInterface.get_config,
            "get_all_configs": ewsRESTInterface.get_all_configs,
            "get_perception": ewsRESTInterface.get_perception,
            "get_proxies": ewsRESTInterface.get_proxies,
            "add_proxy": ewsRESTInterface.add_proxy,
            "add_comp": ewsRESTInterface.add_comp,
            "remove_proxy": ewsRESTInterface.remove_proxy,
            "remove_comp": ewsRESTInterface.remove_comp,
            "ip_list": ewsRESTInterface.ip_list,
            "terminate": ewsRESTInterface.terminate
        }.get(function_string)

        return func()

    @staticmethod
    def __config_text(configuration):
        """Get the JSON string of a Configuration object."""
        return configuration.original_json

    @staticmethod
    def __config_by_component(component):
        """Get the JSON string of a Component object's configuration."""
        #we know the type is Component with certainty
        return ewsRESTInterface.__config_text(component.get_parent_config())
    
    @staticmethod
    def __config_by_relation(relation):
        """Get the JSON string of a Relation object's configuration."""
        return ewsRESTInterface.__config_by_component(relation.parent_comp)   
        
    #you would for example feed a result of relation_alternative into this function
    @staticmethod
    def change_configuration(key):
        """Change configuration using Configuration object, Relation object, or Component object given they're unique."""
        types = {
            Configuration: ewsRESTInterface.__config_text, 
            Relation: ewsRESTInterface.__config_by_relation,
            Component: ewsRESTInterface.__config_by_component
        }

        func = types.get(type(key))
        config_json = func(key)
        #need to check if switching to current config or should be eliminated by not being listed as alternative

        #print(config_json)
        if(config_json == ewsRESTInterface.__config_text(ewsRESTInterface.get_config())):
            print("tried switching to current config")
            return
        
        ewsRESTInterface.set_config({"config":config_json})

    
 
        