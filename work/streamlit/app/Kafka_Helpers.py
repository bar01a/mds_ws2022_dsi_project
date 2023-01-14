class Consumer:
    
    def __init__(self, server, port, topic_name, handler):
        import sys
        from kafka import KafkaConsumer
        import threading
        
        self.server = str(server)
        self.port = str(port)
        self.topic_name = str(topic_name)
        self.handler = handler
        # self.stop_event = stop_event
        
        self._consumer = None
        try:
            self._consumer = KafkaConsumer(self.topic_name,
                                           auto_offset_reset='latest',
                                           bootstrap_servers=f'{self.server}:{self.port}',
                                           api_version=(0, 10, 2))
            
        except Exception as ex:
            print('Exception while connecting Kafka')
            print(str(ex))
            
        self.x = threading.Thread(target=self.subscribe)
        self.x.start()
        
    def subscribe(self):
        if not self._consumer == None:
            try:
                print('Waiting for new events...')
                for event in self._consumer:
                    if not event.key == None:
                        key = event.key.decode("utf-8")
                    if not event.value == None:
                        value = event.value.decode("utf-8")
                    if not event.key == None and not event.value == None:
                        self.handler(key, value)
                self._consumer.close()
            except Exception as ex:
                print('Exception in subscribing')
                print(str(ex))
                
    # def close(self): #
        
                

class Producer:
    
    def __init__(self, server, port):
        from time import sleep
        from json import dumps
        
        self.server = str(server)
        self.port = str(port)
        
        
    def send(self, topic_name, key, value):

        from kafka import KafkaProducer
        # connect to Kafka and open producer
        self.producer = KafkaProducer(bootstrap_servers=f'{self.server}:{self.port}',
                                      api_version=(0, 10, 2),
                                      value_serializer=lambda x:x)  # dumps(x).encode('utf-8'))

        key_bytes = bytes(str(key), encoding='utf-8')
        value_bytes = bytes(str(value), encoding='utf-8')
        self.producer.send(topic_name, key=key_bytes, value=value_bytes)
        self.producer.flush()

        # close connection
        self.producer.close()
        