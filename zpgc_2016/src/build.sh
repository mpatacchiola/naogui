
echo "==== Compiling mainwindow design... ===="
pyuic4 "../include/mainwindow.ui" -o "../include/design.py"
echo "==== Compilation terminated. ===="
./main.py
