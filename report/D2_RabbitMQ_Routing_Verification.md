# D2 — RabbitMQ Topic Routing Verification

## Experiment Setup

- **Exchange:** `rapido-dispatch`
- **Exchange type:** Topic
- **Exchange durability:** Durable
- **Producer:** `stream/dispatcher.py`
- **Consumer:** `stream/driver.py`
- **Message format:** JSON
- **Publishing interval:** Approximately 2 seconds

Three driver consumers were started before the dispatcher, each with a separate, exclusive RabbitMQ queue.

| Driver | Topic binding |
|---|---|
| Ravi | `bangalore.koramangala.*` |
| Priya | `bangalore.indiranagar.*` |
| Arjun | `bangalore.*.ride` |

## Execution Results

The dispatcher published **202 requests** between approximately **07:26:06 UTC and 07:32:49 UTC on 14 November 2026**, giving a publishing duration of approximately **6 minutes and 43 seconds**.

This exceeds the required minimum execution duration of two minutes.

## Routing Verification

| Published routing key | Observed matching drivers | Interpretation |
|---|---|---|
| `bangalore.koramangala.food` | Ravi | Zone-specific binding matches the request |
| `bangalore.indiranagar.ride` | Priya, Arjun | Both location-specific and ride-specific bindings match |
| `bangalore.whitefield.ride` | Arjun | Ride wildcard matches any single Bangalore zone |
| `bangalore.koramangala.ride` | Ravi, Arjun | One event can be delivered to multiple matching queues |

An example of overlapping routing was request ID `17d3091a-ecc2-4f52-adf8-07e271623601`, which appeared in both Ravi's and Arjun's consumer logs.

## Observations

RabbitMQ distributed published messages according to each queue's topic binding. The `*` wildcard matched exactly one routing-key segment. Separate driver queues allowed the same request to be received by multiple matching drivers.

The consumers used explicit acknowledgements (`basic_ack`) for successfully processed messages.

Only the three active drivers were tested in this experiment. The additional D1 patterns, including Chennai and the `#` wildcard control binding, require separate verification.

## Conclusion

The RabbitMQ dispatcher and three driver consumers operated successfully for more than two minutes. The observed message delivery matched the expected topic routing behavior for the tested bindings.