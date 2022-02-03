from collections import deque, namedtuple
from datetime import datetime
import json
import copy
class Configuration:
    """A class representing a configuration of the Emergent Web Server."""
    #component list
    #relation list
    def __eq__(self, obj):
        if(type(obj) == Configuration):
            return obj.original_json == self.original_json

    def __hash__(self):
        return hash(self.original_json)

    def __init__(self, config_text):
        "Given a JSON string corresponding to a Configuration of the Emergent Web Server creates a Configuration object."
        self.original_json = config_text
        config_text = config_text.split("|")
        components = config_text[1].split(",")
        relations = config_text[2].split(",")
        self.__process_components(components)
        self.__process_relations(relations)
      
    def get_component(self,index):
        """Returns the Component object of the given index in the Configuration object's component_list."""
        return self.component_list[index]
        
    def get_relation(self,index):
        """Returns the Relation object of the given index in the Configuration object's relation_list."""
        return self.relation_list[index]

    def get_relation_list(self):
        """Returns the list of Relation objects corresponding to the Configuration object."""
        return self.relation_list
    
    def get_component_list(self):
        """Returns the list of Component objects corresponding to the Configuration object."""
        return self.component_list

    def __process_components(self,text_comp_list):
        """During creation of a Configuration object, creates the component_list based on json_text"""
        temp_list = []
        for text_comp in text_comp_list:
            temp_list.append(Component(text_comp, self))

        self.component_list = temp_list
    
    def __process_relations(self,text_rels_list):
        """During creation of a Relation object, creates the relation_list based on json_text"""
        temp_list = []
        for text_rel in text_rels_list:
            temp_list.append(Relation(text_rel,self.component_list))

        self.relation_list = temp_list
          
        
    def tree_variant(self,variant, components_to_exclude = None, thread_component = None):
        """Constructs the TreeRepresentation class' instances."""
        return self.TreeRepresentation(component_list = self.component_list,variant = variant,components_to_exclude=components_to_exclude,thread_component=thread_component)


    def arborification(self, indexing=True):
        """Returns the configuration as a tree"""
        tree_rep = self.TreeRepresentation(self.component_list, "FULL")

        return tree_rep
    
    class TreeRepresentation:
        """A wrapper for the data structure representing the dependencies between components of a configuration of the EWS"""
        def __init__(self, component_list, variant, components_to_exclude = None, thread_component = None):
            """
            There are three variants FULL, BASE, and THREAD. 
            Full requires no optional arguments. 
            BASE requires components_to_exclude.
            THREAD requires thread_component.
            """
            self.structure = []
            self.root_layer = set(())

            
            if(variant == "FULL"):
                self.__complete_structure(component_list)
            elif(variant == "BASE"):
                if(components_to_exclude is not None):
                    self.__base_structure(component_list,components_to_exclude)
                else:
                    print("BASE requires list of components to exclude")
            elif(variant == "THREAD"):
                if(thread_component is not None):
                    self.__thread(thread_component)
                else:
                    print("THREAD requires component to act as root")
            else:
                print("Invalid variant of TreeRepresentation")

    
        def __complete_structure(self, component_list):
            """Creates a tree of the configuration in its entirety."""
            for component in component_list:
                if len(component.parents)== 0:
                    self.root_layer.add((component,"root"))

            self.structure.append(list(self.root_layer))

            new_layer = self.root_layer
            #begin while   
            while(len(new_layer) > 0):
                new_layer = []
                
                for element_index in range(len(self.structure[-1])):
                    children = self.structure[-1][element_index][0].children
                    
                    for child in children:
                        new_layer.append((child,element_index))
                if(len(new_layer) > 0):
                    self.structure.append(new_layer)
            

        def __base_structure(self, component_list, components_to_exclude):        
            """Creates a tree of the configuration with the components_to_exclude, removed."""
            for component in components_to_exclude:
                #print(component.name)
                if(component) not in component_list:
                    print("A component given does not belong to same configuration")
                    exit(1)


            component_ids = [id(comp) for comp in components_to_exclude]


            
            for component in component_list:
                if len(component.parents)== 0:
                    self.root_layer.add((component,"root"))

            self.structure.append(list(self.root_layer))

            new_layer = self.root_layer
            #begin while   
            while(len(new_layer) > 0):
                new_layer = []
                
                for element_index in range(len(self.structure[-1])):
                    children = self.structure[-1][element_index][0].children
                    
                    for child in children:
                        if(id(child) not in  component_ids):
                            new_layer.append((child,element_index))
                if(len(new_layer) > 0):
                    self.structure.append(new_layer)
            #end while
            
        def __thread(self, given_component):
            """Generates a tree starting at the given_component."""

            self.root_layer.add((given_component,"root"))

            self.structure.append(list(self.root_layer))

            new_layer = self.root_layer

            while(len(new_layer) > 0):
                new_layer = []
                for element_index in range(len(self.structure[-1])):
                    children = self.structure[-1][element_index][0].children
                    for child in children:
                        new_layer.append((child,element_index))
                if(len(new_layer) > 0):
                    self.structure.append(new_layer)

        def __eq__(self, obj):
            if(type(obj) == Configuration.TreeRepresentation):
                if(len(self.structure) == len(obj.structure)):
                    for layer_index in range(len(self.structure)):
                        layer_A = self.structure[layer_index]
                        layer_B = obj.structure[layer_index]

                        if(len(layer_A) != len(layer_B)):
                            return False

                        for layer_item_index in range(len(layer_A)):
                            layer_A_item = layer_A[layer_item_index]
                            layer_B_item = layer_B[layer_item_index]

                            if((layer_B_item[1] != layer_B_item[1]) or (layer_A_item[0] != layer_B_item[0])):
                                return False   

                    return True
     
                return False
            
            return False

        def remove_indexing(self):
            new_structure = []

            for layer in self.structure:
                new_layer = []
                for item in layer:
                    new_layer.append(item[0])
                
                new_structure.append(new_layer)

            self.structure = new_structure

        def as_adjacency_dict(self):
            adj_dict = {}


            for layer_index in range(len(self.structure)):
                current_layer = self.structure[layer_index]
                
                position = 0
                for layer_item in current_layer:
                    adj_dict[layer_item[0]] = []
                    if(layer_index + 1 < len(self.structure)):
                        next_layer = self.structure[layer_index + 1]
                        for next_layer_item in next_layer:
                            if(next_layer_item[1] == position):
                                adj_dict[layer_item[0]].append(next_layer_item[0])
                    position+=1

            return adj_dict
                    
                    #(component,index)

            
            

            

        


        
        
   


