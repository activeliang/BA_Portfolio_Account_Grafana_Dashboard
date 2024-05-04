from config import accounts
import ccxt
from db import influxdb_client
from logger import logger
import time
from datetime import datetime, timedelta
import os


bucket = 'mybucket'

def printEnv():
    # 获取所有环境变量
    env_vars = os.environ

    # 打印环境变量的键和值
    for key, value in env_vars.items():
        print(f"{key}: {value}")

def getAccountUid(exchange):
    checksum = exchange.options['checksum']
    # 查询是否存在相同 checksum 的记录
    query = f'from(bucket: "{bucket}") |> range(start: -1y) |> filter(fn: (r) => r._measurement == "account" and r._field == "uid" and r.checksum == "{checksum}")'
    with influxdb_client() as (query_api, write_api, Point):
        result = query_api.query(query=query)
        points = result
        for table in points:
            for record in table.records:
                return record.get_value()
        logger.info(f"No uid record found, obtaining uid... checksum:{checksum}")
        # 如果不存在相同 checksum 的记录，则执行函数 B 获取 uid
        uid = exchange.private_get_account()['uid']
        # 保存记录
        data = [
            {
                "measurement": "account",
                "tags": {
                    "checksum": checksum
                },
                "fields": {
                    "uid": uid
                }
            }
        ]
        write_api.write(bucket=bucket, record=data)
        logger.info(f"Record saved successfully: uid={uid}, checksum={checksum}")
        # 等待一段时间以确保数据写入完成
        return uid

def render_exchange(account):
    return ccxt.binance({
        'apiKey': account['apiKey'],
        'secret': account['secret'],
        'timeout': 30000,
        'rateLimit': 10,
        'enableRateLimit': False,
        'options': {
            'adjustForTimeDifference': True,  # ←---- resolves the timestamp
            'recvWindow': 10000,
            'portfolioMargin': True,
            'checksum': f"{account['apiKey'][-10:]}{account['secret'][-10:]}"
        },
    })

def fetch_data(account):
    exchange = render_exchange(account)
    balance = exchange.papi_get_account()['actualEquity']
    # 减去5分钟
    minutes_6_ago = int((datetime.now() - timedelta(minutes=600)).timestamp())*1000
    f_income_list = exchange.papi_get_um_income({ 'incomeType': 'COMMISSION', 'limit': 1000, 'startTime': minutes_6_ago })
    f_last_order_time = int(f_income_list[-1]['time'])*1000000 if f_income_list else None

    d_income_list = exchange.papi_get_cm_income({ 'incomeType': 'COMMISSION', 'limit': 1000, 'startTime': minutes_6_ago })
    d_last_order_time = int(d_income_list[-1]['time'])*1000000 if d_income_list else None
    
    s_income_list = exchange.sapi_get_margin_capital_flow({ 'type': 'TRADING_COMMISSION', 'limit': 1000, 'startTime': minutes_6_ago })
    s_last_order_time = int(s_income_list[-1]['timestamp'])*1000000 if s_income_list else None
    json_body = [
        {
            "measurement": "account_metrics",
            "tags": {
                "account_name": account['remark'],
                "account_id": getAccountUid(exchange),
            },
            "time": time.time_ns(),
            "fields": {
                "active": 'true',
                "balance": float(balance),
                "f_last_order_time": f_last_order_time,
                "d_last_order_time": d_last_order_time,
                "s_last_order_time": s_last_order_time,
            }
        }
    ]
    print(json_body)
    with influxdb_client() as (query_api, write_api, Point):
        write_api.write(bucket=bucket, record=json_body)

def write_active_account_ids():
    account_ids = [getAccountUid(render_exchange(account)) for account in accounts]
    print(account_ids)
    with influxdb_client() as (query_api, write_api, Point):
        point = Point("account_ids").tag("type", "active").field("active_ids", '-'.join(account_ids))
        write_api.write(bucket=bucket, record=point)


def main():
    # printEnv()
    account = accounts[0]
    for account in accounts:
        logger.info(f"正在处理:{account['remark']}")
        fetch_data(account)
    write_active_account_ids()

if __name__ == "__main__":
    main()
