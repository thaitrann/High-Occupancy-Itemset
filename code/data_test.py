import pandas as pd
import random

data = {
    'Tid': [],
    'Items': []
}

alphabet = 'abcde'

for i in range(1, 10000):
    tid = 'T' + str(i)
    items = list(set(random.choices(list(alphabet), k=random.randint(1, 26))))
    
    data['Tid'].append(tid)
    data['Items'].append(items)

df = pd.DataFrame(data)
print(df)
