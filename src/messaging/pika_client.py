import os
import ssl
import pika

class PikaClient:
    def __init__(self):

        # SSL Context for TLS configuration of Amazon MQ for RabbitMQ
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.set_ciphers("ECDHE+AESGCM:!ECDSA")

        mode = os.getenv('mode')
        print('MODE: ', mode)

        rabbit_broker_id = os.getenv("rabbitmq_broker_id")
        rabbit_user = os.getenv("rabbitmq_user")
        rabbit_password = os.getenv("rabbitmq_password")
        rabbit_region = os.getenv("rabbitmq_region")

        url = (
            "amqp://localhost:5672"
            if mode != "prod"
            else f"amqps://{rabbit_user}:{rabbit_password}@{rabbit_broker_id}.mq.{rabbit_region}.amazonaws.com:5671"
        )

        parameters = pika.URLParameters(url)
        
        if mode == "prod":
            print('CONFIGURING SSL')
            parameters.ssl_options = pika.SSLOptions(context=ssl_context)

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
