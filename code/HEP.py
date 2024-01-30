import pandas as pd
from collections import Counter
import time
# from data_test import *

start_time = time.time()

# sample
data = {
    'Tid': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
    'Items': [['a', 'c', 'd'],
              ['a', 'b', 'd'],
              ['b', 'c', 'd', 'e'],
              ['a', 'd'],
              ['c', 'd', 'e'],
              ['a', 'b', 'c', 'd', 'e']]
}
df = pd.DataFrame(data)
df['Item_Length'] = df['Items'].apply(lambda items: len(items))

unique_items = sorted(df['Items'].explode().unique())

# calculate occupancy list
def occupancy_list(df):
    occupancy_list = {}
    for item in unique_items:
        tid_list = df[df['Items'].apply(lambda items: item in items)]['Tid'].tolist()
        tid_lengths = [(tid, len(df[df['Tid'] == tid]['Items'].iloc[0])) for tid in tid_list if item in df[df['Tid'] == tid]['Items'].iloc[0]]
        occupancy_list[item] = tid_lengths
    return occupancy_list

# calculate stset
def stset(occupancy_list):
    stset = {}
    for key, values in occupancy_list.items():
        stset[key] = [item[0] for item in values]
    return stset

# calculate support
def support(stset):
    support = {}
    support = {key: len(value) for key, value in stset.items()}
    return support

# calculate occupancy
def occupancy(occupancy_list):
    occupancy = {}
    for key, values_list in occupancy_list.items():
        total = 0
        for i in values_list:
            total += len(key)/i[1]
        occupancy[key] = round(total, 2)
    return occupancy

# ex: 'a': {'l(a)': [2, 3, 5], 'n(a)': [1, 2, 1]}
def prepare_UBO(occupancy_list):
    UBO = {}
    for key, list_values in occupancy_list.items():
        values = [i[1] for i in list_values]
        l_key = sorted(set(values))
    
        counter = Counter(values)
        n_key = [counter[i] for i in l_key]
        
        UBO[key] = {'l': l_key, 'n': n_key}
    return UBO

# calculate according to the formula: ni x lx/li
def cal_ubo(l, n):
    total = 0
    for i in range(len(l)):
        total += n[i] * l[0] / l[i]
    return round(total, 2)

# summarize: ∑ni x lx/li => save to list 
def ubo_final(length, number_transaction):
    ubo = []
    for i in range(len(length)):
        ubo.append(cal_ubo(length[i:], number_transaction[i:]))
    return ubo

# get max from summarize => save max value in UBO by key
def calculate_maxUBO(UBO):
    for key, values in UBO.items():
        list_values = list(values.values())
        
        length = list_values[0]
        number_transaction = list_values[1]

        # print(key, length, number_transaction, sep = " - ")
        ubo = max(ubo_final(length, number_transaction))
        UBO[key]['UBO'] = [ubo]
    return UBO

# UBO calculation methods
def UBO(occupancy_list):
    UBO = prepare_UBO(occupancy_list)    
    UBO = calculate_maxUBO(UBO)
    return UBO

# UBO result formatting
def show_UBO(UBO):
    for key, values in UBO.items():
        print("Key: " + key)
        for inner_key, inner_value in values.items():
            if inner_key.startswith("l"):
                print("# Different length in transactions - " + inner_key + ": " + str(inner_value))
            elif inner_key.startswith("n"):
                print("# Number of transactions with length - " + inner_key + ": " + str(inner_value))
            elif inner_key.startswith("UBO"):
                print("# Upper bound of occupancy - " + inner_key + ": " + str(inner_value))
        print("---")

# runtime
def runtime(start_time):
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

# the index, support, occupancy and UBO of each itemset
def itemset_info(occupancy, support, UBO):
    df_occupancy = pd.DataFrame(occupancy.items(), columns=['Item', 'O(P)'])
    df_support = pd.DataFrame(support.items(), columns=['Item', 'Sup(P)'])
    df_UBO = pd.DataFrame([(key, value['UBO'][0]) for key, value in UBO.items()], columns=['Item', 'UBO(P)'])
    
    merge_df = df_support.merge(df_occupancy, on = "Item").merge(df_UBO, on = "Item")
    
    return merge_df

# call function
occupancy_list = occupancy_list(df)
stset = stset(occupancy_list)
support = support(stset)
occupancy = occupancy(occupancy_list)
UBO = UBO(occupancy_list)

print(itemset_info(occupancy, support, UBO))
runtime(start_time)
