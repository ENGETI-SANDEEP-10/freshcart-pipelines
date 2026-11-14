# Part C — ML Pipeline with Mage

## C1. Pipeline Graph and Execution

The Iris classification pipeline was built in Mage using the `iris_classifier` pipeline. The original pipeline contained four connected blocks:

`load_iris → prepare_data → train_model → save_results`

| Block | Mage block type | Responsibility and validation |
|---|---|---|
| `load_iris` | Data loader | Loads the 150-row Iris dataset and validates the loaded data |
| `prepare_data` | Transformer | Splits the dataset into 120 training and 30 testing rows; validates the split |
| `train_model` | Transformer | Trains a decision tree and checks that test accuracy is at least 80% |
| `save_results` | Data exporter | Saves the 30 test predictions to `iris_predictions.csv` after upstream tests pass |

The pipeline was executed in Google Colab using Mage's test-enabled pipeline runner:

```bash
mage run iris_project iris_classifier --test
```

The initial run used `max_depth=3`. It produced **150 loaded rows, 120 training rows, 30 testing rows, and 100% test accuracy**. The prediction CSV contained 30 records.

**Evidence:** `C1_Mage_Pipeline_Graph.png`, `C1_Mage_Pipeline_Test_Run.png`, and `C1_Iris_Predictions_CSV.png`.

## C2. Automated Tests as a Gate

The decision-tree depth was changed using runtime variables for five separate runs. Before each execution, the previous `iris_predictions.csv` file was deleted to determine whether the current run produced an output.

| `max_depth` | Test accuracy | `test_accuracy` passed? | Predictions CSV created? |
|---|---:|---|---|
| 1 | 0.633 | No | No |
| 2 | 0.967 | Yes | Yes |
| 3 | 1.000 | Yes | Yes |
| 4 | 1.000 | Yes | Yes |
| 5 | 1.000 | Yes | Yes |

The `train_model` block contains a test that asserts accuracy is at least 0.80. With `max_depth=1`, the accuracy was approximately 63.3%, so the test failed and the downstream `save_results` block did not execute. The absence of the CSV confirmed that the failing result had not been exported.

This is preferable to exporting first and checking later because it prevents results that fail a defined quality requirement from being published. The same principle applies to production ML systems, where invalid predictions should be stopped before downstream consumers use them.

**Evidence:** `C2_Max_Depth_1.png` through `C2_Max_Depth_5.png`.

## C3. Evaluation Branch

An `evaluate_model` transformer was added as a second downstream block of `train_model`.

The resulting branching structure was:

```text
train_model
├── save_results
└── evaluate_model
```

The edited pipeline configuration in `pipelines/iris_classifier/metadata.yaml` connects both downstream blocks from `train_model`:

```yaml
downstream_blocks: [save_results, evaluate_model]
```

The evaluation transformer calculated a confusion matrix and classification metrics from the 30 test predictions.

**Observed confusion matrix:**

| Actual \ Predicted | Class 0 | Class 1 | Class 2 |
|---|---:|---:|---:|
| Class 0 | 10 | 0 | 0 |
| Class 1 | 0 | 9 | 0 |
| Class 2 | 0 | 0 | 11 |

**Observed evaluation metrics:**

| Metric | Value |
|---|---:|
| Accuracy | 1.000 |
| Macro precision | 1.000 |
| Macro recall | 1.000 |
| Macro F1-score | 1.000 |

All 30 test predictions were correct in this run. The Mage UI was opened through a Cloudflare tunnel, and the branching pipeline graph was verified.

**Evidence:** `C3_Mage_UI_Branched_Graph.png`, `C3_Evaluation_Metrics.png`, and `C3_Evaluation_Branch_Run.png`.

## C4. Custom Validation Block

A new transformer named `validate_iris` was inserted immediately after `load_iris`.

The final six-block pipeline was:

```text
load_iris
    ↓
validate_iris
    ↓
prepare_data
    ↓
train_model
    ├── save_results
    └── evaluate_model
```

The `validate_iris` block checks three conditions:

1. The dataset contains exactly **150 rows**.
2. There are **no missing values**.
3. The target column contains exactly **three classes**.

An attached `@test` function asserts the required conditions. During execution, the block reported 150 rows, zero missing values, and three classes, and its test passed.

This validation step prevents incomplete or structurally incorrect input data from reaching model training. It is particularly useful because detecting a problem before the train/test split makes the source of the failure easier to identify.

The custom block and updated pipeline configuration were committed to GitHub in commit `267154d`. Local pytest passed, and the GitHub Actions Python CI workflow also passed.

**Evidence:** `C4_Validate_Iris_Test_Passed.png`, `C4_Local_Pytest_Passed.png`, `C4_GitHub_Actions_Passed.png`.

## Conclusion

Mage made the ML workflow reproducible by organizing data loading, validation, preparation, training, exporting, and evaluation as connected blocks. The depth experiment demonstrated that automated tests act as quality gates, while the evaluation branch and custom validation block improved observability and input-data reliability.