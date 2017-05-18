import smtplib,json
import dbSpectro

def main():
	sendEmail(subject      = '[Carl]test', 
		message      = 'test email. \nObservation of plaskett star started at 22:16\n and finished', 
		)


def sendEmail(subject, message,db,projectName):

	json_text=open("../config/config.json").read()
	config=json.loads(json_text)

	adress=dbSpectro.getProjectFollowers_fromProjectName(db,projectName)
	to_addr_list=[ config['email']['myAdress'] ]
	to_addr_list.extend(adress.split(','))
	print to_addr_list

	smtpserver= config['email']['smtp']
	login= config['email']['login']
	password= config['email']['password']
	
	cc_addr_list= [ ]
	from_addr= config['email']['from']
	header  = 'From: %s\n' % from_addr
	header += 'To: %s\n' % ','.join(to_addr_list)
	#header += 'Cc: %s\n' % ','.join(cc_addr_list)
	header += 'Subject: %s\n\n' % subject
	message = header + message
 
	server = smtplib.SMTP(smtpserver)
	server.starttls()
	server.login(login,password)
	problems = server.sendmail(from_addr, to_addr_list, message)
	server.quit()
	return problems

if __name__ == '__main__':
	main()