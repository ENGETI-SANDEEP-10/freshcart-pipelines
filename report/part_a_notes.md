
# Part A — Git and CI/CD

## A2. Where does each command act?

| Command | Where the change happens | What exactly happens? |
|---|---|---|
| `git init` | Local repository | Creates a new Git repository by initializing the hidden `.git` directory. |
| `git add train.py` | Staging area | Adds the current changes in `train.py` to the staging area for the next commit. |
| `git commit -m "msg"` | Local repository | Saves a snapshot of staged changes in local Git history with the message `msg`. |
| `git remote add origin URL` | Local Git configuration | Registers a remote repository address under the name `origin`. It does not upload code. |
| `git push -u origin main` | Remote repository and local tracking configuration | Uploads local commits from `main` to `origin` and sets the upstream tracking branch. |
| `git pull origin main` | Local repository and working directory | Fetches the remote `main` branch and integrates its changes into the current local branch. |

### Can a teammate see my code immediately after git commit?

No. The `git commit` command saves changes only
in my local Git repository. It does not upload
them to GitHub.

My teammate can see the committed code on GitHub
only after I push the commits to the remote
repository using `git push`, provided they have
access to that repository.

### Git workflow explanation

The working directory contains the files I edit.

When I run `git add`, the selected changes move
into the staging area.

When I run `git commit`, Git records a snapshot
of those staged changes in the local repository.

When I run `git push`, my local commits are
uploaded to the remote GitHub repository.

GitHub Actions then automatically executes
the configured CI workflow after a push.

### A3. CI experiment summary

I implemented an automated pytest test to verify
the 80:20 split of the Iris dataset.

The correct implementation produces:
- Training rows: 120
- Testing rows: 30

I deliberately changed test_size from 0.2 to 0.3,
which produced:
- Training rows: 105
- Testing rows: 45

The pytest assertion failed, and GitHub Actions
correctly reported a failed workflow.

I restored test_size to 0.2, committed the fix,
and pushed the corrected code.

The final GitHub Actions workflow passed.

### CI evidence

- A3_CI_Green_Run.png
- A3_CI_Deliberate_Failure.png
- A3_CI_Final_Green_Run.png
- A3_CI_Experiment_Overview.png

### GitHub repository

https://github.com/ENGETI-SANDEEP-10/freshcart-pipelines
