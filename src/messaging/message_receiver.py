from .pika_client import PikaClient

class MessageReceiver(PikaClient):

    def get_message(self, queue):
        method_frame, header_frame, body = self.channel.basic_get(queue)
        if method_frame:
            print(method_frame, header_frame, body)
            self.channel.basic_ack(method_frame.delivery_tag)
            return method_frame, header_frame, body
        else:
            print("No message returned")

    def close(self):
        self.channel.close()
        self.connection.close()
