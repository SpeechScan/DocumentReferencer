from .pika_client import PikaClient

class MessageReceiver(PikaClient):
    def add_handler(self, queue, callback):
        self.channel.queue_declare(queue=queue)
        self.channel.basic_consume(
            queue=queue, on_message_callback=callback, auto_ack=True
        )

    def start_listening(self):
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()

    def close(self):
        self.channel.close()
        self.connection.close()
