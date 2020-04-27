import sys
import lib.dbSpectro as dbSpectro

print("efface les spectres et fichiers de travail d'une observation")
if len(sys.argv) < 2:
    print("nombre d'argument incorrect")
    print("utiliser: /npython removeWorksSpc.py obsId")
    exit()

obsId=int(sys.argv[1])
print("obsId = "+str(obsId))

db = dbSpectro.init_connection()
cursorSpcFiles,cursorOtherFiles = dbSpectro.getListRemoveWork(db, obsId)

for spcFile in cursorSpcFiles: print(spcFile[0])
for otherFile in cursorOtherFiles: print(otherFile[0])

answer = raw_input("are you sure to delete from database these files ?   Y/N  O/N  (N)" )
if answer=='Y' or answer=='O':
    print("delete files...")
    dbSpectro.removeWork(db,obsId)

dbSpectro.update_observation_status(db,obsId,'ACQFINISH')
