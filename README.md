# Covid19-Italy-Counter
I made a simple Python programm for a Raspberry Pi in order to show every data about the COVID19 in out country. It has national data, specific region data and Basilicata (my own region) data. It is coded in order to be displayed on a small 4.5" display with a resolution of 480x240. On bigger display you will see only a small window with this dimensions, and on smaller display (where have you found it?) it will go outside of the display.

# Installation
To use this script you will need Python3 and the module Pandas. To get pandas simply type "pip3 install pandas" in the terminal. The other modules are already installed in python on the Raspberry Pi.
Download the files in the repository and put 'covid-gui.py' and the 'img' folder in the same directory.

# Run
Using a terminal window, move into the directory where 'covid-gui.py' is located. In Linux is "cd /path/to/file". Then run the script using "python3 covid-gui.py". Don't run it outside of the folder, like with "python3 path/covid-gui.py" or it will not work. If you want to run the improved version, use "python3 covid-gui-2-0.py"

# Improved re-coded version
The "covid-gui-2-0.py" application is an improved re-coded version of the original one. I didn't like how I coded the first one, and I had problems adding some features, so I decided to re-code it in order to add those features.
The GUI and all of the functions are the same as before. In this version I added a local download of the data in 3 .csv files (one for Italy, one for all of the regions, and one for the Basilicata) in order to get the difference in every data between today and yesterday. The first time you will start the application, in every data it will show "(+0)" instead of the actual number, because "yesterday" data are missing. The day after it will show the right number. Unfortunately you have to run the application everyday, at around 19:00 CEST, so it can download the latest data.
I also added a backup function for the .csv files. You can disable it by changing to false the flags:
- 'backup_mode_nazione'
- 'backup_mode_regione'
- 'backup_mode_basilicata'

