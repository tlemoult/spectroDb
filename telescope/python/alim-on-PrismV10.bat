
echo allume Powercontrol telescope
python C:\Users\DELL\worspace\prod\spectroDb\telescope\python\IPX800ctrl.py info 7=1
TIMEOUT /T 1

echo echo allume camera guidage
python C:\Users\DELL\worspace\prod\spectroDb\telescope\python\PowerBoxSet.py COM2 0=1


rem echo allume Electronique telescope Astrosib
rem python C:\Users\DELL\worspace\prod\spectroDb\telescope\python\PowerBoxSet.py COM2 3=1


echo allume monture
python C:\Users\DELL\worspace\prod\spectroDb\telescope\python\IPX800ctrl.py info 6=1

TIMEOUT /T 2
"C:\Program Files (x86)\PRiSM v10\prism.exe" &
