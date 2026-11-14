
# Part E — End-to-End Data Engineering Architecture

```mermaid
flowchart TB
    G["GitHub Repository<br/>freshcart-pipelines"]
    CI["GitHub Actions CI<br/>Python 3.12 + pytest"]

    G -->|"Push triggers"| CI

    subgraph ELT["Part B — FreshCart ELT"]
        EX["Sample Web and Mobile APIs"]
        BR["Snowflake Bronze<br/>Raw JSON"]
        SI["Snowflake Silver<br/>Clean, Validate, Deduplicate"]
        GO["Snowflake Gold<br/>Orders, Revenue, Loyalty Points"]

        EX -->|"Extract and Load"| BR
        BR -->|"SQL Transform"| SI
        SI -->|"Enrich and MERGE"| GO
    end

    subgraph ML["Part C — Mage ML Pipeline"]
        IR["Iris Dataset<br/>150 Records"]
        VA["Load and Validate"]
        PR["Prepare Data<br/>120 Train / 30 Test"]
        TR["Decision Tree Training<br/>Accuracy Test"]
        SA["Save Predictions CSV"]
        EV["Evaluation Metrics<br/>Confusion Matrix"]

        IR --> VA
        VA --> PR
        PR --> TR
        TR --> SA
        TR --> EV
    end

    subgraph ST["Part D — RabbitMQ Streaming"]
        DI["Python Dispatcher<br/>Every 2 Seconds"]
        MQ["RabbitMQ Topic Exchange<br/>rapido-dispatch"]
        DR["Driver Queues<br/>Topic Pattern Matching"]
        AC["ACK / NACK<br/>Message Handling"]

        DI -->|"JSON Events"| MQ
        MQ --> DR
        DR --> AC
    end

    G -. "Version-controlled ELT code" .-> EX
    G -. "Version-controlled Mage code" .-> IR
    G -. "Version-controlled stream code" .-> DI

    CI -. "Automated test for<br/>Iris data preparation" .-> PR
```

## Architecture Explanation

The GitHub repository stores the source code for the FreshCart ELT, Mage ML, and RabbitMQ streaming components. GitHub Actions automatically executes Python tests when changes are pushed.

The FreshCart ELT pipeline loads raw API data into Snowflake Bronze, cleans and deduplicates records in Silver, and publishes business-ready orders in Gold.

The Mage pipeline independently loads the Iris dataset, validates it, prepares training and testing data, trains a decision-tree classifier, and exports predictions and evaluation results.

The RabbitMQ dispatcher independently publishes events to a topic exchange, which routes matching requests to private driver queues. Consumers use ACK for valid messages and NACK for malformed messages.

The diagram represents the overall architecture of the assignment. The Iris model does not directly train on FreshCart Gold data, and RabbitMQ events are not directly loaded into Snowflake in the implemented version.
