'use strict';

console.log('Hello world');
var Connection = require('rabbitmq-client')
const delay = ms => new Promise(resolve => setTimeout(resolve, ms))


var doConnect = async (count,requestCount) => {
    while (true) {
        for (var i = 0; i < count; i++) {
            var rabbit = new Connection.Connection({
                url: 'amqp://guest:guest@172.16.7.91:30672',
                // wait 1 to 30 seconds between connection retries
                retryLow: 100,
                retryHigh: 300,
            })

            rabbit.on('error', (err) => {
                // connection refused, etc
                console.error(err)
            })

            rabbit.on('connection', () => {
                console.log('The connection is successfully (re)established')

            })

            var test = async () => {
                var ch = await rabbit.acquire()
                ch.on('close', () => {
                    console.log('channel was closed')
                });
                await ch.queueDeclare({ queue: 'my-queue', exclusive: true });
                var data = { title: 'just some object' }
                await ch.basicPublish({ routingKey: 'my-queue' }, data);
                console.log("Send message")
            }
            for (var x = 0; x < requestCount; x++) {
                test().then();
            }
        }
        console.log("xong");
        await delay(1000);
    }
}
//const rabbit = new Connection.Connection({
//    url: 'amqp://guest:guest@172.16.7.91:30672',
//    // wait 1 to 30 seconds between connection retries
//    retryLow: 1000,
//    retryHigh: 30000,
//})



//async function run() {
//    // will wait for the connection to establish before creating a Channel
//    const ch = await rabbit.acquire()

//    // channels can emit some events too
//    ch.on('close', () => {
//        console.log('channel was closed')
//    })

//    // create a queue for the duration of this connection
//    await ch.queueDeclare({ queue: 'my-queue', exclusive: true })

//    const data = { title: 'just some object' }

//    // resolves when the data has been flushed through the socket
//    // or if ch.confirmSelect() was called, will wait for an acknowledgement
//    await ch.basicPublish({ routingKey: 'my-queue' }, data)

//    // consume messages until cancelled or until the channel is closed
//    await ch.basicConsume({ queue: 'my-queue' }, (msg) => {
//        console.log(msg)
//        // acknowledge receipt of the message
//        ch.basicAck({ deliveryTag: msg.deliveryTag })
//    })

//    // It's your responsibility to close any acquired channels
//    await ch.close()

//    // Don't forget to end the connection
//    await rabbit.close()
//}

//run()
doConnect(5000,1000)
'{"isJson":true,"service":"Auth","assemblyName":"ERM.Business.AD","className":"UsersBusiness","methodName":"LoginAsync","mutiTenant":true,"msgBodyData":["WcglUHNBCHHp+9txNG0saA==","kenFCA3U/0zZn8O0Kr/QGg==","","AIzaSyC1SKqppxpxwT7i3qEdUjJjn-J_SMoUBic"],"saas":0,"tenant":"default"}'
'{"isJson":true,"service":"SYS","assemblyName":"Core","className":"CMBusiness","methodName":"GetCacheAsync","mutiTenant":true,"msgBodyData":["TranslateLabel","Comments"],"saas":0,"userID":"CODXADMIN","tenant":"default","functionID":"WP"}'
http://172.16.7.240/api/SYS/exec14
loadtest -n 100000 -c 10000 -k http://172.16.7.91
loadtest -c 1000 --rps 1000 http://172.16.7.91/default/wp/portal/WP
loadtest -P '{"isJson":true,"service":"SYS","assemblyName":"Core","className":"CMBusiness","methodName":"GetCacheAsync","mutiTenant":true,"msgBodyData":["TranslateLabel","Comments"],"saas":0,"userID":"CODXADMIN","tenant":"default","functionID":"WP"}' -n 1000 -c 100 --rps 2000 -T 'application/json' 'http://172.16.7.240/api/SYS/exec39'
loadtest -P '{"isJson":true,"service":"Auth","assemblyName":"ERM.Business.AD","className":"UsersBusiness","methodName":"LoginAsync","mutiTenant":true,"msgBodyData":["WcglUHNBCHHp+9txNG0saA==","kenFCA3U/0zZn8O0Kr/QGg==","","AIzaSyC1SKqppxpxwT7i3qEdUjJjn-J_SMoUBic"],"saas":0,"tenant":"default"}' -n 100000 -c 1000 --rps 2000 -T 'application/json' http://172.16.7.240/api/Auth/exec66
