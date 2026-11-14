
flowchart TD
    A["load_iris<br/>data_loader<br/>Test: exactly 150 rows"]
    B["prepare_data<br/>transformer<br/>Test: validate train/test split"]
    C["train_model<br/>transformer<br/>Test: accuracy >= 80%"]
    D["save_results<br/>data_exporter<br/>Saves iris_predictions.csv"]

    A --> B
    B --> C
    C --> D
<!-- Open the Markdown preview in Antigravity, or paste the Mermaid code into Mermaid Live Editor to view the diagram. -->