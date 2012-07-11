#! /usr/bin/python
#$ -l h_rt=1:00:00
#$ -j y
#$ -o $HOME/UAA.out
import sys, localconfig, platform
if platform.system() == "Windows":
        print "You are running DeltaQuadBot UAA Module for Windows."
        sys.path.append(localconfig.winpath)
else:
        sys.path.append(localconfig.linuxpath)
        print "You are running DeltaQuadBot UAA Module for Linux."
import wikipedia

import globalfunc as globe
	
if not globe.startAllowed():
        print "Fatal - System Access Denied."
        sys.exit(1)
        print "System Alert - Program Still running."
globe.main()
globe.checkWait()
wikipedia.stopme()
