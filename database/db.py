import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
  host="localhost",					
  user="root",					
  password="Pass@123!",  # 🔹 put your MySQL password					
  database="socitymanagement"					
)					

    return connection
