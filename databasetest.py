import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="admin",passwd="1234",database="trainingdata")

mycursor =mydb.cursor()
mycursor.execute("select * from trainpatterns")
patterns = mycursor.fetchall()
num_fields =mycursor.rowcount
mycursor.execute("select * from responses")
responses = mycursor.fetchall()
i=  [i[0] for i in patterns]
print(i)