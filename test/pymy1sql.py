
import pymysql

DBHOST = "127.0.0.1"
USER = "root"
PASSWORD = "19951023chen"
DATABASE = "douban"
DBPORT = 3306
score = [] #评分
num = [] #评分相同的电影数量
con = pymysql.connect(DBHOST, USER, PASSWORD, DATABASE, DBPORT)
cur = con.cursor()  # 声明一个游标
sql = "select score,count(score) from movie250 group by score"
cur.execute(sql)
data =cur.fetchall()
for item in data:
    score.append(item[0])
    num.append(item[1])    # 放到列表里面去
cur.close()
con.close()
print(score)
print(num)