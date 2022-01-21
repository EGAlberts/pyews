from pyews.server_interface import ewsRESTInterface as eRI 
from pyews.global_vars import settings
import numpy as np
import time 
COLLECTION_WINDOW = 60
DESIRED_SAMPLES = 10
CHOSEN_METRIC = "response_time"
CONFIG = 0
REWARD = 1
N_K = 2


definitions = {
    "URL" : "http://localhost:2011/",    
    "main_component" : "../repository/TCPNetwork.o",
    "proxy_JSON" : {"exp":"|../metacom/monitoring/proxies/HTTPProxy.o|*(*:http.handler.GET.HTTPGET[0]:*)|"}
} 

settings["IP"] = definitions["URL"]

eRI.initialize_server(definitions["main_component"],definitions["proxy_JSON"])

configurations = eRI.get_all_configs()

knowledge = [[config, 0, 1] for config in configurations] #[config, cumulative reward, times_chosen]


def truncate_normalize(cost, preferHigh):
    upper_bound = 300
    lower_bound = 0
 #truncate
    if(cost > upper_bound):
        cost = upper_bound
    elif(cost < lower_bound):
        cost = lower_bound

    result = float(cost/upper_bound) #normalize
    
    if(not preferHigh):
        result = 1.0 - result

    return result

def e_greedy(arms, knowledge):
    EPSILON = 0.5

    choice = np.random.random()

    selected_arm = None
    if choice < EPSILON: selected_arm = np.random.choice(len(arms))
    else: selected_arm = knowledge.index(max(knowledge, key=lambda k: k[REWARD]/k[N_K])) #max of the averages, and then the index of that.

    return selected_arm


while(True):
    new_configuration_i = e_greedy(configurations, knowledge)
    eRI.change_configuration(configurations[new_configuration_i])

    time.sleep(COLLECTION_WINDOW)

    sample_list = []
    while(len(sample_list) < DESIRED_SAMPLES):
        perception = eRI.get_perception()
            
        reading = None

        if(CHOSEN_METRIC in perception.metric_dict):
            reading = perception.metric_dict[CHOSEN_METRIC]
        
        if(reading):
            sample_list.extend([truncate_normalize(individual_value,reading.is_preference_high) \
                for individual_value in reading.value_list])
        else:
            print("There is no traffic being experienced by the EWS")
    
    sample_list = np.random.choice(sample_list, size = DESIRED_SAMPLES) #limit to 10 in case of over-sampling

    knowledge[new_configuration_i][REWARD] += sum(sample_list)
    knowledge[new_configuration_i][N_K] += DESIRED_SAMPLES






