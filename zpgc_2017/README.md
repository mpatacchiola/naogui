GUI 4 HRI
----------

In this experiment there are two robot (opponent and banker) which play an investment game with a human player.
The opponent has his own screen and buttons to decide which price to choose. The banker is a robot which can return money two the two players.

XML parameters
--------------

- **number** {int} the trial id number
- **gaze** {True, False} If True all the robots looks the player.
- **pointing** {True, False} If True all the robots point to the screen.
- **bmf** {float} (b)anker (m)ultiplication (f)actor. It multiply the total received.
- **linv** {float} (l)eader (inv)estment
- **tinv** {float} (t)eam (inv)estment
- **word1** {string} sentence produced by the robot in the *second* interaction.
- **word2** {string} sentence produced by the robot.
- **word3** {string} sentence produced by the robot. If the 'XXX' substring is present it is replaced with the total investment of all the players.
- **word4** {string} sentence produced by the robot. If the 'XXX' substring is present it is replaced with the banker returned value.

```xml
<list1>
    <trial>
        <number>1</number>
        <word1>Hello world</word1>
        <word2>Player A, you invested invested XXX</word2>
        <word3>Player B, you invested 7</word2>
        <word4>Player B, you invested 7</word2>
        <bmf>2.0</bmf>        
        <linv>10</rinv>
        <tinv>5</binv>
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
