from .messaging import MessageReceiver
from .services import DocumentService


def add_rabbitmq_handler(message_receiver, queue, callback):
    message_receiver.add_handler(
        queue,
        lambda ch, method, properties, body: callback(body),
    )

def rabbitmq_start_listening():
    message_receiver = MessageReceiver()
    document_service = DocumentService()

    add_rabbitmq_handler(
        message_receiver,
        "inconsistencies",
        lambda body: document_service.find_inconcistency(body.decode('utf-8')),
    )

    message_receiver.start_listening()
    message_receiver.close()


if __name__ == "__main__":
    rabbitmq_start_listening()
