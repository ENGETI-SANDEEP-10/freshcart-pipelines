
# From Git to Gold — Data Engineering Pipelines

**Student:** ENGETI SANDEEP  
**Roll Number:** 23BCS081  
**Course:** Data Engineering

**GitHub Profile:**
https://github.com/ENGETI-SANDEEP-10

**Repository:**
https://github.com/ENGETI-SANDEEP-10/freshcart-pipelines

## Project Overview

This repository contains the implementation of the
"From Git to Gold" Data Engineering assignment.

The project covers version control, CI/CD, ELT,
machine learning orchestration, and event streaming.

## Components

### Part A — Git and CI/CD
- Git repository and version control
- GitHub Actions continuous integration
- Automated testing with pytest
- Successful and deliberately failing CI experiments

### Part B — FreshCart ELT
- Extract sample API data into raw files
- Load raw data into Snowflake Bronze
- Clean, validate and deduplicate orders
- Maintain customer history using SCD Type 2
- Publish Gold order facts
- Execute data-quality checks

### Part C — Mage ML Pipeline
- Load the Iris dataset
- Split data into training and testing sets
- Train a Decision Tree classifier
- Validate model accuracy
- Export predictions and evaluation results

### Part D — RabbitMQ Streaming
- Publish ride and food requests
- Route messages using a topic exchange
- Process messages through private driver queues
- Implement ACK and NACK handling

### Part E — Report
- Assignment answers and explanations
- Execution evidence
- Integration diagram
- Debugging reflection

## Technology Stack

- Python 3.12
- Git and GitHub
- GitHub Actions
- Snowflake
- Mage
- RabbitMQ with pika
- pytest
- Google Colab
- Google Antigravity IDE

## Repository Structure

- `elt/` — FreshCart notebook
- `iris_project/` — Mage ML pipeline
- `stream/` — RabbitMQ dispatcher and driver
- `tests/` — Automated tests
- `evidence/` — Assignment screenshots
- `report/` — Final report and supporting materials
- `.github/workflows/` — CI configuration

## Development Status

Project initialization in progress.

Implementation and testing results will be documented
as each assignment component is completed.

## Security

Secrets and credentials must not be committed.
Use environment variables for sensitive settings.
