import shutil

from confluent_kafka import Producer

p = Producer({'bootstrap.servers': '172.16.7.91:30992'})
p.produce('topic-002', "Chi la test dasdas dasdasd dasdasd".encode('utf-8'))
import cy_kit
from confluent_kafka import Consumer
c = Consumer({
    'bootstrap.servers': '172.16.7.91:30992',
    'group.id': 'mygroup'
})

c.subscribe(['topic-002'])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))
#10.244.33.243:9092 10.244.33.243
c.close()