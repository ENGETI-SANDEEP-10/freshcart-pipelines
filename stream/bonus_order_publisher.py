
import json
import os
import time

import pika


EXCHANGE = "rapido-dispatch"
ROUTING_KEY = "freshcart.orders.web"
TOTAL_ORDERS = 30


def create_order(number):
    """Create a valid, repeatable FreshCart web order."""
    return {
        "order_id": f"ORD-BONUS-{number:03d}",
        "cust_email": "priya.r@gmail.com",
        "cust_name": "Priya R",
        "order_date": "2026-09-03",
        "amount": "100.00",
        "currency": "INR",
        "pincode": "600041",
        "updated_at": (
            f"2026-09-03 12:{number:02d}:00"
        ),
    }


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.environ.get(
                "RABBITMQ_HOST", "localhost"
            )
        )
    )

    try:
        channel = connection.channel()

        channel.exchange_declare(
            exchange=EXCHANGE,
            exchange_type="topic",
            durable=True,
        )

        print("Connected to RabbitMQ")
        print(f"Exchange: {EXCHANGE}")
        print(f"Routing key: {ROUTING_KEY}")
        print(f"Orders to publish: {TOTAL_ORDERS}")

        for number in range(1, TOTAL_ORDERS + 1):
            order = create_order(number)

            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=ROUTING_KEY,
                body=json.dumps(order),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                ),
            )

            print(
                f"[{number}/{TOTAL_ORDERS}] "
                f"Published {order['order_id']}",
                flush=True,
            )

            if number < TOTAL_ORDERS:
                time.sleep(1)

        print("All 30 bonus orders published.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
