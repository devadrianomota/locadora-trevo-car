import mysql.connector
from mysql.connector import Error
import os

class Database:
    def __init__(self):
        # ⚠️ ALTERE ESTAS CONFIGURAÇÕES conforme seu MySQL!
        self.host = 'localhost'
        self.database = 'trevocar'
        self.user = 'root'
        self.password = 'mota1413@'  # ⬅️ COLOQUE SUA SENHA AQUI!
        
    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if connection.is_connected():
                print("✅ Conectado ao MySQL!")
                return connection
        except Error as e:
            print(f"❌ Erro ao conectar com MySQL: {e}")
            return None

# Teste a conexão
if __name__ == "__main__":
    db = Database()
    conn = db.get_connection()
    if conn:
        conn.close()
        print("✅ Conexão testada com sucesso!")