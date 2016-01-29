import sys
import platform
import localconfig
if platform.system() == "Windows":
        sys.path.append(localconfig.winpath)
else:sys.path.append(localconfig.linuxpath)
import wikipedia
import json
def getUserList():
        site = wikipedia.getSite()
        predata = {'action': 'query',
            'list': 'allusers',
            'augroup': 'ipblock-exempt',
            'aulimit':'5000',
            'format':'json'}
        response, raw = site.postForm(site.apipath(), predata)
        result = json.loads(raw)
        reg = result["query"]["allusers"]
        userlist=""
        detaillist=""
        for user in reg:
                username = user["name"]
                userlist = userlist+ "\n"+"*{{User|"+user["name"]+"}}"
                try:detaillist = detaillist + "\n*" + query(username)
		except:
			print "FAILED - " + username
        sendPage(userlist, "raw")
        sendPage(detaillist, "list")
        return
def query(user):
        letitle = "User:" + user
        #letitle = letitle.split("&quot;")[0]
        site = wikipedia.getSite()
        predata = {'action': 'query',
         'list': 'logevents',
         'letype': 'rights',
         'letitle':letitle,
         'format':'json',
	 'lelimit':'100'
              }
        #print 'LETITLE: ' +letitle
        response, raw = site.postForm(site.apipath(), predata)
        result = json.loads(raw)
        log = result["query"]["logevents"]
        #print log
        for event in log:
                if event["params"]["oldgroups"] == '': event["params"]["oldgroups"]="None"
                if not "ipblock-exempt" in event["params"]["oldgroups"] and "ipblock-exempt" in event["params"]["newgroups"]:return event["timestamp"]+ " [[User:" + event["user"] + "|" + event["user"] + "]] ([[User talk:" + event["user"] + "|talk]] | [[Special:Contributions/" + event["user"] + "|contribs]] | [[Special:Block/" + event["user"] + "|block]])" + " changed rights for [[" +event["title"] + "]] from " + ','.join(event["params"]["oldgroups"]) + " to " + ','.join(event["params"]["newgroups"]) + " per '" + event["comment"] + "'"
                #print "Event: "+event["timestamp"]+ " " + event["user"] + " changed userrights for " +event["title"] + " from " + event["rights"]["old"] + " to " + event["rights"]["new"] + " because " + event["comment"]
def sendPage(text, txtformat):
    #print text
    summary = localconfig.summary
    if txtformat == "list":
        site = wikipedia.getSite()
        pagename = localconfig.listlocation
        page = wikipedia.Page(site, pagename)
        #print text
        pagetxt = page.get()
        page.put(text, comment=summary)
    elif txtformat == "raw":
        site = wikipedia.getSite()
        pagename = localconfig.rawlocation
        page = wikipedia.Page(site, pagename)
        pagetxt = page.get()
        page.put(text, comment=summary)
def startAllowed():
        site = wikipedia.getSite()
        pagename = localconfig.gopage
        page = wikipedia.Page(site, pagename)
        start = page.get()
        if start == "Run":
                return True
        else:
                return False
