# Racing-Companion
Racing Companion helps racing enthusiasts manage maintenance work and track days for their racing vehicles with an intuitive and powerful interface.

Read more (non technical) [here](https://dherslof.github.io/RacingCompanion/)!

# Background
Racing-Companion is a personal project in order to keep track of track day data and maintenance work for my different vehicles. My wish is to be able to get the time
so I can continue to update the tool with more features and improvements going forward.

# Features
The application has multi-vehicle support for following key features:
* Maintenance Tracking
* Track Day Management

## Planned features
- [ ] Maintenance Reminders
- [ ] Performance Analytics
- [ ] Data Export
- [ ] Notes & Checklists

## Known issues
Below is a list of known issues. A known issue can be a improvement of existing functionality, small tweaks or plain bugs.

## Dependencies
Except having `Python3` installed on a `Ubuntu` (debian) machine, following packages needs to be installed on the machine in order for the application to run properly:

**apt** packages:
* python3-tk

**pip** packages:
* numpy
* customtkinter
* matplotlib

In order to simplify the dependency installtion, the provided `install_dependencies.sh` script can be executed with *sudo* privileges. This will installed the required things for you.
After a successful execution of the script the application should be ready to be used.

### Extra
In some cases, an update to the new installed packages might be needed. At the time of writing, the only known case is for the **pip** package `Pillow`. This can be noticed by following error log:
```bash
Traceback (most recent call last):
  File "racing-companion.py", line 11, in <module>
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
  File "/usr/local/lib/python3.8/dist-packages/matplotlib/backends/backend_tkagg.py", line 1, in <module>
    from . import _backend_tk
  File "/usr/local/lib/python3.8/dist-packages/matplotlib/backends/_backend_tk.py", line 15, in <module>
    from PIL import Image, ImageTk
ImportError: cannot import name 'ImageTk' from 'PIL' (/usr/lib/python3/dist-packages/PIL/__init__.py)
```

The update is done by:
```bash
$ pip3 install --upgrade Pillow
```

# Installation & Usage
No specific installation is required if the dependencies are fulfilled. Just clone repository and start using!

1. Clone the repositiory
```bash
$ git clone git@github.com:dherslof/RacingCompanion.git
```
2. Install dependencies if needed
```bash
sudo ./install_dependencies.sh
```
3. Use the application!
```bash
python3 racing-companion.py
```

For the best user experience, start by adding your vehicle!

*Optional*: The `setup_local_bin_link.sh` script can be used during installation as well. It will link the racing-companion to your local bin directory which will let you execute the application outside of the repo directory.

# Test
Currently the testing is a bit limited. However, it's very important for the project and highly prioritized. The aim is 100% coverage on base functionality, non GUI. Since I have limited experience of GUI testing, there is no set target but it should not be forgotten!

## Unit tests
`pytest` is used for unit testing, and unit test files are stored at `test/`.

Run test from repo root:
```bash
PYTHONPATH=. pytest
```

## Support
### Data Storage
The application uses `/home/$USER/racing-companion` as a storage directory, and data files will be stored under `/home/$USER/racing-companion/.rcstorage/`. Data files are currently stored in a plain **.json** file. It's simple to read and can be used by other tools. This will be updated in the future.
