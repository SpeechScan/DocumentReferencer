import os
from .messaging import MessageReceiver

if __name__ == "__main__":
    rabbit_broker_id = os.getenv("rabbitmq_broker_id")
    rabbit_user = os.getenv("rabbitmq_user")
    rabbit_password = os.getenv("rabbitmq_password")
    rabbit_region = os.getenv("rabbitmq_region")

    # Create Basic Message Receiver which creates a connection
    # and channel for consuming messages.
    basic_message_receiver = MessageReceiver(
        rabbit_broker_id, rabbit_user, rabbit_password, rabbit_region
    )

    # Consume the message that was sent.
    basic_message_receiver.get_message("hello world queue")

    # Close connections.
    basic_message_receiver.close()
