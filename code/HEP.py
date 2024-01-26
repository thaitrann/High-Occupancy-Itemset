import pandas as pd
from collections import Counter

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

# for key, values in occupancy_list.items():
#     print(f"{key}: {values}")

prepare_UBO = {}

for key, list_values in occupancy_list.items():
    values = [i[1] for i in list_values]
    l_key = sorted(set(values))
    
    counter = Counter(values)
    n_key = [counter[i] for i in l_key]
    
    prepare_UBO[key] = {'l({})'.format(key): l_key, 'n({})'.format(key): n_key}
    
for key, values in prepare_UBO.items():
    print(f"{key}: {values}")



