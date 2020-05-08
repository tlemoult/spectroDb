import lib.emailFnc as emailFnc
import lib.dbSpectro as dbSpectro

db=dbSpectro.init_connection()
project="del_cep"
print("follower of this project are: ")
print(dbSpectro.getProjectFollowers_fromProjectName(db,project))

emailFnc.sendEmail("sujet Test carl Obs failed", "message de test de carl. Hey j'ai ma propre adresse maintenant.",db,project)

emailFnc.sendEmail("sujet Test carl Obs finished ", "Normalement ce message la est recus par les follower du projet.",db,project)


exit()