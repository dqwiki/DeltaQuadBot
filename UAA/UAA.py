#! /usr/bin/python
import sys, localconfig, platform, time
#OS Runtime comments
if platform.system() == "Windows":
        sys.path.append(localconfig.winpath)
        print "You are running DeltaQuadBot UAA Module for Windows."
else:
        sys.path.append(localconfig.linuxpath)
        print "You are running DeltaQuadBot UAA Module for Linux."
import wikipedia
import globalfunc as globe
override = False
if not globe.startAllowed(override):
        print "Fatal - System Access Denied."
        sys.exit(1)
        print "System Alert - Program Still running."
globe.main()
globe.checkWait()
globe.pageCleanup()
wikipedia.stopme()
