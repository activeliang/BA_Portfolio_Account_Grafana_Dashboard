# from influxdb import InfluxDBClient


# # 从环境变量中获取用户名和密码
# import os


# # 连接 InfluxDB
# client = InfluxDBClient(host='influxdb', port=8086, username=f"{influxdb_user}", password=f"{influxdb_password}")

# # client = InfluxDBClient(url="http://influxdb:8086", token=f"{influxdb_user}:{influxdb_password}", org=f"{influxdb_db}")
# client.switch_database(f"{influxdb_db}")
# # write_api = client.write_api(write_options=WriteOptions(batch_size=500, flush_interval=10_000, jitter_interval=2_000, retry_interval=5_000))






from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import contextlib

import os
influxdb_auth_token = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
influxdb_org = os.getenv("DOCKER_INFLUXDB_INIT_ORG")
influxdb_bucket = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET")
influxdb_user = os.getenv("DOCKER_INFLUXDB_INIT_USERNAME")
influxdb_password = os.getenv("DOCKER_INFLUXDB_INIT_PASSWORD")

@contextlib.contextmanager
def influxdb_client():
    client = InfluxDBClient(url="http://influxdb:8086", username=influxdb_user, password=influxdb_password, token=influxdb_auth_token, org=influxdb_org)
    write_api = client.write_api(write_options=SYNCHRONOUS, default_bucket=influxdb_bucket)
    query_api = client.query_api()
    try:
        yield query_api, write_api, Point
    finally:
        write_api.close()
        client.close()