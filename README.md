# Greehill python assignment

Python package to synchronize folders and files

# How it works

Inside the given directory, modification of any folder / file will apply to every other folder / file if they have the same foldername / filename.
Available modifications:
 * add folder / file
 * remove folder / file
 * rename folder / file

# Usage

- git clone https://github.com/B-MaTe/greehill_python_assigment.git
- run the program with the following arguments:
  * path of source folder (string)
  * number of modifications allowed (int)
  * Windows example in cmd: 
    **python sync_folders.py C:\Users\User\ExampleExperimentalFolder 5**
- add / remove / rename any folder / file inside that directory
- the program will quit when the allowed number of modification is reached


# Creator
- Máté Balázs
