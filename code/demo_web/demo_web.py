import pandas as pd

df = pd.read_csv("E:\MyDesktop\ThaiTran\Personal_Project\High-Occupancy-Itemset\code\demo_web\demo_web.csv")
df['Items'] = df['Items'].apply(lambda x: x.split(','))
df['Items'] = df['Items'].apply(lambda x: list(set(x)))
if __name__ == "__main__":
    print(df)
        # Lấy danh sách các dòng có phần tử bị trùng lặp trong cột "Items"
    duplicated_rows = df[df['Items'].apply(lambda x: len(set(x)) != len(x))]
    print(len(duplicated_rows))
    df.to_csv("E:\MyDesktop\ThaiTran\Personal_Project\High-Occupancy-Itemset\code\demo_web\demo_web_remove_dup.csv")