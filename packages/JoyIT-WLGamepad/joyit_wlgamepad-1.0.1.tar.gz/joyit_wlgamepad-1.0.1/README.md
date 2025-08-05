# JoyIT_WLGamepad
Library to use the SBC-WLGamepad with the Raspberry Pi

## Installation
You can install this library from PyPI.
To install it for the current user on your Raspberry Pi, use the following command:
```
pip install JoyIT_WLGamepad
```

## Example
You need to clone this repository on your Raspberry Pi to be able to execute the example code.
```
git clone https://github.com/joy-it/JoyIT_WLGamepad
```
Afterward, you need to move into the directory and activate the virtual environment with the following commands.
```
cd JoyIT_WLGamepad
python -m venv --system-site-packages env
source env/bin/activate
```
Then you can execute the example with the following command.
```
python3 examples/example.py
```