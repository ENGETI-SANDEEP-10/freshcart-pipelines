# D3 — RabbitMQ Acknowledgements and Malformed-Message Handling

## Objective

To demonstrate how RabbitMQ consumers acknowledge successfully processed messages, reject malformed messages, and handle potential message redelivery.

## Experiment Setup

The experiment used the durable `rapido-dispatch` topic exchange, a Python dispatcher, and a driver consumer connected to RabbitMQ through Pika.

The driver was started with the binding pattern `bangalore.#`, allowing it to receive requests from all Bangalore zones.

The dispatcher deliberately omitted the `zone` field from every 10th JSON message while preserving the original routing key.

## Observed Results

The dispatcher successfully published malformed messages. For example, message #20 was published using the routing key `chennai.whitefield.food`, but its JSON body did not contain the `zone` field.

The driver logs also showed a malformed Bangalore request being rejected:

`[Ravi] REJECTED key=bangalore.koramangala.food: Missing required fields: ['zone']`

Valid Bangalore requests continued to appear as `RECEIVED` in the same driver terminal.

This demonstrated that the consumer could distinguish valid requests from malformed ones.

## ACK versus NACK

**ACK (`basic_ack`)** indicates that a consumer successfully processed a delivered message. RabbitMQ can then remove that message from the queue.

**NACK (`basic_nack`)** indicates that the consumer cannot or will not process the message successfully.

In this experiment:

- Valid messages were processed and acknowledged using `basic_ack`.
- Messages missing required fields were rejected using `basic_nack(requeue=False)`.
- The consumer used `auto_ack=False`, so acknowledgements were handled explicitly.

## What Happens if the Consumer Crashes Before ACK?

If a consumer's connection closes before it acknowledges a delivered message, RabbitMQ generally requeues the unacknowledged message for another delivery.

This helps prevent message loss when a consumer crashes, although the same message may be processed again. Production consumers should therefore be designed to tolerate duplicate deliveries.

This behavior is explained conceptually; a consumer-crash experiment was not performed.

## Poison Messages and Requeue Behavior

A **poison message** is a message that repeatedly causes consumer processing to fail, such as a request containing a permanently invalid payload.

If such a message is rejected with `basic_nack(requeue=True)`, RabbitMQ may redeliver it repeatedly. This can create a requeue loop, waste resources, and prevent useful work from progressing.

Using `basic_nack(requeue=False)` avoids immediate redelivery to the same queue. RabbitMQ discards the rejected message unless a dead-letter exchange or another relevant policy is configured.

For a production system, rejected messages should generally be routed to a dead-letter queue for inspection rather than silently discarded.

## Conclusion

The experiment demonstrated valid-message processing and malformed-message rejection using explicit RabbitMQ acknowledgements. Deliberately removing a required JSON field allowed the consumer's validation logic to exercise the negative-acknowledgement path.

The test supports the distinction between `basic_ack` for valid messages and `basic_nack(requeue=False)` for malformed messages, while illustrating why uncontrolled requeueing can be dangerous.

## Evidence

- `evidence/part_d/D3_Malformed_Dispatcher.png`
- `evidence/part_d/D3_Driver_NACK.png`