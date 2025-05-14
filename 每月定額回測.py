import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

pd.set_option('mode.chained_assignment', None)

# -------------------------------------------------
# 主程式：計算回測結果並回傳 Plotly 圖表
# -------------------------------------------------

def main():
    # 讀取資料（與腳本同資料夾）
    stock = pd.read_csv('0050歷史股價.csv', encoding='utf-8-sig', low_memory=False)
    dividend = pd.read_csv('0050歷史股利.csv', encoding='utf-8-sig', low_memory=False)

    # 初始化變數
    max_price = stock.loc[0, '收盤價(元)']
    cost = [0]
    cum_dividend = [0]
    shares = [0]
    market_value = []
    date = []

    month_check = int(stock.loc[0, '年月日'].split('/')[1])
    stock['除息金額'] = 0

    # 逐天模擬
    for i in range(len(stock)):
        close_i = stock.loc[i, '收盤價(元)']

        # 每月第一天投入 10,000 元
        month = int(stock.loc[i, '年月日'].split('/')[1])
        if month == month_check:
            buy_shares = int(10000 / close_i)
            shares.append(shares[-1] + buy_shares)
            cost.append(cost[-1] + int(close_i * buy_shares))
            month_check = 1 if month_check == 12 else month_check + 1
        else:
            shares.append(shares[-1])
            cost.append(cost[-1])

        # 除息
        if stock.loc[i, '年月日'] in dividend['除息日'].tolist():
            money = float(dividend.loc[dividend['除息日'] == stock.loc[i, '年月日'], '息值(元)'])
            stock.loc[i, '除息金額'] = money

        cum_dividend.append(cum_dividend[-1] + stock.loc[i, '除息金額'] * shares[-1])
        cost[-1] -= stock.loc[i, '除息金額'] * shares[-1]  # 股利抵成本

        market_value.append(int(close_i * shares[-1]))
        y, m, _ = stock.loc[i, '年月日'].split('/')
        date.append(f'{y}-{m}')

    # 移除開頭 0，並對齊長度
    cost = cost[1:]
    shares = shares[1:]
    cum_dividend = cum_dividend[1:]

    min_len = min(len(date), len(cost), len(cum_dividend), len(market_value))
    date = date[:min_len]
    cost = cost[:min_len]
    cum_dividend = cum_dividend[:min_len]
    market_value = market_value[:min_len]

    # -------------------- Plotly 畫圖 --------------------
    fig = go.Figure()
    # 堆疊柱狀圖：成本 + 股利
    fig.add_trace(go.Bar(x=date, y=cost, name='成本', marker_color='orange'))
    fig.add_trace(go.Bar(x=date, y=cum_dividend, name='累積股利', marker_color='red'))
    # 市值折線圖
    fig.add_trace(go.Scatter(x=date, y=market_value, name='市值', mode='lines', line=dict(color='indianred')))

    fig.update_layout(
        title='0050 每月定額回測 $10,000 回測',
        xaxis_title='Date',
        yaxis_title='Value (NTD)',
        barmode='stack',
        bargap=0,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified',
        margin=dict(l=40, r=40, t=80, b=40)
    )

    return fig

# -------------------------------------------------
# Streamlit 入口
# -------------------------------------------------

st.set_page_config(page_title='0050 每月定額回測', layout='wide')
st.title('0050 ETF 每月定額回測')

if st.button('開始跑回測'):
    st.plotly_chart(main(), use_container_width=True)
