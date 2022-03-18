import time
import pyupbit
import datetime
import numpy as np

access = "QcY0uZHjVxywQfNWxrR1AB7CveJXnUsNsmx5Yfkv"
secret = "qpER0QpyZ41xedxCWZFfPmTLHgj3IJOS0dtkE76W"
upbit = pyupbit.Upbit(access, secret)
balances = upbit.get_balances()

# total

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval='minute10', count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

items=pyupbit.get_tickers(fiat="KRW")
# items=["KRW-WAVES","KRW-MFT","KRW-XRP", "KRW-SAND", "KRW-FLOW", "KRW-MANA", "KRW-SOL","KRW-STRK","KRW-MBL","KRW-BAT"]

# 기본 세팅
while True:
    try:
        for item in items:    
            #print('01')
            now = datetime.datetime.now()
            interval = 'minute10'
            count = 100
            start_time = get_start_time(item)
            end_time = start_time + datetime.timedelta(minutes=10)
            df=pyupbit.get_ohlcv(ticker=item,interval=interval,to=now,count=count)
        
            # 이동평균갑 확인 및 데이터 추가
            # print('02')
            for i in [10,20,30,40,50,60,70,80,90,100]:
                df[i]=df['close'].rolling(window=i).mean()
            
            # 현재 값이 모든 이동평균값보다 높은지 불린 값으로 리스트에 저장
            # print('03')
            list=[]      
            for i in [10,20,30,40,50,60,70,80,90,100]:
                list.append(df['close'][-1]>df[i][-1])
            
            # 현재 이동편균값이 현재가의 !% 범위 이내에 모여있는지 확인
            # print('04')
            list1=df.iloc[99,6:17]
            min=list1.min()
            max=list1.max()
            diff=list1.max()-list1.min()
            ratio=diff/max
            # print('05')
            
            # 종목별 잔고 확인
            bal = upbit.get_balance(item) ## 잔고수량
            buy_pr = upbit.get_avg_buy_price(item)  ## 평균구매금액
            item_bal = bal * buy_pr ## 잔고금액
            # print("종목:",item,"잔고량:",bal,"평균매수금액:",buy_pr,"현재가:",(pyupbit.get_current_price([item])), "이동평균선:",(all(list) == True),"ratio:",ratio)
           
            # 세가지 조건을 만족하면 매수
            if (all(list) == True) & (ratio < 0.008) & ((np.mean(df['volume'][94:99])) > (np.mean(df['volume'])*1.2)) :
                krw = get_balance(item)
                # print(krw)
                if item_bal < 50000 :
                    # print(round(item_bal))
                    # print((upbit.get_balances()[0]['balance']))
                    if round(float(upbit.get_balances()[0]['balance'])) > 20000 :
                        # print(upbit.get_balances()[0]['balance'])
                        upbit.buy_market_order(item, 20000)
                        print(datetime.datetime.now(),item,"매수")
                        print("종목:",item,"ratio:",(ratio < 0.008),"돌파:",(all(list) == True), "거래량비:", (np.mean(df['volume'][94:99])) / (np.mean(df['volume'])))
            
            # print("종목:",item,"ratio:",(ratio < 0.008),"돌파:",(all(list) == True), "거래량비:", (np.mean(df['volume'][94:99])) / (np.mean(df['volume'])))
            # print('06')
            
            # 수익률 1.5% 발생시 50% 매도
            if item_bal > 10000 :
                sell_data = round(10000 / (pyupbit.get_current_price([item])),2)
                if float(buy_pr)*1.015 < (pyupbit.get_current_price([item])) :
                    upbit.sell_market_order(item,sell_data)
                    print(datetime.datetime.now(),item,"매도")
                    time.sleep(5)
            time.sleep(2)
            # print(now)
    
    except Exception as e:
        print(e)
        time.sleep(1)