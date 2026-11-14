# From Git to Gold — Final Assignment Report

**Student:** ENGETI SANDEEP  
**Roll Number:** 23BCS081  
**Course:** Data Engineering  
**Repository:** https://github.com/ENGETI-SANDEEP-10/freshcart-pipelines

## Part A — Git and CI/CD

### A1. Repository Structure and Commit History

The `freshcart-pipelines` GitHub repository organizes the assignment into separate components: `elt/` for the FreshCart ELT notebook, `iris_project/` for the Mage ML pipeline, `stream/` for RabbitMQ scripts, `tests/` for automated tests, and `.github/workflows/` for continuous integration. The `.gitignore` file excludes environment secrets, Python caches, model files, and generated datasets.

The Git workflow follows four stages:

**Working directory → Staging area → Local Git repository → GitHub remote repository → CI testing**

The repository contains ten meaningful commits, including deliberately introducing and fixing a failing test.

**Output of `git log --oneline`:**

```text
05acdc4 Align RabbitMQ message schema with assignment requirements
d3315c3 Add evidence screenshots for Git CI, FreshCart ELT, Mage ML and RabbitMQ
0a993a0 Add RabbitMQ event streaming with topic routing and ACK/NACK handling
267154d Add Mage Iris pipeline with validation and evaluation blocks
479613c fix: restore correct 80-20 Iris data split
276e0e3 test: deliberately break Iris split to verify CI
b2a395e fix: separate Mage dependencies from CI environment
de5bcc3 ci: add automated Iris data preparation test
8c425ff feat: add FreshCart ELT and Mage ML reference notebooks
04bd122 chore: initialize project documentation and configuration
```

### A2. Git Command Explanations

| Command | Where the change happens | What exactly happens? |
|---|---|---|
| `git init` | Working directory / local repository | Initializes a Git repository and creates the `.git` directory that stores version-control metadata. |
| `git add train.py` | Staging area | Stages the current contents of `train.py` for inclusion in the next commit. |
| `git commit -m "msg"` | Local repository | Saves a snapshot of the staged changes in local Git history with a commit message. |
| `git remote add origin URL` | Local repository configuration | Registers a remote repository address under the name `origin`. |
| `git push -u origin main` | Remote Git repository | Uploads local `main` commits to the remote and configures upstream tracking. |
| `git pull origin main` | Local working branch and repository | Fetches updates from remote `main` and integrates them into the current branch. |

**Can a teammate see the code on GitHub immediately after `git commit`?**

No. A Git commit is stored locally. A teammate can see the new commit on GitHub only after it has been pushed to the remote repository, assuming they have access to it.

### A3. Automated Testing with GitHub Actions

A GitHub Actions workflow was configured to run Python tests on repository pushes. The workflow checks out the repository, sets up Python 3.12, installs dependencies, and runs `pytest`.

The `test_prepare_data.py` test verifies that the Iris dataset is divided into 120 training rows and 30 testing rows, corresponding to an 80:20 split of the 150-row dataset.

To demonstrate CI failure detection, the training/test split was deliberately changed to 70:30. The automated test detected the incorrect split and the CI workflow failed. The split was then restored to 80:20 and committed, after which CI passed.

This experiment demonstrates how automated CI tests can catch regressions before incorrect code is accepted as a working version.

**Evidence:** GitHub Actions failing and passing screenshots in `evidence/part_a/`. The final Mage and RabbitMQ commits also have passing CI evidence in `evidence/part_c/` and `evidence/part_d/`.