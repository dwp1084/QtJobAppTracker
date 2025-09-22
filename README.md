# Job Application Tracker

This is a lightweight job application tracker written in Python that uses SQLite
databases to keep track of the status of job applications, filter out inactive
ones, and show statistics on the application data.

## Usage

To run the application without building into an executable, clone this 
repository. Optionally, create a python virtual environment, either through an 
IDE or by following [this guide](https://docs.python.org/3/library/venv.html), 
and activate it. Then, install the [requirements](requirements.txt):
`pip install -r requirements.txt`.

Then, navigate to the [UI folder](JobAppTracker/QtGUI/ui). In there are a number
of QT UI files with the extension `*.ui`. For each one, in your environment, run
the following command, replacing UI_filename with the file name without the 
extension:
```
pyuic6 [UI_filename].ui -o ui_[UI_filename].py
```

If pyuic6 is not recognized as a command, either add it to your PATH, or try the
following command instead:
```
python -m PyQt6.uic.pyuic [UI_filename].ui -o ui_[UI_filename].py
```

Then finally, run [main.py](JobAppTracker/main.py)


## Build

Instructions coming soon.