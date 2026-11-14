
import argparse
import json

import pika


EXCHANGE = "rapido-dispatch"


def main():
    parser = argparse.ArgumentParser(
        description="Rapido driver RabbitMQ consumer"
    )
    parser.add_argument("name", help="Driver name")
    parser.add_argument(
        "pattern",
        help="Topic binding pattern, e.g. bangalore.koramangala.*",
    )
    args = parser.parse_args()

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="topic",
        durable=True,
    )

    # Create a private queue for this driver instance.
    result = channel.queue_declare(
        queue="",
        exclusive=True,
    )
    queue_name = result.method.queue

    channel.queue_bind(
        exchange=EXCHANGE,
        queue=queue_name,
        routing_key=args.pattern,
    )

    channel.basic_qos(prefetch_count=1)

    print(f"Driver: {args.name}")
    print(f"Binding: {args.pattern}")
    print(f"Private queue: {queue_name}")
    print("Waiting for requests. Press Ctrl+C to stop.\n")

    def callback(ch, method, properties, body):
        try:
            request = json.loads(body)

            if not isinstance(request, dict):
                raise ValueError("Request must be a JSON object")

            required_fields = (
                "id",
                "city",
                "zone",
                "type",
                "ts",
            )

            missing_fields = [
                field
                for field in required_fields
                if field not in request
            ]

            if missing_fields:
                raise ValueError(
                    f"Missing required fields: {missing_fields}"
                )

            print(
                f"[{args.name}] RECEIVED "
                f"key={method.routing_key} "
                f"id={request['id']} "
                f"city={request['city']} "
                f"zone={request['zone']} "
                f"type={request['type']} "
                f"ts={request['ts']}",
                flush=True,
            )

            # Valid message: acknowledge successful processing.
            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )

        except (json.JSONDecodeError, ValueError) as error:
            print(
                f"[{args.name}] REJECTED "
                f"key={method.routing_key}: {error}",
                flush=True,
            )

            # Malformed message: reject without requeueing.
            ch.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False,
            )

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=False,
    )

    try:
        channel.start_consuming()

    except KeyboardInterrupt:
        print(f"\nDriver {args.name} stopped.")

    finally:
        if channel.is_open:
            channel.stop_consuming()
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()