class Component:
    """A class representing the components of a configuration of the Emergent Web Server."""
    def __init__(self,text_rep, parent_conf):
        self.name = text_rep.split("/")[-1] #last element is name of component e.g. TCPNetwork.o
        self.parents = []
        self.children = [] #this should align with the 'requires' in .dn files
        self.relations = set(())
        self.parent_configuration = parent_conf

    def add_parent(self, component):
        """Add a component to the list of parents, the components which require this component."""
        self.parents.append(component)

    def get_parent_config(self):
        """Returns the Configuration object to which this Component object belongs."""
        return self.parent_configuration

    def get_name(self):
        """Returns the name (the filename of the component) of a component."""
        return self.name

    def get_relations(self):
        """Returns the relations in which the components plays a role."""
        return self.relations     

    def __eq__(self, obj): 
        #Note: The Components across different configurations are all the same files, these are distinguished by their paths, the filename (name) is a part of that path
        #Therefore equality based on names is sufficient, in the case of identicallly named but differently pathed values, the full path from the JSON should be stored and
        #used for comparison instead. In the case of components from different configurations, compare the parent_configuration field.
        if(type(obj) == Component):
            return self.get_name() == obj.get_name()
        else:
            return False

    def __hash__(self):
        #This is relevant when using sets. 
        return hash((self.name)) 

    def __str___(self):
        return self.name

    def __repr__(self):
        return self.name

