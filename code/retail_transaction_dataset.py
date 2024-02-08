import pandas as pd
import ast

# data = pd.read_csv("E:\Download\đề tài dự án 2\Retail_Transactions_Dataset.csv\Retail_Transactions_Dataset.csv")

# df = data[['Transaction_ID', 'Product']]
# df = df.rename(columns={'Transaction_ID': 'Tid', 'Product': 'Items'})


# # Biến đổi cột "Product" thành danh sách các sản phẩm
# df['Items'] = df['Items'].apply(lambda x: ast.literal_eval(x))



import pandas as pd

# Đọc dữ liệu từ tệp CSV
df = pd.read_csv("E:\Download\đề tài dự án 2\OnlineRetail.csv", encoding='latin1')
filtered_df = df.query('Quantity > 0')
# Lấy các cột 'invoiceNo' và 'Description'
invoice_description = filtered_df[['InvoiceNo', 'Description']]

invoice_description_dict = {}

# Duyệt qua từng hàng trong DataFrame
for index, row in invoice_description.iterrows():
    invoiceNo = row['InvoiceNo']
    description = row['Description']
    
    # Kiểm tra nếu invoiceNo đã tồn tại trong dictionary
    if invoiceNo in invoice_description_dict:
        # Nếu đã tồn tại, thêm description vào danh sách đã có
        invoice_description_dict[invoiceNo].append(description)
    else:
        # Nếu chưa tồn tại, tạo danh sách mới và thêm vào dictionary
        invoice_description_dict[invoiceNo] = [description]

df_new = pd.DataFrame(invoice_description_dict.items(), columns=['Tid', 'Items'])
df = df_new.head(100)