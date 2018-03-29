import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json
import threading

'''

Dai che divento il capo dei websockets

'''

class my_websocket():

    def __init__(self, channel, pair):

        self.bid = []
        self.ask = []
        self.t_stamp = ''
        
        #Initialize subscribtion data
        self.channel = channel
        self.pair = pair

        self.ws = websocket.WebSocketApp("wss://www.bitmex.com/realtime/",
                                        on_message = self.on_message,
                                        on_error = self.on_error,
                                        on_close = self.on_close)


        self.ws.on_open = self.on_open
        
        



    def get_data(self):

        return self.t_stamp, self.bid, self.ask
    


    def process_data(self, msg):

        try:
            
            bids = msg['data'][0]['bids']#[0][0]
            asks = msg['data'][0]['asks']#[0][0]

            t_stamp = msg['data'][0]['timestamp']

        except:

            print 'Exception happened'
            return 0

        self.bid = bids
        self.ask = asks

        self.t_stamp = t_stamp

        return 0



    def subscribe(self, ws):

        ws.send(json.dumps({
        "op": "subscribe",
        "args": [self.channel + ':' + self.pair]#["orderBook10:XBTUSD"]
        }))

        print('\nSubscribed!\n')
        time.sleep(10)


    def on_message(self, ws, message):
        message_readable = json.loads(message)

        self.process_data(message_readable)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        def run(*args):
            for i in range(3):
                time.sleep(1)
                ws.send("Hello %d" % i)
            time.sleep(1)
            print('\nWebsocket Ready..\n')

        self.subscribe(self.ws)


    def run_forever(self):

        self.ws.run_forever()



#if __name__ == "__main__":
#
#    websocket.enableTrace(True)
#
#    my_socket = my_websocket('orderBook10', 'XBTUSD')
#
#    wst = threading.Thread(target=my_socket.run_forever)
#    wst.daemon = True
#    wst.start()
#
#    time.sleep(10)
#    
#    while True:
#
#        print(my_socket.get_data())
#        time.sleep(1)
#
#    my_socket.ws.close()
