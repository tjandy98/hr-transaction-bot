import sqlite3

conn = sqlite3.connect('transactions.db')
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS transactions")
#Creating table as per requirement
sql ='''CREATE TABLE Transactions(
     id CHAR(50),
     user CHAR(50),
   amount FLOAT, comment CHAR(250), category CHAR(50), createdDate CHAR(20)
)'''
cursor.execute(sql)
print("Table created successfully........")
conn.commit()
conn.close()


sql = 'INSERT INTO transactions VALUES( "dfcfd2c6-fe81-4cd2-868f-f1983c47714f","356543671", 10.0, "10", "Food", "2022-01-08 07:55:13")'