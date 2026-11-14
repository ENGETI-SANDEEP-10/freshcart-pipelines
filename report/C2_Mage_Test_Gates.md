# Part C2 — Mage Tests as a Gate

**Student:** ENGETI SANDEEP  
**Roll Number:** 23BCS081

## Experiment Results

The Iris classification pipeline was executed five times using the `--runtime-vars` option with `max_depth` values from 1 through 5. Before every execution, the existing `iris_predictions.csv` file was deleted to ensure that CSV creation could be attributed to the current run.

| max_depth | Test accuracy | test_accuracy passed? | iris_predictions.csv created? |
|---|---|---|---|
| 1 | 0.633 (63.3%) | No | No |
| 2 | 0.967 (96.7%) | Yes | Yes |
| 3 | 1.000 (100%) | Yes | Yes |
| 4 | 1.000 (100%) | Yes | Yes |
| 5 | 1.000 (100%) | Yes | Yes |

## How Does a Failing @test Stop save_results?

The `train_model` block has a `@test` function called `test_accuracy`, which requires the test accuracy to be at least 80%. When `max_depth = 1`, the decision tree achieved only 63.3% accuracy, causing the assertion to fail. Mage marked the block test as failed and stopped the dependent `save_results` block from executing. This was confirmed because `iris_predictions.csv` did not exist after the failed run.

## Why Is Testing Before Saving Better?

Testing before saving ensures that low-quality model predictions are not published or consumed by downstream systems. If results were saved first and tested afterward, an inaccurate predictions file could already be available to users or automated processes. By making the accuracy check a prerequisite for `save_results`, Mage prevents invalid outputs from being created and makes failures easier to identify.

## Conclusion

The experiments demonstrate that Mage's `@test` decorators act as quality gates. A model that fails the required accuracy threshold cannot proceed to the exporting stage, while models that pass the test successfully produce the predictions CSV.