import os
from .messaging import MessageReceiver
from .services import DocumentService


def add_rabbitmq_handler(message_receiver, queue, callback):
    message_receiver.add_handler(
        queue,
        lambda ch, method, properties, body: callback(body),
    )


def rabbitmq_start_listening():
    rabbit_broker_id = os.getenv("rabbitmq_broker_id")
    rabbit_user = os.getenv("rabbitmq_user")
    rabbit_password = os.getenv("rabbitmq_password")
    rabbit_region = os.getenv("rabbitmq_region")

    message_receiver = MessageReceiver(
        rabbit_broker_id, rabbit_user, rabbit_password, rabbit_region
    )
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
