GoFish experiment with NAOs
----------------------------

This experiment is an implementation of the GoFish game using NAOs robot instead of virtual Avatars.
The files in this repository are the only one modified in order to implement the robot movements.

The code requires a CSV file called `robot.csv` where for each row there is:

1. Name of the avatar [Veronika, Monika, Tereza]
2. IP address of the robot which must be associated to the avatar
3. PORT for the connection to the robot (default: 9559)
4. Movement. A boolean variable which define if the robot should move (True) or not (False)

