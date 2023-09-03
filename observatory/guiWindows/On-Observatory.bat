echo **********************************************
echo * script mise en route manuelle observatoire *
echo **********************************************
echo 
echo allume Powercontrol telescope
python C:\Users\DELL\worspace\prod\spectroDb\telescope\python\IPX800ctrl.py info 7=1
TIMEOUT /T 1

echo allume camera guidage
python C:\Users\DELL\worspace\prod\spectroDb\telescope\python\PowerBoxSet.py COM2 0=1

echo allume Electronique telescope Astrosib
python C:\Users\DELL\worspace\prod\spectroDb\telescope\python\PowerBoxSet.py COM2 3=1

echo allume monture
python C:\Users\DELL\worspace\prod\spectroDb\telescope\python\IPX800ctrl.py info 6=1

echo ouvre petale telescope
python C:\Users\DELL\worspace\prod\spectroDb\telescope\python\astrosib-cmd.py COM9 SHUTTEROPEN?1,1,1,1,1

echo mise en route ventillateur miroir primaire
python C:\Users\DELL\worspace\prod\spectroDb\telescope\python\astrosib-cmd.py COM9 COOLERAUTOON?1

echo mise en route chauffage mirroir secondaire
python C:\Users\DELL\worspace\prod\spectroDb\telescope\python\astrosib-cmd.py COM9 HEATAUTOON?2

TIMEOUT /T 2
"C:\Program Files (x86)\PRiSM v10\prism.exe" &
