# Part D — RabbitMQ Event Streaming

## D1. Topic Routing Predictions

RabbitMQ uses a topic exchange named `rapido-dispatch`. Messages are published with routing keys in the format `city.zone.type`.

The driver binding patterns are:

| Driver | Binding pattern |
|---|---|
| Ravi | `bangalore.koramangala.*` |
| Priya | `bangalore.indiranagar.*` |
| Arjun | `bangalore.*.ride` |
| Meena | `bangalore.*.food` |
| Karthik | `chennai.tnagar.food` |
| Control | `bangalore.#` |

Before executing the dispatcher, the following routing predictions were recorded.

| No. | Routing key | Predicted receiving queues |
|---|---|---|
| 1 | `bangalore.koramangala.food` | Ravi, Meena, Control |
| 2 | `bangalore.indiranagar.ride` | Priya, Arjun, Control |
| 3 | `bangalore.whitefield.ride` | Arjun, Control |
| 4 | `chennai.tnagar.food` | Karthik |
| 5 | `chennai.whitefield.ride` | Dropped (no matching binding) |
| 6 | `bangalore.koramangala` | Control only |

The `*` wildcard matches exactly one routing-key word, whereas `#` matches zero or more words. Question 6 has only two words. Ravi's binding requires a third word after `bangalore.koramangala`, so it does not match. Priya, Arjun, Meena, and Karthik also do not match. Only `bangalore.#` matches because `#` can cover the remaining `koramangala` word.

These predictions were recorded before running the RabbitMQ programs.

**Evidence:** `D1_Routing_Predictions_Before_Run.png`.

## D2. Dispatcher and Driver Implementation

Two Python scripts were created using the Pika library:

- `stream/dispatcher.py` publishes JSON messages every two seconds.
- `stream/driver.py` accepts a driver name and binding pattern, creates a private RabbitMQ queue, binds it to the exchange, and consumes matching messages.

The exchange is declared as a **durable topic exchange**, and the dispatcher publishes persistent messages.

Following the final schema correction, each valid message contains:

```json
{
  "id": "unique-request-id",
  "city": "bangalore",
  "zone": "koramangala",
  "type": "ride",
  "ts": "UTC timestamp"
}
```

Three consumers were started simultaneously:

| Driver | Binding |
|---|---|
| Ravi | `bangalore.koramangala.*` |
| Priya | `bangalore.indiranagar.*` |
| Arjun | `bangalore.*.ride` |

The dispatcher was run for more than the required two minutes. Its recorded run published 202 requests over approximately 6 minutes and 43 seconds.

Observed routing examples:

| Routing key | Drivers observed receiving |
|---|---|
| `bangalore.koramangala.food` | Ravi |
| `bangalore.indiranagar.ride` | Priya and Arjun |
| `bangalore.whitefield.ride` | Arjun |
| `bangalore.koramangala.ride` | Ravi and Arjun |

For example, request `17d3091a-ecc2-4f52-adf8-07e271623601` appeared in both Ravi's and Arjun's logs. This demonstrates that RabbitMQ copies a published message to each queue with a matching binding.

Only Ravi, Priya, and Arjun were active in this three-driver experiment. Therefore, the D1 recipients Meena, Karthik, and Control remain routing predictions rather than directly observed deliveries in this run.

**Evidence:** `D2_Dispatcher_Publishing.png` and screenshots in `D2_Three_Drivers_Receiving/`.

## D3. ACK, NACK, and Malformed Messages

The dispatcher was modified so that every tenth message deliberately omits the `zone` field from its JSON body. Its routing key remains valid, allowing RabbitMQ to deliver the malformed message to a matching consumer.

The driver validates the required fields: `id`, `city`, `zone`, `type`, and `ts`.

For valid messages, the driver calls:

```python
ch.basic_ack(delivery_tag=method.delivery_tag)
```

For malformed messages, it calls:

```python
ch.basic_nack(
    delivery_tag=method.delivery_tag,
    requeue=False,
)
```

The experiment showed normal `RECEIVED` output for valid messages and `REJECTED` output for a malformed message with the error:

`Missing required fields: ['zone']`

An additional regression test used a temporary consumer with binding `#`, which receives requests from both Bangalore and Chennai. This verified the updated field names and the malformed-message rejection path.

### What Happens if a Driver Crashes Before ACK?

When a consumer connection closes before a message is acknowledged, RabbitMQ normally makes its unacknowledged message available for redelivery. Another consumer may then process that message. Applications should tolerate possible duplicate processing because a message can be delivered more than once.

### What Happens With `requeue=True` for a Poison Message?

A poison message is one that consistently fails validation or processing. If it is repeatedly rejected with `requeue=True`, RabbitMQ can continually redeliver it, producing a requeue loop and unnecessary processing.

Using `requeue=False` prevents the rejected message from being returned to its queue. Without a configured dead-letter mechanism, RabbitMQ discards it. In a production system, a dead-letter queue would help preserve rejected messages for investigation.

## Conclusion

The RabbitMQ experiments demonstrated topic-based routing, independent driver queues, overlapping subscriptions, and explicit acknowledgement handling. The updated scripts also use the JSON field names specified in the assignment.

**Evidence:** `D3_Malformed_Dispatcher.png`, `D3_Driver_NACK.png`, `D3_Updated_Schema_Dispatcher.png`, and `D3_Updated_Schema_Driver.png`.