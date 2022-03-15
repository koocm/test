import time
import pyupbit
import datetime

access = "QcY0uZHjVxywQfNWxrR1AB7CveJXnUsNsmx5Yfkv"
secret = "qpER0QpyZ41xedxCWZFfPmTLHgj3IJOS0dtkE76W"
upbit = pyupbit.Upbit(access, secret)
balances = upbit.get_balances()

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

# 기본 세팅
while True:
    try:
        # print('01')
        now = datetime.datetime.now()
        interval = 'minute10'
        count = 100
        start_time = get_start_time("KRW-XRP")
        end_time = start_time + datetime.timedelta(minutes=10)
        df=pyupbit.get_ohlcv(ticker="KRW-XRP",interval=interval,to=now,count=count)
        
        # 이동평균갑 확인 및 데이터 추가
        # print('02')
        for i in [10,20,30,40,50,60,70,80]:
            df[i]=df['close'].rolling(window=i).mean()
            
        # 현재 값이 모든 이동평균값보다 높은지 불린 값으로 리스트에 저장
        # print('03')
        list=[]      
        for i in [10,20,30,40,50,60,70,80]:
            list.append(df['close'][-1]>df[i][-1])
            
        # 현재 이동편균값이 현재가의 !% 범위 이내에 모여있는지 확인
        # print('04')
        list1=df.iloc[99,6:17]
        min=list1.min()
        max=list1.max()
        diff=list1.max()-list1.min()
        ratio=diff/max
        # print('05')
        # 위 두가지 조건을 만족하면 매수
        if (all(list) == True) & (ratio < 0.015) :
            krw = get_balance("KRW")
            if krw > 20000:
                upbit.buy_market_order("KRW-XRP", 20000)
                print(datetime.datetime.now(),"매수")
        # print("ratio:",ratio)
        # print(all(list) == True)
        # print('06')
        # 수익률 1.5% 발생시 50% 매도
        if upbit.get_balance('XRP') > 20 :
            if float(upbit.get_balances()[1]['avg_buy_price']) > ((pyupbit.get_current_price(["KRW-XRP"]))*1.04) :
                upbit.sell_market_order("KRW-XRP",10)
                print(datetime.datetime.now(),"매도")
        time.sleep(30)
    
    except Exception as e:
        print(e)
        time.sleep(1)