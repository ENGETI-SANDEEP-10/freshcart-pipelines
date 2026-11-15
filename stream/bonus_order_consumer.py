
import json
import os
import time
from pathlib import Path

import pika


EXCHANGE = "rapido-dispatch"
QUEUE = "freshcart-bonus-orders"
ROUTING_KEY = "freshcart.orders.web"
COLLECTION_SECONDS = 60

OUTPUT_FILE = Path("bonus_data/freshcart_orders.json")

REQUIRED_FIELDS = {
    "order_id",
    "cust_email",
    "cust_name",
    "order_date",
    "amount",
    "currency",
    "pincode",
    "updated_at",
}


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.environ.get("RABBITMQ_HOST", "localhost")
        )
    )

    channel = connection.channel()

    try:
        channel.exchange_declare(
            exchange=EXCHANGE,
            exchange_type="topic",
            durable=True,
        )

        channel.queue_declare(
            queue=QUEUE,
            durable=True,
        )

        channel.queue_bind(
            queue=QUEUE,
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY,
        )

        orders = []
        delivery_tags = []

        print("Connected to RabbitMQ")
        print(f"Queue: {QUEUE}")
        print(f"Binding: {ROUTING_KEY}")
        print("READY - Start the publisher in another terminal.")
        print("Collecting for 60 seconds...", flush=True)

        deadline = time.monotonic() + COLLECTION_SECONDS

        while time.monotonic() < deadline:
            method, properties, body = channel.basic_get(
                queue=QUEUE,
                auto_ack=False,
            )

            if method is None:
                connection.process_data_events(time_limit=0)
                time.sleep(0.25)
                continue

            try:
                order = json.loads(body.decode("utf-8"))

                if not isinstance(order, dict):
                    raise ValueError("Expected JSON object")

                if not REQUIRED_FIELDS.issubset(order):
                    raise ValueError("Missing required order fields")

            except (ValueError, UnicodeDecodeError) as error:
                print(f"Rejected invalid message: {error}")
                channel.basic_nack(
                    delivery_tag=method.delivery_tag,
                    requeue=False,
                )
                continue

            orders.append(order)
            delivery_tags.append(method.delivery_tag)

            print(
                f"Received {len(orders)}: {order['order_id']}",
                flush=True,
            )

        if orders:
            OUTPUT_FILE.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            # Save the batch before acknowledging the messages.
            with OUTPUT_FILE.open("w", encoding="utf-8") as file:
                json.dump(orders, file, indent=2)
                file.flush()
                os.fsync(file.fileno())

            for tag in delivery_tags:
                channel.basic_ack(delivery_tag=tag)

            print(f"Saved file: {OUTPUT_FILE}")
        else:
            print("No orders received. No file created.")

        print(f"Total orders collected: {len(orders)}")
        print("Consumer finished.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
