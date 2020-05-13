from bs4 import BeautifulSoup
import urllib
import xlwt
import re
import pymysql

#------数据爬虫------


DBHOST = "127.0.0.1"
USER = "root"
PASSWORD = "password"
DATABASE = "douban"
DBPORT = 3306


datalist = []
# 主流程：获取数据、解析内容、保存数据
def main():
    baseurl = "https://movie.douban.com/top250?start="
    askURL(baseurl)
    # 爬取网页
    datalist = getData(baseurl)

    #保存数据到数据库
    saveDataDB(datalist)

    # 保存数据到excel表中
    # savepath = "豆瓣电影Top250_1.xls"
    # saveData(datalist, savepath)


#判断是否表存在
# 判断数据库是否存在
def data_exists():
    # 使用的数据库
    database = DATABASE
    db = pymysql.connect(DBHOST, USER, PASSWORD, DATABASE, DBPORT)
    cursor = db.cursor()  # 创建游标
    sql = "show databases"
    cursor.execute(sql)
    databases = [cursor.fetchall()] #查询所有数据
    databases_list = re.findall('(\'.*?\')',str(databases))
    databases_list = [re.sub("'",'',each)for each in databases_list]
    if database in databases_list:
        print("%s:数据库已经存在"%database)
    else:
        # 创建数据库
        sql = "CREATE DATABASE IF NOT EXISTS " + database
        try:
            cursor.execute(sql)
            db.commit()
            print("数据库创建成功！")
        except:
            db.rollback()
            print("数据库创建异常，回滚。。")

# 判断表是否存在
def table_exists ():
    # 爬虫存储表
    table = 'movie250'
    db = pymysql.connect(DBHOST, USER, PASSWORD, DATABASE, DBPORT)
    cursor = db.cursor()  # 创建游标

    sql = "show tables"
    cursor.execute(sql)
    tables = cursor.fetchall()
    tables_list = re.findall('(\'.*?\')',str(tables))
    tables_list = [re.sub("'",'',each)for each in tables_list]
    if table in tables_list:
        print("爬虫存储表：%s\t已表存在！！！！"%table)
    else:
        print("表不存在！")
        try :
            init_db()
            print("表：%s创建成功！"%table)
        except:
            db.rollback()
            print("%s表异常，已回滚。。"%table)



def askURL(url):
    # 模拟浏览器头部信息，向豆瓣服务器发送信息
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }
    # 用户代理：表示告诉豆瓣服务器，我们是什么类型的机器，浏览器（本质上是告诉浏览器，我们可以接收什么水平的文件内容）
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)
    return html


# 影片详情链接的规则
findLink = re.compile(r'<a href="(.*?)">')  # 创建正则表达式对象，表示规则(字符串的模式)
# 影片图片的链接
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)  # re.S 忽视换行符
# 影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 找到评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
# 找到概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
# 找到影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


# 爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0, 10):  # 调用回去页面信息的函数 · 10次
        url = baseurl + str(i * 25)
        html = askURL(url)  # 保存获取到的网页源码
        # 逐一解析数据
        soup = BeautifulSoup(html, "html.parser")
        # 查找符合要求的字符串，形成列表
        for item in soup.find_all('div', class_='item'):
            # print(item)  # 测试查看电影item全部信息
            data = []  # 保存一部电影的所有信息
            item = str(item)

            link = re.findall(findLink, item)[0]  # re库用来通过正则表达式查找指定的字符串
            data.append(link)  # 添加链接
            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)

            titles = re.findall(findTitle, item)
            # data.append(titles)
            # 片名可能只有一个中文名，没有英文名
            if (len(titles) == 2):
                ctitle = titles[0]
                data.append(ctitle)  # 添加中文名
                otitle = titles[1].replace("/", "")  # 去掉无关的符号
                data.append(otitle)  # 添加外国名
            else:
                data.append(titles[0])
                data.append(' ')  # 外国名留空

            rating = re.findall(findRating, item)[0]
            data.append(rating)

            judgeNum = re.findall(findJudge, item)[0]
            data.append(judgeNum)

            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")  # 去掉句号
                data.append(inq)  # 添加概述
            else:
                data.append(" ")  # 留空

            bd = re.findall(findBd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)', " ", bd)  # 去掉<br/>
            bd = re.sub('/', " ", bd)  # 替换/
            data.append(bd.strip())  # 去掉前后的空格
            datalist.append(data)  # 把处理好的一部电影信息放入datalist
    for it in datalist:
        print(it)
    return datalist


# 保存数据到excel表
def saveData(datalist,savepath):
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建film对象
    sheet = book.add_sheet("豆瓣电影Top250", cell_overwrite_ok=True)  # 创建工作表
    col = ("电影详情链接", "图片链接", "影片中文名", "影片外国名", "评分", "评价数", "概况", "相关信息")
    for i in range(0, 8):
        sheet.write(0, i, col[i])  # 写入列名
    for i in range(0, 250):
        print("第%d条" % (i + 1))
        data = datalist[i]
        for j in range(0, 8):
            sheet.write(i + 1, j, data[j])  # 写入数据

    book.save(savepath)  # 保存


def saveDataDB(datalist):
    data_exists()
    table_exists()
    db = pymysql.connect(DBHOST, USER, PASSWORD, DATABASE, DBPORT)
    print("连接成功！！")
    cur = db.cursor()  # 声明一个游标
    print("开始插入数据！")

    for data in datalist:
        for index in range(len(data)):
            if index == 4 or index == 5:
                continue
            print(data[index])
            data[index] = '"'+data[index]+'"' #给插入数据加入双引号
        sql = '''
                INSERT INTO movie250 (
                info_link,pic_link,cname,ename,score,rated,instroduction,info) 
                VALUES(%s)'''%",".join(data)
        # print(sql)
        cur.execute(sql)
        db.commit()
    print('插入完成！')
    cur.close()
    db.close()


def init_db():

    try:
        db = pymysql.connect(DBHOST, USER, PASSWORD, DATABASE, DBPORT)
        print("连接成功！！")
        cur = db.cursor()  # 声明一个游标
        sql = 'CREATE TABLE `movie250` (`id` int(11) NOT NULL AUTO_INCREMENT,`info_link` text,`pic_link` text,`cname` text,`ename` text,`score` float(16,2) DEFAULT NULL,`rated` int(11) DEFAULT NULL,`instroduction` text,`info` text,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;'
        cur.execute(sql)
        print("表创建成功")
    except pymysql.err as e:
        print("表创建失败：" + str(e))


if __name__ == "__main__":
    main()
    print("爬取完毕!")
