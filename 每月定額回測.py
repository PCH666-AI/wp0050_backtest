import streamlit as st
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
pd.set_option('mode.chained_assignment', None)
def main():
    stock = pd.read_csv('0050歷史股價.csv', encoding='UTF-8', low_memory=False, index_col=False)
    dividend = pd.read_csv('0050歷史股利.csv', encoding='UTF-8', low_memory=False, index_col=False)
    
    max_price = stock.loc[0, '收盤價(元)']
    true_cost=[0]
    true_cost_reduce=[0]
    true_cost_increase=[0]
    
    dd = 0
    cost = [0]
    cost_reduce = [0]
    cost_increase = [0]
    cost_reinvest = [0]
    cum_dividend = [0]
    cum_dividend_reduce = [0]
    cum_dividend_increase = [0]
    cum_dividend_reinvest = [0]
    shares = [0]
    shares_reduce = [0]
    shares_increase = [0]
    shares_reinvest = [0]
    market_value = []
    market_value_reduce = []
    market_value_increase = []
    market_value_reinvest = []
    stock_price = []
    date = []
    
    date_str = stock.loc[0, '年月日']
    print("Date string:", date_str)
    month_check = int(date_str.split('/')[1])
    month_check = int(stock.loc[0, '年月日'].split('/')[1])
    stock['除息金額'] = 0
    for i in range(0, len(stock)):
        if stock.loc[i, '收盤價(元)'] >= max_price:     # 判斷DD
            max_price = stock.loc[i, '收盤價(元)']
            dd = 0
        else:
            dd = stock.loc[i, '收盤價(元)'] / max_price
        if dd == 0:
            quota_reduce = 10000
            quota_increase = 10000
        elif dd < 0.8:
            quota_reduce = 6000
            quota_increase = 14000
        stock_price.append(stock.loc[i, '收盤價(元)'])
        # t_date = stock.loc[i, '年月日'].split('/')
        month = int(stock.loc[i, '年月日'].split('/')[1])
        if month == month_check:      # 每月第一天定額買入
            shares.append(int(10000 / stock.loc[i, '收盤價(元)']) + shares[-1])
            shares_reduce.append(int(quota_reduce / stock.loc[i, '收盤價(元)']) + shares_reduce[-1])
            shares_increase.append(int(quota_increase / stock.loc[i, '收盤價(元)']) + shares_increase[-1])
            shares_reinvest.append(int(10000 / stock.loc[i, '收盤價(元)']) + shares_reinvest[-1])
            true_cost.append(int(stock.loc[i, '收盤價(元)'] * int(10000 / stock.loc[i, '收盤價(元)'])) + cost[-1])
            true_cost_reduce.append(int(stock.loc[i, '收盤價(元)'] * int(quota_reduce / stock.loc[i, '收盤價(元)'])) + cost_reduce[-1])
            true_cost_increase.append(int(stock.loc[i, '收盤價(元)'] * int(quota_increase / stock.loc[i, '收盤價(元)'])) + cost_increase[-1])
            cost.append(int(stock.loc[i, '收盤價(元)'] * int(10000 / stock.loc[i, '收盤價(元)'])) + cost[-1])
            cost_reduce.append(int(stock.loc[i, '收盤價(元)'] * int(quota_reduce / stock.loc[i, '收盤價(元)'])) + cost_reduce[-1])
            cost_increase.append(int(stock.loc[i, '收盤價(元)'] * int(quota_increase / stock.loc[i, '收盤價(元)'])) + cost_increase[-1])
            cost_reinvest.append(int(stock.loc[i, '收盤價(元)'] * int(10000 / stock.loc[i, '收盤價(元)'])) + cost_reinvest[-1])
            month_check += 1
            if month_check == 13:
                month_check = 1
        else:
            cost.append(cost[-1])
            cost_reduce.append(cost_reduce[-1])
            cost_increase.append(cost_increase[-1])
            cost_reinvest.append(cost_reinvest[-1])
            shares.append(shares[-1])
            shares_reduce.append(shares_reduce[-1])
            shares_increase.append(shares_increase[-1])
            shares_reinvest.append(shares_reinvest[-1])
    
        if stock.loc[i, '年月日'] in dividend['除息日'].tolist():    # 除息資料
            money = dividend.loc[dividend['除息日'] == stock.loc[i, '年月日'], '息值(元)']
            stock.loc[i, '除息金額'] = float(money)
            cost[-1] = cost[-1] - int(stock.loc[i, '除息金額'] * shares[-1])  #股利從成本扣除
            cost_reduce[-1] = cost_reduce[-1] - int(stock.loc[i, '除息金額'] * shares_reduce[-1])
            cost_increase[-1] = cost_increase[-1] - int(stock.loc[i, '除息金額'] * shares_increase[-1])
    
        else:
            cum_dividend.append(stock.loc[i, '除息金額'] * shares[-1] + cum_dividend[-1])
            cum_dividend_reduce.append(stock.loc[i, '除息金額'] * shares_reduce[-1] + cum_dividend_reduce[-1])
            cum_dividend_increase.append(stock.loc[i, '除息金額'] * shares_increase[-1] + cum_dividend_increase[-1])
            market_value.append(int(stock.loc[i, '收盤價(元)'] * shares[-1]))
            market_value_reduce.append(int(stock.loc[i, '收盤價(元)'] * shares_reduce[-1]))
            market_value_increase.append(int(stock.loc[i, '收盤價(元)'] * shares_increase[-1]))
            date.append(stock.loc[i, '年月日'].split('/')[0] + '-' + stock.loc[i, '年月日'].split('/')[1])
    
    
    cost.remove(0)
    cost_reduce.remove(0)
    cost_increase.remove(0)
    cost_reinvest.remove(0)
    shares.remove(0)
    shares_reduce.remove(0)
    shares_increase.remove(0)
    shares_reinvest.remove(0)
    cum_dividend.remove(0)
    cum_dividend_reduce.remove(0)
    cum_dividend_increase.remove(0)
    cum_dividend_reinvest.remove(0)
    print(cum_dividend)
    # 市值成本折線圖
    fig, ax1 = plt.subplots()
    # fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(18, 4))
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    # ax1.set_title('0050每月定額$10000，回檔20%加or減碼40%', size=16)
    ax1.set_title('0056每月定額$10000', size=16)
    ax1.set_xlabel('Date')
    for tick in ax1.get_xticklabels():
        tick.set_rotation(45)
    ax1.xaxis.set_major_locator(MultipleLocator(12))
    ax1.set_ylabel('Value')
    ax1.plot(date, market_value, label='市值(正常定期定額)', color='indianred')
    ax1.plot(date, market_value_increase, label='市值(定期定額遇到空頭加碼)', color='steelblue')
    ax1.plot(date, market_value_reduce, label='市值(定期定額遇到空頭減碼)', color='seagreen')
    ax1.bar(date, cost, color='orange', label='成本(正常定期定額)')
    ax1.bar(date, cum_dividend, bottom=cost, color='red', label='累積股利(正常定期定額)')
    ax1.legend(loc='upper left')
    ax1.grid()
    plt.tight_layout()
    # plt.savefig(r'C:\股票\figure\0050每月定額，回檔20%加減碼40%，創新高回復quota.jpg')
    # plt.savefig(r'C:\股票\figure\0056每月定額$10000.jpg')
    plt.show()
    
    # 數據群組長條圖
    fig, ax2 = plt.subplots()
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    type = ['定期定額跌深加碼40%', '正常定期定額', '定期定額跌深減碼40%']
    mv = [market_value_increase[-1], market_value[-1], market_value_reduce[-1]]
    cs = [cost_increase[-1], cost[-1], cost_reduce[-1]]
    width = 0.25
    x = np.arange(len(type))
    # fig, ax2 = plt.subplots()
    bar1 = ax2.bar(x - width/2, cs, width, label='Cost', color=['lightblue', 'sandybrown', 'lightgreen'])
    bar2 = ax2.bar(x + width/2, mv, width, label='Value', color=['steelblue', 'indianred', 'seagreen'])
    ax2.set_ylabel('Value')
    ax2.set_xticks(x)
    ax2.set_xticklabels(type)
    ax2.set_title('定期定額三種方式比較', size=16)
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax2.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 1),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
    autolabel(bar1)
    autolabel(bar2)
    ax2.grid(axis='y')
    plt.tight_layout()
    # plt.savefig(r'C:\股票\figure\0050定期定額三種方式市值、數據比較.jpg')
    fig = plt.gcf()   # 取得目前那張圖
    return fig        # 把圖當作函式回傳值
# ——— Streamlit 入口 ———
st.set_page_config(page_title="0050 每月定額回測", layout="wide")
st.title("0050 ETF 每月定額回測")

if st.button("開始跑回測"):
    chart = main()       # 執行剛才包好的函式
    st.pyplot(chart)     # 將圖鑲到網頁
    #
    #
    # 回測數據
    # data = {'date': stock['年月日'].tolist(), 'price': stock['收盤價(元)'].tolist(),
    #         'value(normal)': market_value, 'value(reduce)': market_value_reduce, 'value(increase)': market_value_increase,
#         'cost(normal)': cost, 'cost(reduce)': cost_reduce, 'cost(increase)': cost_increase}
# df = pd.DataFrame(data)
# df.to_csv(r'C:\股票\0050加減碼數據.csv', encoding='Big5', index=False)
