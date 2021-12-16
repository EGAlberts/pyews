from pyews.server_interface import ewsRESTInterface as eRI
from pyews.utilities import print_relation_list, http_post, print_comp_list, print_tree
from pyews.server_abstractions import Configuration, Relation, Component

import enum
class ConfigurationModel:
    """Builds a model representation of the ews and provides control over it."""
    
    def __init__(self):
        self.__build_bank()
                        
    def __build_bank(self):
        """Fills the component_bank and relation_bank sets with all Component and Relation objects of all configurations."""
        self.component_bank = set(())
        self.relation_bank = set(())

        configuration_list = eRI.get_all_configs() #this should ensure that the elements in the bank can still be linked to their respective configs

        for configuration in configuration_list:
            for component in configuration.get_component_list():
                self.component_bank.add(component)
                for relation in component.get_relations():
                    self.relation_bank.add(relation)

    
    def get_component_bank(self):
        """Returns the component_bank, set of all components across configurations."""
        return self.component_bank
    
    def get_relation_bank(self):
        """Returns the relation_bank, set of all relations across configurations."""
        return self.relation_bank
        
    def component_dependency_spectrum(self, component):
        """For a given Component object comp, returns a list of Relation objects from the relation_bank in which comp is the parent component i.e. comp requires x for y."""
        #all relations in which component is parent_comp i.e. 'requires' another component
        #it should hold that a component is the parent in all its relations
        relations_with_component_as_parent = []

        for relation in self.relation_bank:
            if relation.parent_comp == component:
                relations_with_component_as_parent.append(relation)
        return relations_with_component_as_parent

    def relations_with_alternatives(self,given_configuration = None):
        """For a given Configuration object (or the current configuration by default) prints and returns all the relations with alternatives to them."""
        if(given_configuration != None):
            configuration = given_configuration
        else:
            configuration = eRI.get_config()
        
        relation_list = configuration.get_relation_list()

        list_with_alts = []

        for relation in relation_list:
            if len(self.relation_alternative(relation)) > 0: #possibly more efficient to immediately provide tuple with relation_alternative result
                #print(relation.description() + " has alternatives, specifically:")
                list_with_alts.append(relation)
                #print_relation_list(self.relation_alternative(relation))
                #print("end")
        return list_with_alts

    def relation_alternative(self,relation = None):
        """For a given Relation object (or the one picked through user input by default) returns a list of the other Relation objects which are alternative to it."""

        if(relation == None):
            print("Please pick by index which relation you'd like to see the alternatives of (current_config) (index 5 illustrates best)")
            current_config = eRI.get_config()
            print_relation_list(current_config.get_relation_list())
            chosen_index = int(input("index? "))
            relation = current_config.get_relation(chosen_index)


        alternatives = []

        list_dependent_relations = self.component_dependency_spectrum(relation.parent_comp)

        for dependent_relation in list_dependent_relations:
            #we already know their parent comp matches, now to see if they serve the same purpose
            if (dependent_relation.name == relation.name) and (dependent_relation != relation):
                alternatives.append(dependent_relation)
        
        return alternatives

    def all_sets_of_alternatives(self):
        """Independent of any one configuration, returns list of lists of alternative relations"""

        #the idea is, it cannot be assumed that one configuration reveals the possible alternatives across all
        #a configuration 

        #There are two ways I can think of, 1. Pass over all configurations, run them through relations_with_alternatives, store results in a set and return
        #2. Go through all relations in relation bank, run them through relation_alternative, and return those relations as a list of lists
        record_of_relations = []
        #this is 2.
        list_of_variables = []
        for relation in self.get_relation_bank():
            if(relation not in record_of_relations):
               

                current_rel_alt_list = self.relation_alternative(relation)
                current_rel_alt_list.append(relation) #add self to list
                
                if(len(current_rel_alt_list) > 1):
                    #print(relation.description())
                    #print("was not in")
                    #print_relation_list(record_of_relations)
                    record_of_relations.extend(current_rel_alt_list)
                    list_of_variables.append(current_rel_alt_list)

        return list_of_variables

    class FeatureDiagram:
        def __init__(self, config_model):
            self.parent_model = config_model
            self.diagram_dictionary = dict()

            all_configurations_list = eRI.get_all_configs()

            base = all_configurations_list[0] #this can be any index

            base_tree = base.tree_variant("BASE",components_to_exclude = [rel.child_comp for rel in self.parent_model.relations_with_alternatives(base)])

            dict_tree = base_tree.as_adjacency_dict()

            self.add_compdict_to_dict(dict_tree)

            self.gather_alternatives()

            new_alts = dict(self.diagram_dictionary)

            all_values = []
            for keys,values in self.diagram_dictionary.items():
                all_values.extend(values)
                
            for value in all_values:
                if value not in new_alts:
                    child_values = value.children
                    new_alts[value] = child_values
                    all_values.extend(child_values)

            self.diagram_dictionary = new_alts

            
    
        def get_decompositions(self):
            """Returns a subset of the feature diagram's dictionary containing only the decompositions """ 
            subset = dict()

            for key in self.diagram_dictionary:
                if type(key) is ConfigurationModel.FeatureDiagram.DiagramDecomposition:
                    subset[key] = self.diagram_dictionary[key]
                     
            return subset
                


        def gather_alternatives(self):
            """Determines the decompositions of the Feature Diagram."""
            all_sets_of_alts_list = self.parent_model.all_sets_of_alternatives()

            all_decomps = []
            for alternative_set in all_sets_of_alts_list:
                feature = self.DiagramFeature(alternative_set[0].parent_comp) #for example HTTPHeader

                self.add_to_dict(feature)           

                alternative_features = [] #HTTPGET, GETCMP, GETCH etc.
                name = ""
                for relation in alternative_set:
                    name = relation.name
                    child_feature = self.DiagramFeature(relation.child_comp)
                    alternative_features.append(child_feature)
                    self.add_to_dict(child_feature)

                decomp = self.DiagramDecomposition("Alternative",feature, alternative_features, name )
                
                #print("\nconsidering: " + alternative_set[0].parent_comp.name + "\n")
                for element in alternative_set[0].parent_comp.children:
                    feature_of_it = self.DiagramFeature(element)
                    if feature_of_it not in self.diagram_dictionary[feature]:
                        self.diagram_dictionary[feature].append(feature_of_it)

                
                all_decomps.append((feature,decomp))
               
            for featuretoaddto,decomp in all_decomps:
                self.add_decomp_to_dict(featuretoaddto,decomp)
                self.add_to_dict(decomp)

                
                #self.diagram_dictionary[decomp].extend(decomp.children)                

            
            #for keys,values in self.diagram_dictionary.items():

        def add_decomp_to_dict(self,row, decomp):
            values = self.diagram_dictionary[row]

            for value in values:
                if value in decomp.children:
                    self.diagram_dictionary[row].remove(value)
    
            self.diagram_dictionary[row].append(decomp)
      
        def add_to_dict(self, item):

            if(item not in self.diagram_dictionary):
                self.diagram_dictionary[item] = []
                self.diagram_dictionary[item].extend(item.children)
                return True
            else:
                return False

        def add_compdict_to_dict(self, given_dict):
            for keys,values in given_dict.items():
                key_feature = self.DiagramFeature(keys)
                
                list_feature_kids = []

                for value in values:
                    list_feature_kids.append(self.DiagramFeature(value))
                
                self.add_to_dict(key_feature)

        def base_check(self):
            """Verifies that the configurations when stripped of their alternates are all identical."""
            #check if bases are all the same

            #go through every configuration, 
            #find their alter-able component(s)
            #remove these from the configuration to generate the base
            # then compare each of these bases to check they're the same
            all_configurations_list = eRI.get_all_configs()
            
            first_config = all_configurations_list[0]

            first_alts = self.parent_model.relations_with_alternatives(first_config)

            first_component_list = [rel.child_comp for rel in first_alts]

            first_base = first_config.tree_variant("BASE",components_to_exclude = first_component_list)

            all_configurations_list.remove(first_config)


            for config in all_configurations_list:
                list_of_alterable__rels = self.parent_model.relations_with_alternatives(config)
                #print_relation_list(list_of_alterable_components) looks good
                list_of_components = [rel.child_comp for rel in list_of_alterable__rels]
                base_tree = config.tree_variant("BASE",components_to_exclude = list_of_components)

                if(base_tree != first_base):
                    return False
                
                    
                #print_comp_list(list_of_components) looks good
                

            return True
        
        class DiagramFeature:
            
            def __init__(self, component):
                "Makes a diagram feature, a wrapper for a Component."
                self.relationships = []
                self.name = component.name
                self.children = []

                for child in component.children:
                    self.children.append(ConfigurationModel.FeatureDiagram.DiagramFeature(child))

            def add_relationship(self,parent, child):
                self.relationships.append()

            def __repr__(self):
                return self.name

            def __eq__(self,obj):
                if(type(obj) == ConfigurationModel.FeatureDiagram.DiagramFeature):
                    return self.name == obj.name
                return False

            def __hash__(self):
                return hash(self.name)

        class DiagramDecomposition(DiagramFeature):
            relationship_types = enum.Enum('RelationshipType', 'Mandatory Alternative Optional Or')

            #parent
            #children
            
            def __init__(self, rel_type, parent, child_list, name):
                self.type = self.relationship_types[rel_type]
                
                if(rel_type == "Alternative"):
                    self.parent = parent
                    self.children = child_list

                self.name = str(self.type) + " " + name
            
            def __eq__(self,obj):
                if(type(obj) == ConfigurationModel.FeatureDiagram.DiagramDecomposition):
                    if( (len(self.children) == len(obj.children)) and (self.type == obj.type)):
                        self.children.sort(key= lambda feature: feature.name)
                        obj.children.sort(key= lambda feature: feature.name)

                        
                        for index in range(len(self.children)):
                            if(self.children[index] != obj.children[index]):
                                return False
                        return True

                    else:
                        return False
                else:
                    return False
            
            def __hash__(self):
                return hash(self.name)

    def feature_model(self):
        """Generates the feature diagram for the EWS as a whole."""
        feature_diagram = self.FeatureDiagram(self)
    
        return feature_diagram


    

        
  
    





        

