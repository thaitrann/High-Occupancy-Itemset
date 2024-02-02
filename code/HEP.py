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
    df_occupancy_list = pd.DataFrame(occupancy_list.items(), columns=['Items', 'Occupancy_list'])
    return df_occupancy_list

# calculate stset
def stset(df_occupancy_list):
    df_stset = pd.DataFrame(columns=['Items', 'Occupancy'])

    for index, row in df_occupancy_list.iterrows():
        item = row['Items']
        occupancy_list = [tid for tid, _ in row['Occupancy_list']]
        df_stset = df_stset.append({'Items': item, 'Occupancy': occupancy_list}, ignore_index=True)
    return df_stset

# calculate support
def support(df_stset):
    df_support = pd.DataFrame(columns=['Items', 'Support'])
    df_support['Items'] = df_stset['Items']
    df_support['Support'] = df_stset['Occupancy'].apply(len)
    return df_support

# calculate occupancy
def occupancy(df_occupancy_list):
    occupancy_data = []
    for index, row in df_occupancy_list.iterrows():
        item = row['Items']
        occupancy_list = row['Occupancy_list']
        total = 0
        for tid, length in occupancy_list:
            total += len(item) / length
        occupancy_data.append({'Items': item, 'Occupancy': round(total, 2)})
    
    df_occupancy = pd.DataFrame(occupancy_data)
    
    return df_occupancy

# ex: 'a': {'l(a)': [2, 3, 5], 'n(a)': [1, 2, 1]}
def df_prepare_UBO(df_occupancy_list):
    UBO_data = []
    for index, row in df_occupancy_list.iterrows():
        item = row['Items']
        occupancy_list = row['Occupancy_list']
        
        values = [i[1] for i in occupancy_list]
        l_item = sorted(set(values))
    
        counter = Counter(values)
        n_item = [counter[i] for i in l_item]
        
        UBO_data.append({'Items': item, 'l_item': l_item, 'n_item': n_item})
    
    df_UBO = pd.DataFrame(UBO_data)
    return df_UBO

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
def calculate_maxUBO(df_UBO):
    df_UBO['List_UBO'] = None
    df_UBO['Max_UBO'] = None
    for index, row in df_UBO.iterrows():
        length = row['l_item']
        number_transaction = row['n_item']
        
        ubo = ubo_final(length, number_transaction)
        max_ubo = max(ubo)
        
        df_UBO.at[index, 'List_UBO'] = ubo
        df_UBO.at[index, 'Max_UBO'] = max_ubo
        
    return df_UBO

# UBO calculation methods
def UBO(df_occupancy_list):
    df_UBO = df_prepare_UBO(df_occupancy_list)    
    df_UBO = calculate_maxUBO(df_UBO)
    return df_UBO

# runtime
def runtime(start_time):
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

# the index, support, occupancy and UBO of each itemset
def itemset_info(df_occupancy, df_support, df_UBO):
    merge_df = df_support[['Items', 'Support']].merge(df_occupancy[['Items', 'Occupancy']], on = "Items").\
        merge(df_UBO[['Items', 'Max_UBO']], on = "Items")
    
    return merge_df

def df_intersection(items1, items2, df_occupancy_list):
    df = pd.DataFrame(columns=['Items', 'Occupancy_list'])
    list1 = df_occupancy_list.loc[df_occupancy_list['Items'] == items1, 'Occupancy_list'].iloc[0]
    list2 = df_occupancy_list.loc[df_occupancy_list['Items'] == items2, 'Occupancy_list'].iloc[0]
    
    intersection_list = list(set(list1) & set(list2))
    intersection_list = sorted(intersection_list, key = lambda x: x[0])
    intersection_items = items1 + items2

    df = df.append({'Items': intersection_items, 'Occupancy_list': intersection_list}, ignore_index=True)
    return df

def hep_algorithm(threshold, df, df_itemset_info, df_occupancy_list):
    threshold = threshold * len(df)
    C1 = set()
    HO1 = set()
    
    for index, row in df_itemset_info.iterrows():
        items = row['Items']
        support = row['Support']
        occupancy = row['Occupancy']
        max_ubo = row['Max_UBO']
        
        if support >= threshold:
            if max_ubo >= threshold:
                C1.add(frozenset(items))
                # C1.add(items)
            if occupancy >= threshold:
                HO1.add(frozenset(items))
                # HO1.add(items)

    # return C1, HO1
    
    # Generate Ck and HOk
    k = 2
    Ck_1 = C1
    HOk = [HO1]
    
    while Ck_1:
        Ck = set()
        for P1 in Ck_1:
            for P2 in Ck_1:
                if len(set(P1).intersection(set(P2))) == k - 2:
                    P = frozenset([P1, P2])
                    P_occupancy_list = df_intersection(P1, P2, df_occupancy_list)
                    ubo = UBO(P_occupancy_list)['Max_UBO'].iloc[0]
                    if ubo >= threshold:
                        Ck.add(P)
                        if len(P_occupancy_list) >= threshold:
                            HOk.append(P)
        k += 1
        Ck_1 = Ck
    
    # Return the set of all high occupancy itemsets
    HO_Set = set()
    for itemsets in HOk:
        HO_Set.update(itemsets)
    
    return HO_Set            
    
# call function
df_occupancy_list = occupancy_list(df)
df_stset = stset(df_occupancy_list)
df_support = support(df_stset)
df_occupancy = occupancy(df_occupancy_list)
df_UBO = UBO(df_occupancy_list)
df_itemset_info = itemset_info(df_occupancy, df_support, df_UBO)

# print(df_occupancy_list)
# print(df_stset)
# print(df_support)
# print(df_occupancy)
# print(df_UBO)
print(df_occupancy_list)

threshold = 0.25
HO_Set = hep_algorithm(threshold, df, df_itemset_info, df_occupancy_list)
print(HO_Set)

# C1, HO1 = hep_algorithm(threshold, df, df_itemset_info, df_occupancy_list)
# print(C1)

# C1 = {'a', 'd', 'c', 'e', 'b'}

# ck = set()

# for i in C1:
#     for j in C1:
#         p = set(i).union(set(j))
#         print(p)
# #         ck.add(p)
# # print(ck)

runtime(start_time)

