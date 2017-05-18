import lib.emailFnc as emailFnc
import lib.dbSpectro as dbSpectro

db=dbSpectro.init_connection()
print dbSpectro.getProjectFollowers_fromProjectName(db,'RR_lyr')

emailFnc.sendEmail("sujet Test carl", "message de test de carl",db,'RR_lyr')

exit()