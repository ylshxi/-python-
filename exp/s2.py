# 引入库
import pymysql
import requests
from tkinter import *
from tkinter import END, DISABLED, NORMAL
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import matplotlib.pyplot as plt
from tkinter.messagebox import *
from sqlalchemy import create_engine
from sklearn.metrics import mean_squared_error, r2_score          # 使用r2_score对模型评估
from sklearn.linear_model import LinearRegression

# 设置展示的行列数最大值
pd.options.display.max_rows = 2000
# 全局存放爬取到的数据，供save函数使用
data = pd.DataFrame()
c = ''

# 创建 Tkinter 窗口
root = Tk()
root.title("20002447-xld")
root.geometry("900x400")

# 创建基本元素
L1 = Label(root, text="编号：", font=20)
L1.place(x=320, y=15)
E1 = Entry(root, bd=5, font=20, width=15)
E1.place(x=380, y=15)  # 固定文本窗位置
btn_read = Button(root, text='爬取数据', font=18, width=10)
btn_read.place(x=230, y=50)  # 固定窗口位置
btn_scatter = Button(root, text='保存数据', font=18, width=10)
btn_scatter.place(x=350, y=50)
btn_predict = Button(root, text='预测分析', font=18, width=10)
btn_predict.place(x=470, y=50)

# 创建一个文本框用于显示数据
text_data = ScrolledText(root, height=20, width=90, state=DISABLED)
text_data.place(x=140, y=100)


# 从网页上爬取或直接从数据库中获取金融数据
def baidu():
    global data
    global c
    code = E1.get()
    c = code
    # 初始化数据库连接
    # 按实际情况依次填写MySQL的用户名、密码、IP地址、端口、数据库名
    s = 'mysql+pymysql://root:root@localhost:3306/test1?charset=utf8'
    engine = create_engine(s)
    # 使用pandas的read_sql_query函数执行SQL语句，并存入dataFrame
    data_frame = pd.read_sql("show tables like '%s';" % ('s' + code), engine)
    if data_frame.empty:
        try:
            url = "https://finance.pae.baidu.com/selfselect/getstockquotation?all=1&code=" + code + \
                  "&isIndex=true&isBk=false&isBlock=false&isFutures=false&isStock=false&newFormat=1&" \
                  "is_kc=0&ktype=1&market_type=ab&group=quotation_index_kline&finClientType=pc"
            res = requests.get(url)
            res.encoding = res.apparent_encoding
            res = res.text
            # 数据处理、清洗
            table_head = res.split('"],"marketData":"')[0]
            table_head = table_head.split('"keys":["')[1].split('","')
            trade_data = res.split('"],"marketData":"')[1]
            trade_data = trade_data.replace('"}}}', '').replace('-', '').split(';')
            data_set = []
            for i in trade_data:
                i = i.split(',')
                data = {}
                for num in range(len(i)):
                    data[table_head[num]] = i[num]
                data_set.append(data)
            data_set = pd.DataFrame(data_set)
            data = data_set.loc[:, ['close', 'high', 'low', 'volume']]
        except:
            data = pd.DataFrame()
            showinfo('警告！', code + '相关数据无法获取！')
    else:
        if code != '':
            data = pd.read_sql('''SELECT * FROM  %s;''' % ('s' + code), con=engine)
        else:
            showinfo('警告！', code + '相关数据无法获取！')
    # 将数据显示在文本框中
    text_data.configure(state=NORMAL)
    text_data.delete('1.0', END)
    text_data.insert('end', str(data))
    text_data.configure(state=DISABLED)


# 绘图函数
def figure(title, *datalist):
    code =str(E1.get())
    plt.rcParams['font.family'] = ['SimHei']
    plt.figure(facecolor='gray', figsize=[16, 8])
    for v in datalist:
        plt.plot(v[0], '-', label=v[1], linewidth=2)
        plt.plot(v[0], 'o')
    plt.grid()
    plt.title(title, fontsize=20)
    plt.legend(fontsize=16)
    plt.savefig(code + ".png", dpi=1000, bbox_inches='tight')
    plt.show()

# 使用线性回归模型，根据最低价、最高价、成交量来预测收盘价
def predict():
    code = E1.get()
    # 连接数据库
    conn = pymysql.connect(host="localhost", user="root", password="root", database="test1")
    try:
        # 读取数据
        data = pd.read_sql('''SELECT * FROM  %s;''' % ('s' + code), con=conn)
        # 建立3个自变量与目标变量的线性回归模型
        data_new = data[['close', 'high', 'low', 'volume']]
        print(data_new)
        import numpy as np
        # 目标值
        y = np.array(data_new['close'])
        data_new = data_new.drop(['close'], axis=1)
        # 特征值
        X = np.array(data_new)
        from sklearn.model_selection import train_test_split
        # 划分训练集与测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        # print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
        from sklearn import preprocessing
        # 初始化标准化器
        min_max_scaler = preprocessing.MinMaxScaler()
        # 分别对训练和测试数据的特征以及目标值进行标准化处理
        X_train = min_max_scaler.fit_transform(X_train)
        y_train = min_max_scaler.fit_transform(y_train.reshape(-1, 1))  # reshape(-1,1)指将它转化为1列，行自动确定
        X_test = min_max_scaler.fit_transform(X_test)
        y_test = min_max_scaler.fit_transform(y_test.reshape(-1, 1))
        # 采用线性回归模型LinearRegression进行训练及预测
        lr = LinearRegression()
        # 使用训练数据进行参数估计
        lr.fit(X_train, y_train)
        # 使用测试数据进行回归预测
        y_test_pred = lr.predict(X_test)
        # 训练数据的预测值
        y_train_pred = lr.predict(X_train)

        # 绘制预测值与真实值图
        figure('预测值与真实值图 模型的' + r'$R^2=%.4f$' % (r2_score(y_train_pred, y_train)), [y_test_pred, '预测值'],
               [y_test, '真实值'])
    except:
        showinfo("预测失败")
    conn.close()


# 保存从网页上爬取的数据
def save():
    global data
    global c
    code = E1.get()
    if c == code:
        # 初始化数据库连接
        # 按实际情况依次填写MySQL的用户名、密码、IP地址、端口、数据库名
        s = 'mysql+pymysql://root:root@localhost:3306/test1?charset=utf8'
        engine = create_engine(s)
        try:
            data.to_sql(name='s' + code, con=engine, if_exists='replace', index=False)
            showinfo('提示', code + '数据存储成功！')
        except:
            showinfo('警告', code + '数据存储失败，请先获取数据！')
    else:
        showinfo('警告', code + '相关信息存储失败，请先获取数据！')



# 将函数绑定到按钮上
btn_read.config(command=baidu)
btn_scatter.config(command=save)
btn_predict.config(command=predict)

# 启动 Tkinter 窗口的消息循环
root.mainloop()
