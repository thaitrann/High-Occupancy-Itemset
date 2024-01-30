import pandas as pd
from collections import Counter
import time
# from data_test import *

start_time = time.time()
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

occupancy_list = {}
for item in unique_items:
    tid_list = df[df['Items'].apply(lambda items: item in items)]['Tid'].tolist()
    tid_lengths = [(tid, len(df[df['Tid'] == tid]['Items'].iloc[0])) for tid in tid_list if item in df[df['Tid'] == tid]['Items'].iloc[0]]
    occupancy_list[item] = tid_lengths
    
stset = {}
for key, values in occupancy_list.items():
    stset[key] = [item[0] for item in values]

support = {}
support = {key: len(value) for key, value in stset.items()}

occupancy = {}
for key, values_list in occupancy_list.items():
    total = 0
    for i in values_list:
        total += len(key)/i[1]
    occupancy[key] = round(total, 2)

df_occupancy = pd.DataFrame(occupancy.items(), columns=['Item', 'O(P)'])
df_support = pd.DataFrame(support.items(), columns=['Item', 'Sup(P)'])

merge_df = df_support.merge(df_occupancy, on = "Item")

prepare_UBO = {}

for key, list_values in occupancy_list.items():
    values = [i[1] for i in list_values]
    l_key = sorted(set(values))
    
    counter = Counter(values)
    n_key = [counter[i] for i in l_key]
    
    prepare_UBO[key] = {'l({})'.format(key): l_key, 'n({})'.format(key): n_key}   

def cal_ubo(l, n):
    total = 0
    for i in range(len(l)):
        total += n[i] * l[0] / l[i]
    return round(total, 2)

def ubo_final(length, number_transaction):
    ubo = []
    for i in range(len(length)):
        ubo.append(cal_ubo(length[i:], number_transaction[i:]))
    return ubo

for key, values in prepare_UBO.items():
    list_values = list(values.values())
    length = list_values[0]
    number_transaction = list_values[1]
    print(key, length, number_transaction, sep = " - ")
    ubo = ubo_final(length, number_transaction)
    print(max(ubo))
    print("---")
    
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")

    