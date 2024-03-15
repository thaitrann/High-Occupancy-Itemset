import pandas as pd

df = pd.read_csv("E:\MyDesktop\ThaiTran\Personal_Project\High-Occupancy-Itemset\code\demo_web\demo_web.csv")
df['Items'] = df['Items'].apply(lambda x: x.split(','))
if __name__ == "__main__":
    print(df)