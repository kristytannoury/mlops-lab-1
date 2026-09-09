# Lab 1

## Question 1: Observe the files created, what do you think they contain?

After running uv init, some basic project files are created.

pyproject.toml contains information about the project, like its name, Python version, dependencies and configuration.

.python-version contains the Python version used by the project.

README.md is used to describe the project.

The src folder contains the Python source code of the project.

The .venv folder contains the virtual environment and the installed Python libraries.

Question 2: What are the created files? What are they used for? Which ones should be pushed to git?

After running dvc init, DVC creates files such as:

.dvc/config which contains DVC configuration.

.dvc/.gitignore which prevents DVC internal files such as cache and temporary files from being added to Git.

.dvcignore which tells DVC which files or folders it should ignore.

These configuration files should be pushed to Git because they are small and useful for everyone working on the project.

The actual DVC cache and temporary files should not be pushed.

Question 3: Where are the credentials stored? What are the options other than --global? Should the credentials be pushed to GitHub?

When using --global, the credentials are stored in the global DVC configuration of the current user, outside the project.

Other options are:

--project: saves the configuration in the project.
--local: saves it only for the current project and does not push it to Git.
--system: saves it for all users on the computer.

Credentials such as passwords or tokens should never be pushed to GitHub.

## Question 4: Take a look at the .gitignore file. Explain what happened.

After running:

dvc add data

DVC added the data/ folder to .gitignore.

This happens because Git should not track the actual data files. DVC tracks the data instead, while Git only tracks the small pointer file.

## Question 5: Do you see a .dvc file? What does it contain?

Yes, a file called data.dvc is created.

It does not contain the real dataset. It contains information about the data, such as a hash and the size of the tracked files.

This file acts as a pointer that DVC uses to know which version of the data should be used.

## Question 6: Is the code on GitHub? Is the data there? Is there a file pointing to the data? What about DagsHub?

Yes, the code is on GitHub.

The actual dataset is not stored on GitHub because the data folder is ignored by Git.

The data.dvc file is stored on GitHub and points to the version of the dataset tracked by DVC.

The actual dataset is pushed to DagsHub using:

dvc push

So GitHub contains the code and data pointer, while DagsHub stores the actual data.

## Question 7: After cloning the repository in a new folder, do you see the data folder? What command is needed?

After cloning the Git repository, the actual data is not downloaded automatically.

To download the data from the DVC remote, we use:

dvc pull

This downloads the correct version of the data and recreates the data folder.

## Question 8: Do you still see food11_processed and food11_processed_mini after checking out the old commit?

No.

When we checkout an older Git commit and then run:

dvc checkout

DVC changes the local data to match the version referenced by that old commit.

Since food11_processed and food11_processed_mini did not exist in the older version, they disappear.

When switching back to main and running:

dvc checkout

the newer data folders appear again.
