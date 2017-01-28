import smtplib,json

def main():
	sendEmail(subject      = '[Carl]Obs started', 
		message      = 'Observation of plaskett star started at 22:16\n and finished', 
		)


def sendEmail(subject, message):

	json_text=open("../config/config.json").read()
	config=json.loads(json_text)
	smtpserver= config['email']['smtp']
	login= config['email']['login']
	password= config['email']['password']
	to_addr_list= [ config['email']['to'] ]
	cc_addr_list= [ config['email']['cc'] ]
	from_addr= config['email']['from']
	header  = 'From: %s\n' % from_addr
	header += 'To: %s\n' % ','.join(to_addr_list)
	header += 'Cc: %s\n' % ','.join(cc_addr_list)
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