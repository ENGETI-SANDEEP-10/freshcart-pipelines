# Part E — Debugging Reflection

## A CI Failure That Helped Verify Our Tests

One important issue I encountered during this assignment was a failing GitHub Actions workflow caused by an incorrect Iris training and testing split. The pipeline was supposed to divide the 150-row Iris dataset into 120 training records and 30 testing records, corresponding to an 80:20 ratio. To verify whether the automated test could detect an error, I deliberately changed the split parameter from `test_size=0.2` to `test_size=0.3`.

After committing and pushing this modification, GitHub Actions executed the Python CI workflow and reported a failure. I examined the test results and identified that the failure was caused by the changed train/test ratio. With a 30% test split, the resulting dataset no longer satisfied the assertions expecting exactly 120 training rows and 30 testing rows.

I fixed the issue by restoring `test_size=0.2` in the data preparation code. I then committed the correction and pushed it to GitHub. The subsequent CI run passed, confirming that the expected 80:20 split had been restored.

The failure and correction are recorded in Git commits `276e0e3` and `479613c`, with corresponding red and green workflow screenshots in `evidence/part_a/`.

This experience taught me that automated testing is not simply about obtaining a green status. A reliable test must also fail when an important requirement is violated. Git history helped me identify the change that introduced the problem, while CI provided immediate feedback that the correction worked. Together, version control and automated testing made the pipeline easier to debug and safer to modify.