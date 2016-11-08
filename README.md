NAOGUI
----------

This repository includes the code used in different HRI experiments at Plymouth University between 2015 and 2018 as part of the THRIVE Project and collateral research. The Graphical User Interface (GUI) has been designed using **QT4** and **pyqt** and is compatible with both Linux and Windows. If you want to use the code and you need some feedback you can contact Massimiliano Patacchiola. Most of the code uses a NAO robot and a touchscreen that enable the interaction with the user.

The authors involved in this research are:

- Angelo Cangelosi
- Jeremy Goslin
- Massimiliano Patacchiola
- Ilaria Torre
- Debora Zanatto

The folders are named following the convention [first letter of the authors surname][year][additional letter]. 
For example the code **tzpgc_2016** stands for [Torre, Zanatto, Patacchiola, Goslin, Cangelosi][2016]


Installation
------------

Linux:
------

1. Install qt4: `sudo apt-get install qt4-dev-tools qt4-designer qtcreator`
2. Inastall pyqt: `sudo apt-get install python-qt4 pyqt4-dev-tools`
3. Install choregraphe if you want to use the simulator


Windows:
--------

1. Install python 2.7 (32bit version) from [here](https://www.python.org/download/releases/2.7/)
2. Install pyQt for python 2.7 downloding the binary version from [here](https://riverbankcomputing.com/software/pyqt/download).
3. If you wanna use the simulator install choregraphe (license required) from [here](http://doc.aldebaran.com/1-14/software/installing.html)

Because of different problem of compatibility that i found during the porting on windows, it is better to install the 32 bit version of python and pyQt.
