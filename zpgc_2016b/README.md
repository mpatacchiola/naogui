GUI 4 HRI
----------

In this experiment there are two robot (helper and master) which play an investment game with a human player.

XML parameters
--------------

- **number** {int} the trial id number
- **gaze** {True, False} If True the robot looks the player.
- **pointing** {True, False} If True the robot point the screen.
- **pmf** {float} (p)erson (m)ultiplication (f)actor. It is a value used to multiply the person investement.
- **bmf** {float} player (b) (m)ultiplication (f)actor. It multiply the total received by the Player B.
- **rinv1** {float} (r)obot (inv)estment in the 1st interaction.
- **rinv2a** {float} (r)obot (inv)estment in the 2nd interaction (option 'a')
- **rinv2b** {float} (r)obot (inv)estment in the 2nd interaction (option 'b')
- **mp3** {string} sentence produced by the robot. If the 'XXX' substring is present it is replaced with player invesment. It cannot be empty.
- **nasty** {True, False} the robot can behave differently.

```xml
<list1>
    <trial>
        <number>1</number>
        <mp3>Hello world</mp3>
        <bmf>2.0</bmf>        
        <pmf>3.0</pmf>
        <rinv1>10</rinv1>
        <rinv2a>5</rinv2a>
        <rinv2b>15</rinv2b>
        <gaze>True</gaze>
        <pointing>True</pointing>
        <nasty>False</nasty>
    </trial>
    <trial>
        <number>2</number>
        <mp3>My name is NAO</mp3>
        <bmf>2.0</bmf>   
        <pmf>3.0</pmf>
        <rinv1>10</rinv1>
        <rinv2a>5</rinv2a>
        <rinv2b>15</rinv2b>
        <gaze>True</gaze>
        <pointing>True</pointing>
        <nasty>False</nasty>
    </trial>
</list1>
```

Log structure
--------------

The log is saved in the same folder of the main file. The structure of the log is a CSV file that follows this convention:

trial, person investment first, robot investment first, person investment second, robot investment second, player b investment, person mult factor, player b mult factor, total, gaze, pointing, timer first, timer second 

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
