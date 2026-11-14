import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer

if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def validate_iris(df, *args, **kwargs):
    """Validate the Iris dataset before preprocessing."""

    missing_values = int(df.isnull().sum().sum())
    class_count = int(df['target'].nunique())

    print("Iris validation results:")
    print("Total rows:", len(df))
    print("Missing values:", missing_values)
    print("Number of classes:", class_count)

    return df


@test
def test_iris_quality(output, *args):
    """Prevent invalid Iris data from reaching downstream blocks."""

    assert len(output) == 150, \
        "Expected exactly 150 Iris records"

    assert output.isnull().sum().sum() == 0, \
        "Iris dataset contains missing values"

    assert output['target'].nunique() == 3, \
        "Expected exactly three Iris classes"

    print("Iris data-quality test passed.")
