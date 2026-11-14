# Part D1 — RabbitMQ Topic Exchange Routing Predictions

**Student:** ENGETI SANDEEP  
**Roll Number:** 23BCS081

## Exchange Configuration

- Exchange name: `rapido-dispatch`
- Exchange type: `topic`
- Routing key format: `city.zone.type`

## Driver Bindings

| Driver | Binding pattern |
|---|---|
| Ravi | `bangalore.koramangala.*` |
| Priya | `bangalore.indiranagar.*` |
| Arjun | `bangalore.*.ride` |
| Meena | `bangalore.*.food` |
| Karthik | `chennai.tnagar.food` |
| Control | `bangalore.#` |

## Routing Predictions — Before Execution

| Routing key | Expected receivers |
|---|---|
| `bangalore.koramangala.food` | Ravi, Meena, Control |
| `bangalore.indiranagar.ride` | Priya, Arjun, Control |
| `bangalore.whitefield.ride` | Arjun, Control |
| `chennai.tnagar.food` | Karthik |
| `chennai.whitefield.ride` | None |
| `bangalore.koramangala` | Control only |

## Explanation

A RabbitMQ topic exchange routes messages to queues according to their binding patterns. The `*` wildcard matches exactly one word, while the `#` wildcard matches zero or more words. A message may reach multiple driver queues if several binding patterns match its routing key.

For example, `bangalore.koramangala.food` matches Ravi's zone-specific binding, Meena's food-delivery binding, and Control's Bangalore-wide binding.

The final routing key, `bangalore.koramangala`, has only two words. Ravi does not receive it because `bangalore.koramangala.*` requires a third word. Control receives it because `bangalore.#` matches the remaining `koramangala` word.

## Execution Status

These predictions were prepared before implementing and executing the RabbitMQ dispatcher and drivers. Actual routing behavior will be verified during Part D2.