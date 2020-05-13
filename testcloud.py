import jieba #分词
from matplotlib import pyplot as plt #绘图 数据可视化
from wordcloud import WordCloud #词云
from PIL import Image #图片处理
import numpy as np #矩阵计算
import pymysql

#词云生成

DBHOST = "127.0.0.1"
USER = "root"
PASSWORD = "password"
DATABASE = "douban"
DBPORT = 3306

#准备词云需要的文字
# con = sqlite3.connect("movie.db")
# cur = con.cursor()
con = pymysql.connect(DBHOST, USER, PASSWORD, DATABASE, DBPORT)
cur = con.cursor()  # 声明一个游标
sql = 'select  instroduction from movie250'
cur.execute(sql)
data = cur.fetchall()
text = ""
for item in data:
    # print(item)
    text = text + item[0]
    # print(item[0])
print(text)
cur.close()
con.close()

#分词
cut = jieba.cut(text)
string = " ".join(cut)
print(len(string))

img = Image.open(r'.\static\assets\img\ds1.png')
img_array = np.array(img)
wc = WordCloud(background_color='white',mask=img_array,font_path="SIMYOU.TTF")
wc.generate_from_text(string)

#绘制图片
fig = plt.figure(1)
plt.imshow(wc)
plt.axis('off') #是否显示坐标轴

# plt.show() #显示生成

plt.savefig(r'.\static\assets\img\wordnew.png',dpi=500)