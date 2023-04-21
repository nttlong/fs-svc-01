import cy_kit
import cyx.common.brokers
import datetime
import json
settings = cy_kit.singleton(cyx.common.brokers.Settings)
print(settings.is_use)
print(settings.servers)
print(settings.temp_directory)
import cy_docs

from confluent_kafka import Producer

p = Producer({'bootstrap.servers': '172.16.7.91:30992'})
for i in range(0,100000):
    data = dict(
        code=f"message {i}"
    )
    txt_json = json.dumps(data)
    print(txt_json.encode('utf-8'))
    fx =p.produce('files.new', txt_json.encode('utf-8'))
    print(fx)
print("xong")