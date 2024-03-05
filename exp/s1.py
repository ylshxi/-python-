from tkinter import *
from tkinter import END, DISABLED, NORMAL
from tkinter.scrolledtext import ScrolledText
import pandas as pd
from tkinter.messagebox import *
import tushare as ts  # tushare获取一批金融数据
import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings

warnings.filterwarnings('ignore')  # 忽略警告
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示
plt.rcParams['axes.unicode_minus'] = False  # 解决符号无法显示

# 获取股票编号为600000的近十年的金融数据
df1 = ts.get_k_data('600000', ktype='D', start='2015-04-26', end='2020-04-26')
# 保存为.csv格式到当前目录
datapath1 = "./SH600000.csv"
df1.to_csv(datapath1)

data = []
# 创建 Tkinter 窗口
root = Tk()
root.title("20002447-xld")
root.geometry("900x400")
# 创建基本元素
L1 = Label(root, text="文件名：", font=20)
L1.place(x=320, y=15)
E1 = Entry(root, bd=5, font=20, width=15)
E1.place(x=380, y=15)


# 读取数据
def readata():
    global data
    x = str(E1.get())
    # 读取数据,如果能成功读取文件则显示读取成功，否则显示读取识别
    try:
        # data = pd.read_excel(x)
        data = pd.read_csv(x)

        data.head()
        # 将数据显示在文本框中
        text_data.configure(state=NORMAL)
        text_data.delete('1.0', END)  # 删除所有元素
        text_data.insert('end', str(data))  # 末尾插入
        text_data.configure(state=DISABLED)
        showinfo('提示', '读取成功')
    except:
        showinfo('提示', '读取失败')


# 绘制散点图
def scatter():
    try:
        global data
        plt.scatter(data["close"], data["volume"])
        plt.xlabel("收盘价")
        plt.ylabel("成交量")
        plt.title('股票数据分析图')
        plt.show()
        x = str(E1.get())
        plt.show()
        plt.savefig(x + "1.png", dpi=1000, bbox_inches='tight')  #保存分析结果
    except:
        showinfo("请先读取数据！")


# 绘制趋势图
def trend():
    global data
    try:
        # 保留日期（date）、开盘价（open）、收盘价（close）、成交量（volume）、开盘价（high）这几个属性
        data = data[['date', 'open', 'close', 'volume', 'high']]
        data.sort_values(by='date', inplace=True)  # 按时间先后顺序对数据进行排序

        plt.figure(figsize=(15, 8))  # 画布大小
        # 利用pandas把横坐标转为日期格式
        data['date'] = pd.to_datetime(data['date'])

        plt.plot(data['date'], data['open'], label='开盘价')  # 开盘价折线图
        plt.plot(data['date'], data['close'], label='收盘价')  # 收盘价折线图
        ax = plt.gca()  # 处理x轴字符重叠问题
        data_format = mpl.dates.DateFormatter('%Y')  # 处理x轴字符重叠问题
        ax.xaxis.set_major_formatter(data_format)  # 处理x轴字符重叠问题
        plt.xticks(rotation=45)  # 将x轴标签旋转45°
        plt.legend(loc='upper center')  # 添加图例
        x = str(E1.get())
        plt.show()
        plt.savefig(x + "2.png", dpi=1000, bbox_inches='tight') #保存分析结果
    except:
        showinfo("请先读取数据")


# 定义组件
B1 = Button(root, text="读入数据", font=18, width=10, command=readata)
B1.place(x=260, y=60)  # 给定义的组件固定位置
text_data = ScrolledText(root, height=20, width=100, state=DISABLED)  # 创建一个文本框用于显示读入的数据
text_data.place(x=115, y=100)
B2 = Button(root, text="绘制散点图", font=18, width=10, command=scatter)
B2.place(x=380, y=60)
B3 = Button(root, text="绘制趋势图", font=18, width=10, command=trend)
B3.place(x=500, y=60)
root.mainloop()