class Relation:
    """A class representing the relations between the components of a configuration of the Emergent Web Server."""
    name = "name"
    child_comp = None
    parent_comp = None #these need to be defined as they're used for hash etc. during initialization

    def __init__(self,text_rep, component_list): #passing list maybe not great solution
        """Given the part of the configuration's JSON string which represents relations, as well as the list of all components of the Configuration it is a part of."""
        relation_parts = text_rep.split(":") # e.g. 5:name:6

        
        self.parent_comp = component_list[int(relation_parts[0])]
        
        self.parent_configuration = self.parent_comp.get_parent_config()

        self.parent_comp.relations.add(self)

        self.name = relation_parts[1]

        self.child_comp = component_list[int(relation_parts[2])]
        
        self.child_comp.relations.add(self)

        if component_list[int(relation_parts[2])] not in component_list[int(relation_parts[0])].children:
            component_list[int(relation_parts[0])].children.append(component_list[int(relation_parts[2])])
        
        if component_list[int(relation_parts[0])] not in component_list[int(relation_parts[2])].parents:
            component_list[int(relation_parts[2])].parents.append(component_list[int(relation_parts[0])])

    def get_name(self):
        """Returns a name which describes the role the relation plays in the configuration."""
        return self.name
    
    def get_parent_comp(self):
        """Returns the Component object to which the relation relates some other component to it for it to function."""
        return self.parent_comp

    def get_child_comp(self):
        """Returns the dependent Component object of the relation."""
        return self.child_comp

    def description(self):
        """Returns a string which describes the given relation."""
        return self.parent_comp.name + " requires " + self.name  + " for " + self.child_comp.name + "." 

    def __eq__(self, obj):
        if(type(obj) == Relation):
            return ((self.get_name() == obj.get_name()) and (self.parent_comp == obj.parent_comp) and (self.child_comp == obj.child_comp))
        else:
            return False

    def __hash__(self):
        return hash((self.name, self.parent_comp, self.child_comp))

    def __str___(self):
        return self.description()

    def __repr__(self):
        return self.description()

        

class Perception:
    """A class which abstracts the details returned by the get_perception request to the Emergent Web Server into Event and Metric objects."""
    #config_index to indicate which configuration the system was in at time of perception
    def __init__(self, original_JSON):
        self.list_events = []
        if "events" in original_JSON:
            event_json_list = original_JSON["events"]
            for event_json in event_json_list:
                self.list_events.append(self.Event(event_json))
        
        self.metric_dict = dict()

        if "metrics" in original_JSON:
            metric_json_list = original_JSON["metrics"]
            for metric_json in metric_json_list:
                self.metric_dict[metric_json["name"]] = self.Metric(metric_json)
    def events_equal(self, other_perception):
        self.list_events.sort(key= lambda x: x.type)
        other_perception.list_events.sort(key = lambda x: x.type)
        return self.list_events == other_perception.list_events

  
        

    class Event:
        """Represent an event of the emergent_web_server."""
        def __init__(self, event_JSON):
            #could possibly be simplified/generalized using named tuple and json_loads object hook
            self.type = str(event_JSON["type"]) #This is actually an HTTP MIME type
            self.value = float(event_JSON["quantifier"])
            self.count = float(event_JSON["counter"])

            start_datetime = event_JSON['started']
            end_datetime = event_JSON['finished']

            self.start = datetime(year=start_datetime['year'], month=start_datetime['month'], day=start_datetime['day'],hour=start_datetime['hour'],minute=start_datetime['minute'], second=start_datetime['second'],microsecond=start_datetime['millisecond']*1000)
            self.finish = datetime(year=end_datetime['year'], month=end_datetime['month'], day=end_datetime['day'],hour=end_datetime['hour'],minute=end_datetime['minute'], second=end_datetime['second'],microsecond=end_datetime['millisecond']*1000)

            

        def __eq__(self, other):
            return ((self.type == other.type) and (self.source == other.source))

    class Metric:
        """Represents any metric e.g. response time, of the Emergent Web Server."""
        def __init__(self, metric_JSON):
            actual_metric = metric_JSON
            self.name = actual_metric["name"]
            if(self.name != "no_metric"):
                self.value = float(actual_metric["value"])
                self.count = float(actual_metric["counter"])
                self.is_preference_high = actual_metric["high"]

                start_datetime = actual_metric['started']
                end_datetime = actual_metric['finished']

                self.start = datetime(year=start_datetime['year'], month=start_datetime['month'], day=start_datetime['day'],hour=start_datetime['hour'],minute=start_datetime['minute'], second=start_datetime['second'],microsecond=start_datetime['millisecond']*1000)
                self.finish = datetime(year=end_datetime['year'], month=end_datetime['month'], day=end_datetime['day'],hour=end_datetime['hour'],minute=end_datetime['minute'], second=end_datetime['second'],microsecond=end_datetime['millisecond']*1000)
                #self.value_list = [int(value) for value in actual_metric["valueList"].split(" ")]
            
        def average_value(self):
            return self.value/self.count
            

     

        




