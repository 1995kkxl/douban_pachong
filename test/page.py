
import pymysql

DBHOST = "127.0.0.1"
USER = "root"
PASSWORD = "19951023chen"
DATABASE = "douban"
DBPORT = 3306

datalist = []
con = pymysql.connect(DBHOST, USER, PASSWORD, DATABASE, DBPORT)
cur = con.cursor()  # 声明一个游标
sql = 'select * from movie250'
cur.execute(sql)
results = cur.fetchall()
for item in results:
    datalist.append(item)
print(datalist)
print(len(datalist))

cur.close()
con.close()