import lib.emailFnc as emailFnc
import lib.dbSpectro as dbSpectro

db=dbSpectro.init_connection()
print dbSpectro.getProjectFollowers_fromProjectName(db,'del_cep')

emailFnc.sendEmail("sujet Test carl", "message de test de carl. Hey j'ai ma propre adresse maintenant.",db,'NewBe')

exit()