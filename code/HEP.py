import pandas as pd
from collections import Counter
import time
# from data_test import *
# from mushroom import *
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

# data = {
#     'Tid': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
#     'Items': [['apple', 'cherry', 'durian'],
#               ['apple', 'banana', 'durian'],
#               ['banana', 'cherry', 'durian', 'elderberry'],
#               ['apple', 'durian'],
#               ['cherry', 'durian', 'elderberry'],
#               ['apple', 'banana', 'cherry', 'durian', 'elderberry']]
# }

df = pd.DataFrame(data)
print(df)
df['Item_Length'] = df['Items'].apply(lambda items: len(items))

unique_items = sorted(df['Items'].explode().unique()) # get unique item => save to list

# calculate occupancy list: {'a': [(T1, 3), (T2, 3), (T4, 2), (T6, 5)]} - list Tid, len(Tid) containing unique item
def occupancy_list(df):
    occupancy_list = {} 
    for item in unique_items:
        tid_list = df[df['Items'].apply(lambda items: item in items)]['Tid'].tolist() # create column Items with items in unique item
        tid_lengths = [(tid, len(df[df['Tid'] == tid]['Items'].iloc[0])) for tid in tid_list if item in df[df['Tid'] == tid]['Items'].iloc[0]] # length of Tid containing unique items
        occupancy_list[item] = tid_lengths # add value with item_key
    df_occupancy_list = pd.DataFrame(occupancy_list.items(), columns=['Items', 'Occupancy_list'])
    return df_occupancy_list

# calculate stset: {'a': [T1, T2, T4, T6]} - list of Tid containing unique item
def cal_stset(df_occupancy_list):
    df_stset = pd.DataFrame(columns=['Items', 'Occupancy'])

    for index, row in df_occupancy_list.iterrows():
        item = row['Items']
        occupancy_list = [tid for tid, _ in row['Occupancy_list']] # get Tid containing unique item
        df_stset = df_stset.append({'Items': item, 'Occupancy': occupancy_list}, ignore_index=True)
    return df_stset

# calculate support - count number of Tid containing unique item
def cal_support(df_stset):
    df_support = pd.DataFrame(columns=['Items', 'Support'])
    df_support['Items'] = df_stset['Items']
    df_support['Support'] = df_stset['Occupancy'].apply(len)
    return df_support

# calculate occupancy - O(P) = ∑ T ∈ STSet(P) |P|/|T|
# |P|: len(unique item) itemset {a} =>1
# |T|: len(Tid) 1/3 + 1/3 + 1/2 + 1/5 
def cal_occupancy(df_occupancy_list):
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
        l_item = sorted(set(values)) # get unique len(Tid) => sort ascending
    
        counter = Counter(values)
        n_item = [counter[i] for i in l_item] # count unique len(Tid) in occupancy_list => same index with l_item
        
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
        # ex: len = [2,3,5], num_trans = [1,2,1]
        # i = 0 => len = [2,3,5], num_trans = [1,2,1]
        # i = 1 => len = [3,5], num_trans = [2,1]
        # ...
        ubo.append(cal_ubo(length[i:], number_transaction[i:])) # save result cal_ubo for each i => get maxUBO
    return ubo
    
# get max from summarize => save max value in UBO by key
def calculate_maxUBO(df_UBO):
    df_UBO['List_UBO'] = None # create new column
    df_UBO['Max_UBO'] = None # create new column
    for index, row in df_UBO.iterrows():
        length = row['l_item'] #get list of len(Tid) containing unique item
        number_transaction = row['n_item'] # count unique len(Tid) in occupancy_list
        
        ubo = ubo_final(length, number_transaction) # get list of UBO by i. ex: [2.73, 2.6, 1.0]
        max_ubo = max(ubo) # max list of UBO
        
        df_UBO.at[index, 'List_UBO'] = ubo # save result in df
        df_UBO.at[index, 'Max_UBO'] = max_ubo # save result in df
        
    return df_UBO

# UBO calculation methods: main function
def cal_UBO(df_occupancy_list): 
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
    set1 = set(items1.split("|"))
    set2 = set(items2.split("|"))
    list_1_item = sorted(list(set1 | set2))
    intersection_items = '|'.join(list_1_item)
    
    list_occupancy_1_item = []
    
    for i in list_1_item:
        list_occupancy_1_item.append(df_occupancy_list.loc[df_occupancy_list['Items'] == i, 'Occupancy_list'].iloc[0])
        
    intersection = set(list_occupancy_1_item[0])
    for sublist in list_occupancy_1_item[1:]:
        intersection = intersection.intersection(sublist)

    intersection_list = sorted(intersection, key = lambda x: x[0])
    
    df = df.append({'Items': intersection_items, 'Occupancy_list': intersection_list}, ignore_index=True)

    return df

def hep_algorithm(threshold, df, df_itemset_info, df_occupancy_list):
    threshold = threshold * len(df) # ex: threshold = 25% of len(database)
    C1 = []
    HO1 = []
    
    for index, row in df_itemset_info.iterrows():
        items = row['Items'] # 1-itemset in row
        support = row['Support'] # support of 1-itemset
        occupancy = row['Occupancy'] # occuopancy of 1-itemset
        max_ubo = row['Max_UBO'] # max_ubo of 1-itemset
        
        if support >= threshold:
            if max_ubo >= threshold:
                # C1.add(frozenset(items)) # candidate 1-itemset => use item for C1 to create k-itemset (k = 2, k += 1 for each loop)
                C1.append(items)
            if occupancy >= threshold:
                # HO1.add(frozenset(items)) # High Occupancy 1-itemset.
                HO1.append(items)

    # return C1, HO1
    
    # Generate Ck and HOk
    k = 2
    Ck_1 = C1
    HOk = HO1
    
    while Ck_1:
        Ck = []
        for i in range(len(Ck_1)):
            for j in range(i+1, len(Ck_1)):
                if len(set(Ck_1[i]) & set(Ck_1[j])) == k - 2: # # C1 = {{'a'},{'b'},{'c'},{'d'},{'e'}}
                    # P = set(set(P1).union(set(P2)))
                    P_occupancy_list = df_intersection(Ck_1[i], Ck_1[j], df_occupancy_list)
                    p_items = P_occupancy_list['Items'].iloc[0]
                    # if p_items in HOk:
                    #     print(p_items)
                    #     continue
                    # else:
                    p_ubo = cal_UBO(P_occupancy_list)['Max_UBO'].iloc[0]
                    p_occupancy = cal_occupancy(P_occupancy_list)['Occupancy'].iloc[0]
                    if p_ubo >= threshold:
                        Ck.append(p_items)
                        if p_occupancy >= threshold:
                            HOk.append(p_items)
        k += 1
        Ck_1 = list(set(Ck))
        
    # Return the set of all high occupancy itemsets
    HO_Set = []
    for itemsets in HOk:
        HO_Set.append(itemsets)
    
    return HO_Set            
    
# call function
df_occupancy_list = occupancy_list(df)
df_stset = cal_stset(df_occupancy_list)
df_support = cal_support(df_stset)
df_occupancy = cal_occupancy(df_occupancy_list)
df_UBO = cal_UBO(df_occupancy_list)
df_itemset_info = itemset_info(df_occupancy, df_support, df_UBO)

# print(df_occupancy_list)
# print(df_stset)
# print(df_support)
# print(df_occupancy)
# print(df_UBO)

threshold = 0.25
# HO_Set = hep_algorithm(threshold, df, df_itemset_info, df_occupancy_list)
# print(HO_Set)

runtime(start_time)