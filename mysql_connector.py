import pymysql
import os
from dotenv import load_dotenv
import pymysql.cursors
from pypika import Query, Table, Field
from pypika.queries import QueryBuilder

load_dotenv()

class MYSQLConnector:
    def __init__(self):
        self.conn = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            port=3306,
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database='jeommechu',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close
        
    def excute_query(self, query_obj:QueryBuilder):
        sql = query_obj.get_sql()
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()