
import json
import random
import time
from datetime import datetime, timezone
from uuid import uuid4

import pika


EXCHANGE = "rapido-dispatch"

CITY_ZONES = {
    "bangalore": ["koramangala", "indiranagar", "whitefield"],
    "chennai": ["tnagar", "whitefield"],
}

REQUEST_TYPES = ["ride", "food"]


def create_request():
    city = random.choice(list(CITY_ZONES.keys()))
    zone = random.choice(CITY_ZONES[city])
    request_type = random.choice(REQUEST_TYPES)

    request = {
        "id": str(uuid4()),
        "city": city,
        "zone": zone,
        "type": request_type,
        "ts": datetime.now(timezone.utc).isoformat(),
    }

    routing_key = f"{city}.{zone}.{request_type}"
    return request, routing_key


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="topic",
        durable=True,
    )

    print("Dispatcher connected to RabbitMQ.")
    print(f"Publishing to exchange: {EXCHANGE}")
    print("Every 10th message will omit the zone field.")
    print("Press Ctrl+C to stop.\n")

    count = 0

    try:
        while True:
            request, routing_key = create_request()
            count += 1

            # D3: Deliberately omit zone every 10th message.
            # Keep the routing key valid so matching drivers
            # can receive and reject the malformed payload.
            if count % 10 == 0:
                del request["zone"]
                status = "MALFORMED"
            else:
                status = "VALID"

            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=routing_key,
                body=json.dumps(request),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                ),
            )

            print(
                f"[{count}] {status} Published "
                f"{routing_key}: {json.dumps(request)}",
                flush=True,
            )

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nDispatcher stopped.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
