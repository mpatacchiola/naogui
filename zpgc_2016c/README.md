GUI 4 HRI
----------

In this experiment there are two robot (opponent and banker) which play an investment game with a human player.
The opponent has his own screen and buttons to decide which price to choose. The banker is a robot which can return money two the two players.

XML parameters
--------------

- **number** {int} the trial id number
- **gaze** {True, False} If True the robot looks the player.
- **pointing** {True, False} If True the robot point the screen.
- **pmf** {float} (p)erson (m)ultiplication (f)actor. It is a value used to multiply the person investment.
- **bmf** {float} player (b) (m)ultiplication (f)actor. It multiply the total received by the Player B.
- **rmf** {float} robot multiplication factor
- **rinv** {float} (r)obot (inv)estment
- **binv** {float} player (b) (inv)estment
- **word1** {string} sentence produced by the robot in the *second* interaction. If the 'XXX' substring is present it is replaced with player investment. the string 'YYY' is replaced with the robot investment. Use '-' for empty sentence.
- **word2** {string} sentence produced by the robot. If the 'XXX' substring is present it is replaced with player investment. the string 'YYY' is replaced with the robot investment. Use '-' for empty sentence.


```xml
<list1>
    <trial>
        <number>1</number>
        <word1>Hello world</word1>
        <word2>I invested YYY and you invested XXX</word2>
        <bmf>2.0</bmf>        
        <pmf>3.0</pmf>
        <rmf>3.0</rmf>
        <rinv>10</rinv>
        <binv>5</binv>
        <gaze>True</gaze>
        <pointing>True</pointing>
    </trial>
</list1>
```

Log file
--------------

The log file contains the experiment values for each trial.
The log is saved in the same folder of the `main.py` file. The log is a **CSV** file that follows this convention:

- **trial**
- **person investment**
- **robot investment**
- **player b investment**
- **person mult factor**
- **player b mult factor**
- **person total**
- **gaze**
- **pointing**
- **timer interaction**


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
3. Install Python NAOqi SDK setup from the aldebaran website [here](https://community.ald.softbankrobotics.com/en/resources/software)
4. If you wanna use the simulator install choregraphe (license required) from [here](http://doc.aldebaran.com/1-14/software/installing.html)

Because of different problem of compatibility that i found during the porting on windows, it is better to install the 32 bit version of python and pyQt. When installing pyQT it is necessary to install the version for python 2.7 which is called "PyQt4-4.11.4-gpl-Py2.7-Qt4.8.7-x32.exe".
