# Covid19-Italy-Counter
I made a simple Python programm for a Raspberry Pi in order to show every data about the COVID19 in out country. It has national data, specific region data and Basilicata (my own region) data. It is coded in order to be displayed on a small 4.5" display with a resolution of 480x240. On bigger display you will see only a small window with this dimensions, and on smaller display (where have you found it?) it will go outside of the display.

# Installation
To use this script you will need Python3 and the module Pandas. To get pandas simply type "pip3 install pandas" in the terminal. The other modules are already installed in python on the Raspberry Pi.
Download the files in the repository and put 'covid-gui.py' and the 'img' folder in the same directory.

# Run
Using a terminal window, move into the directory where 'covid-gui.py' is located. In Linux is "cd /path/to/file". Then run the script using "python3 covid-gui.py". Don't run it outside of the folder, like with "python3 path/covid-gui.py" or it will not work.
