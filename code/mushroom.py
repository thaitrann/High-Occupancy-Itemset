import pandas as pd

# Đọc nội dung từ tệp tin txt vào danh sách
with open('E:\MyDesktop\ThaiTran\Personal_Project\High-Occupancy-Itemset\code\mushroom.txt', 'r') as file:
    content = file.readlines()

data = [line.strip().split('\n') for line in content]

# Tạo DataFrame từ danh sách và đặt tên cột là "Items"
df = pd.DataFrame(data, columns=['Items'])
df['Length'] = df['Items'].apply(lambda x: len(x.split()))
df['Items'] = df['Items'].apply(lambda x: list(map(int, x.split())))
# Tạo cột "Tid" từ chỉ số của từng dòng
df['Tid'] = list(map(lambda x: 'T' + str(x), range(1, len(df) + 1)))
df['Items'] = df['Items'].apply(lambda x: [str(item).strip(" ") for item in x])
# Hiển thị DataFrame
df = df.head(10)
print(df)