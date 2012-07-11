#! /usr/bin/python
#$ -j y
#$ -o $HOME/IPBE.out
import globalfunc as globe
import sys
import platform
import localconfig
if platform.system() == "Windows":
        sys.path.append(localconfig.winpath)
else:sys.path.append(localconfig.linuxpath)
import wikipedia
import json
def main():
    globe.getUserList()
if not globe.startAllowed():
        print "Fatal - System Access Denied."
        sys.exit(1)
        print "System Alert - Program Still running."
main()
