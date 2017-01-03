# first import everything we will need for the scheduling
import astropy.units as u
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

		
		#beg=Time(date)+17*u.hour
		#end=Time(date)+31*u.hour
		
		
		beg=Time.now()
		beg.format = 'isot'
		end=self.observer.sun_rise_time(beg,which="next")
		end.format = 'isot'
		# Create a schedule
		self.priority_schedule = Schedule(beg, end)
		print "to next sun Rise" 
		print 'Schedule created from [',beg,'UTC to',end,'UTC ]'

	def addTargetFromName(self,name,durationBlock,priority,config):  # config= dictionnary
		print 'add target name=',name
		self.blocks.append(ObservingBlock(FixedTarget.from_name(name), durationBlock, priority, configuration = config, constraints = []))

	def addTargetFromCoord(self,name,coord,durationBlock,priority,config):  # config= dictionnary
		print 'add target name=',name
		self.blocks.append(ObservingBlock(FixedTarget(coord=coord, name=name), durationBlock, priority, configuration = config, constraints = []))


	def optimize(self):
		# insert blocks into the schedule, and run the scheduler
		print "start schedule.optimize()"
		self.prior_scheduler(self.blocks, self.priority_schedule)
		print "**************************"
		print self.priority_schedule
		print "**************************"
	

	def writeLst(self,filename):
		print "mySchedule.writeLst ",filename
		f=open(filename,'w+')
		for block in self.priority_schedule.observing_blocks:
			name=block.target.name
			project=(block.configuration)['project']
			FLUX_V=block.configuration['FLUX_V']
			ExposureTime=block.configuration['ExposureTime']
			NbExposure=block.configuration['NbExposure']
			TotExposure=block.configuration['TotExposure']
			intTime=block.configuration['intTime']
			uid=block.configuration['uid']
			extraConfig=block.configuration['extraConf']
			calib=block.configuration['calib']
			
			block.start_time.format = 'isot'

			if name!='TransitionBlock':
				coord=block.target.coord.to_string('hmsdms')
				(ra,dec)=coord.split(' ')
				line='"'+name+'"  '+ra[:-3]+'s  '+dec[:-3]+'s  '+str(FLUX_V)+'  FALSE  "Project='+str(project)
				line+="&uid="+str(uid)
				line+="&calib="+calib
				if ExposureTime!=None:  line+="&ExposureTime="+str(ExposureTime)
				if NbExposure!=None: line+="&NbExposure="+str(NbExposure)
				if TotExposure!=None: line+="&TotExposure="+str(TotExposure)
				if intTime!=None: line+="&intTime="+str(intTime)
				if extraConfig!=None: line+="&"+extraConfig

				line+="&dateStart="+str(block.start_time)
				line+='"'
				f.write(line+'\n')

		f.close
