# first import everything we will need for the scheduling
import astropy.units as u
import datetime
from astropy.coordinates import EarthLocation,SkyCoord
from astropy.time import Time
from astroplan import (Observer, FixedTarget, ObservingBlock, Transitioner, PriorityScheduler, Schedule)
from astroplan.constraints import AtNightConstraint, AirmassConstraint, TimeConstraint, AltitudeConstraint
from astroplan.plots import plot_schedule_airmass
import matplotlib.pyplot as plt



class MySchedule(object):
	def __init__(self):
		location = EarthLocation.from_geodetic(2.581944444*u.deg, 48.88027778*u.deg, 50*u.m)
		self.observer = Observer(location=location, name="Chelles", timezone="UTC")
		self.global_constraints = global_constraints = [ AltitudeConstraint(min=25*u.deg,max=70*u.deg,boolean_constraint=True),
													 AtNightConstraint.twilight_civil()] 
		self.blocks = []
		self.transitioner = Transitioner(.8*u.deg/u.second, {'filter':{'default': 600*u.second}})

		# Initialize the scheduler
		self.prior_scheduler = PriorityScheduler(constraints = self.global_constraints, observer = self.observer, transitioner = self.transitioner)

		var=1
		if var==1:
			date=str(datetime.date.today())
			beg=Time(date)+17*u.hour
			end=Time(date)+(24+7)*u.hour
		else:		
			beg=Time.now()
			beg.format = 'isot'
			#end=self.observer.sun_rise_time(beg,which="next")
			end=beg+17*u.hour

		end.format = 'isot'
		# Create a schedule
		self.priority_schedule = Schedule(beg, end)
		print("to next sun Rise") 
		print('Schedule created from [',beg,'UTC to',end,'UTC ]')

	def addTargetFromName(self,name,durationBlock,priority,config):  # config= dictionnary
		print('add target name=',name)
		self.blocks.append(ObservingBlock(FixedTarget.from_name(name), durationBlock, priority, configuration = config, constraints = []))

	def addTargetFromCoord(self,name,coord,durationBlock,priority,config):  # config= dictionnary
		print('add target name=',name)
		self.blocks.append(ObservingBlock(FixedTarget(coord=coord, name=name), durationBlock, priority, configuration = config, constraints = []))


	def optimize(self):
		# insert blocks into the schedule, and run the scheduler
		print("**************************")
		print("start schedule.optimize()")
		self.prior_scheduler(self.blocks, self.priority_schedule)
		print("**************************")
		print(self.priority_schedule)
		print("**************************")
	
	def writeLstRequest(self,filename):
		print("writeLstRequest:")
		self.writeLst(filename,self.blocks)

	def writeLstSchedule(self,filename):
		print("writeLstSchedule:")
		self.writeLst(filename,self.priority_schedule.observing_blocks)

	def writeLst(self,filename,lstBlocks):
		print("mySchedule.writeLst ",filename)
		f=open(filename,'w+')
		for block in lstBlocks:
			name=block.target.name
			project=(block.configuration)['project']
			FLUX_V=block.configuration['FLUX_V']
			ExposureTime=block.configuration['ExposureTime']
			NbExposure=block.configuration['NbExposure']
			TotExposure=block.configuration['TotExposure']
			intTime=block.configuration['intTime']
			uid=block.configuration['uid']
			extraConfig=block.configuration['extraConf']
			calib=block.configuration['Calib']
			

			if name!='TransitionBlock':
				coord=block.target.coord.to_string('hmsdms')
				(ra,dec)=coord.split(' ')
				#fix cordinnate ra,dec precision to 2 digits
				raLst=ra[:ra.find('m')]+'m'+"{:05.2f}".format(float(ra[ra.find('m')+1:ra.find('s')]))+"s"
				decLst=dec[:dec.find('m')]+'m'+"{:05.2f}".format(float(dec[dec.find('m')+1:dec.find('s')]))+"s"
				print(f"name={name} ra={ra} dec={dec} => raLst={raLst} decLst={decLst}")
				line='"'+name+'"  '+raLst+'  '+decLst+'  '
				line+=str(FLUX_V)+'  FALSE  "Project='+str(project)
				line+="&Calib="+str(calib)
				line+="&uid="+str(uid)
				if ExposureTime!=None:  line+="&ExposureTime="+str(ExposureTime)
				if NbExposure!=None: line+="&NbExposure="+str(NbExposure)
				if TotExposure!=None: line+="&TotExposure="+str(TotExposure)
				if intTime!=None: line+="&intTime="+str(intTime)
				if extraConfig!=None: line+="&"+extraConfig

				if block.start_time is not None:
					block.start_time.format = 'isot'
					line+="&dateStart="+str(block.start_time)
				else:
					line+="&priority="+str(block.priority)
				line+='"'
				f.write(line+'\n')

		f.close

	def plotAirMas(self):
		plt.figure(figsize = (14,6))
		plot_schedule_airmass(self.priority_schedule)
		plt.tight_layout()
		plt.legend(loc="upper right")
		plt.show()

	def showTable(self):
		print(self.priority_schedule.to_table())
