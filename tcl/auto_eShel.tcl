proc tle_auto_eShel { }  {

#	set pathSignals "Z:/mnt/gdrive/astro/base/signals/fromAudela"  
	set pathSignals "Z:/home/tlemoult/tmpTest/signals/fromAudela"  
	set startSignalFilename "eShelPipeLine-askStart"
	set runningSignalFilename "eShelPipeline-running"
	set endSignalFilename "eShelPipeLine-end"

	::console::affiche_prompt "**** boucle pipeline eShel automatique****\n"
	::console::affiche_prompt "on surveille ce Path: $pathSignals"

	#for { set a 10 } { $a<20} { incr a} 
	while 1 {
			
		if {[file exists $pathSignals/$startSignalFilename]}  {
			::console::affiche_prompt "Signal demarrage trouve, lance pipeline eShel\n"
			file delete  $pathSignals/$startSignalFilename

			::console::affiche_prompt "lance pipeline eSheln\n"
			#set fd [ open $pathSignals/$runningSignalFilename "w+" ]
			#close $fd

			# mettre ici la commande qui lance le pipeline
			::eshel::processgui::generateAndStartStartScript

			#file delete $pathSignals/$runningSignalFilename
			#::console::affiche_prompt "Fin du pipeline eShel\n"
			#set fd [ open $pathSignals/$endSignalFilename "w+" ]
			#close $fd
			  
		} 

		sleep 5000
		::console::affiche_prompt "."

	}
}

proc sleep {time} {
      after $time set end 1
      vwait end
  }