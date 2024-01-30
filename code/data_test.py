import pandas as pd
import random

data = {
    'Tid': [],
    'Items': []
}

alphabet = 'abcdefghijklmnopqrstuvwxyz'

for i in range(1, 100):
    tid = 'T' + str(i)
    items = random.choices(list(alphabet), k=random.randint(1, 26))
    
    data['Tid'].append(tid)
    data['Items'].append(items)

df = pd.DataFrame(data)
