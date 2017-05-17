import lib.emailFnc as emailFnc
import lib.dbSpectro as dbSpectro

db=dbSpectro.init_connection()
print dbSpectro.getProjectFollowers_fromProjectName(db,'RR_lyr')

emailFnc.sendEmail("sujetTest", "message de test",db,'RR_lyr')

exit()