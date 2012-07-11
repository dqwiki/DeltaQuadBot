#import globalfunc as globe
import sys
import platform
import localconfig
if platform.system() == "Windows":
        sys.path.append(localconfig.winpath)
else:sys.path.append(localconfig.linuxpath)
import wikipedia
import json
site = wikipedia.getSite()
predata = {'action': 'query',
        'list': 'allusers',
        'augroup': 'ipblock-exempt',
        'aulimit':'5000',
        'format':'json'}
response, raw = site.postForm(site.apipath(), predata)
result = json.loads(raw)
reg = result["query"]["allusers"]
#print reg
userlist=""
detaillist=""
for user in reg:
        userlist = userlist+ "\n"+"{{User|"+user["name"]+"}}"
        detaillist = detaillist + "\n"
def query(user):
    letitle = "User:" + user
    #letitle = letitle.split("&quot;")[0]
    site = wikipedia.getSite()
    predata = {'action': 'query',
    'list': 'logevents',
    'letype': 'rights',
    'letitle':letitle,
    'format':'json'
           }
    #print 'LETITLE: ' +letitle
    response, raw = site.postForm(site.apipath(), predata)
    result = json.loads(raw)
    log = result["query"]["logevents"]
    #print log
    for event in log:
            if event["rights"]["old"] == "": event["rights"]["old"]="None"
            if not "ipblock-exempt" in event["rights"]["old"] and "ipblock-exempt" in event["rights"]["new"]:return event["timestamp"]+ " " + event["user"] + " changed userrights for " +event["title"] + " from " + event["rights"]["old"] + " to " + event["rights"]["new"] + " because " + event["comment"]
            #print "Event: "+event["timestamp"]+ " " + event["user"] + " changed userrights for " +event["title"] + " from " + event["rights"]["old"] + " to " + event["rights"]["new"] + " because " + event["comment"]
print query("DeltaQuad.alt")
