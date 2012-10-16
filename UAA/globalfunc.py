from datetime import datetime
import sys
import platform
import time
import json
import re

import localconfig
if platform.system() == "Windows":
        sys.path.append(localconfig.winpath)
else:sys.path.append(localconfig.linuxpath)
import wikipedia
import userlib

def currentTime():
	time = str(datetime.utcnow())
	time = time.replace(' ','T')
	time = time.replace('-','')
	time = time.replace(':','')
	time = time.split('.')[0]
	time = time + 'Z'
	return time
def getEditCount(user):
        try:
                username = userlib.User("en", user)
                if username.editCount() == 0:
                        return False
                else:
                        return True
        except:return None
def checkBlocked(user):
        try:
                username = userlib.User("en", user)
                return username.isBlocked()
        except:return None
def checkRegisterTime(user, maxDays):
        """Returns True if the given user is more than maxDays old, else False."""
        maxSeconds = maxDays * 24 * 60 * 60
        site = wikipedia.getSite()
        params = {"action": "query", "list": "users", "ususers": user, "format": "json", "usprop": "registration"}
        response, raw = site.postForm(site.apipath(), params)
        result = json.loads(raw)
        reg = result["query"]["users"][0]["registration"]
        then = time.strptime(reg, "%Y-%m-%dT%H:%M:%SZ")
        now = time.gmtime()
        thenSeconds = time.mktime(then)
        nowSeconds = time.mktime(now)
        if thenSeconds < nowSeconds - maxSeconds:
                print "True"
                return True
        return False
def searchlist(line, listtype):
    if listtype == "bl":
        i=0
        while i < len(bl):
            #print bl[i].split(":")[0] #Debug lines for when blacklist is having an issue parsing something. 
            #print re.search(bl[i].split(":")[0], line.lower())
            if bl[i].split(":")[0] != "":check = re.search(bl[i].split(":")[0], line.lower())
            else: check = None
            if check == "None" or check == None:
                holder = 1#useless line
            else:
                return [True, bl[i].split(":")[0], ' '.join(bl[i].split(":")[1:])]
            i = i+1
        return [False, None, None]
    if listtype == "wl":
        for entry in wl:
            if entry in line.lower():
                return True
        return False
    if listtype == "sl":
        i=0
        while i < len(sl):
            if re.search(".", sl[i]) != None:
                stringline = sl[i].split(":")[1]
                stringline = stringline.split(" ")
                for everyexpr in stringline:
                    if everyexpr in line:
                        if re.search(".", everyexpr) != None:newline = line.replace(everyexpr, sl[i].split(":")[0])
                        if re.search(".", everyexpr) != None:
                            blslcheck = searchlist(newline, "bl")
                            if blslcheck[0] and re.search(".", everyexpr) != None:
                                if searchlist(newline, "wl"):
                                    return [False, 'Used '+sl[i][0]+' attempting to skip filter: '+blslcheck[1],blslcheck[2]]
                                else:return [True, None, None]
                    else:check = None
                if check == "None" or check == None:
                    holder = 1#useless line
            i = i+1
        return True
def checkUser(user,waittilledit):
        bltest = searchlist(user, "bl")
        try:line = str(bltest[1])
        except:
                print 'Error'
                return
        flags = str(bltest[2])
        if bltest[0]:
                if searchlist(user, "wl"):
                        print "Clear - on wl"
                        return
                else:
                        return post(user,str(bltest[1]),str(bltest[2]),waittilledit)
        slcheck = searchlist(user, "sl")
        if slcheck == True:a=1
        elif 'WAIT_TILL_EDIT' in str(slcheck[2]):waittilledit = True
        else:waittilledit = False
        try:
                if not slcheck[0] and not bltest[0]:
                        return post(user,str(slcheck[1]),str(slcheck[2]),waittilledit)
        except:
                if not slcheck and not bltest[0]:
                        return post(user,str(slcheck[1]),str(slcheck[2]),waittilledit)
        return
def main():
        site = wikipedia.getSite()
        params = {'action': 'query',
        	'list': 'logevents',
        	'letype': 'newusers',
        	'leend':checkLastRun(),
        	'lelimit':'5000',
        	'leprop':'user',
        	'format':'json'        
                }
        response, raw = site.postForm(site.apipath(), params)
        result = json.loads(raw)
        reg = result["query"]["logevents"]
        postCurrentRun()
        print 'Last run occured at ' + checkLastRun()
        for entry in reg:
                user = entry["user"]
                if user == "":continue
                checkUser(user, True)
def runDry():
        site = wikipedia.getSite()
        params = {'action': 'query',
        	'list': 'logevents',
        	'letype': 'newusers',
        	'leend':globe.checkLastRun(),
        	'lelimit':'5000',
        	'leprop':'user',
        	'format':'json'        
                }
        response, raw = site.postForm(site.apipath(), params)
        result = json.loads(raw)
        reg = result["query"]["logevents"]
	#postCurrentRun()
        print 'Last run occured at ' + checkLastRun()
        json = clearXML(json)
        for user in json:
                user = user.replace("&amp;#039;","'")
                user = user.replace("&#039;","'")
		#checkUser(user, True)
                #print "User:"+user
def post(user, match, flags, restrict):
        summary = "[[User:"+localconfig.botname+"|"+localconfig.botname+"]] "+ localconfig.primarytaskname +" - [[User:"+user+"]] ([[Special:Block/"+user+"|Block]])"
        site = wikipedia.getSite()
        pagename = localconfig.postpage
        page = wikipedia.Page(site, pagename)
        pagetxt = page.get()
        if user in pagetxt:
                print 'Blocked posting of '+user
                return
        else:
                print 'Did not block the posting of '+user
        text = "\n\n*{{user-uaa|1="+user+"}}\n"
        if "LOW_CONFIDENCE" in flags:
                text = text + "*:{{clerknote}} There is low confidence in this filter test, please be careful in blocking. ~~~~\n"
        if "WAIT_TILL_EDIT" in flags and restrict != False:#If waittilledit override it not active, aka first run
                edited = getEditCount(user)
                if edited == None:
                        return#Skip user, probally non-existant
                if edited == False:
                        waitTillEdit(user)#Wait till edit, user has not edited
                        return#leave this indented, or it will not continue to report edited users
        if "LABEL" in flags:
                note = flags.split("LABEL(")[1].split(")")[0]
                text = text + "*:Matched: " + note + " ~~~~\n"
        else:
                text = text + "*:Matched: " + match + " ~~~~\n"
        if "NOTE" in flags:
                note = flags.split("NOTE(")[1].split(")")[0]
                text = text + "*:{{clerknote}} " + note + " ~~~~\n"
        if "SOCK_PUPPET" in flags:
                sock = flags.split("SOCK_PUPPET(")[1].split(")")[0]
                text = text + "*:{{clerknote}} Consider reporting to [[WP:SPI]] as [[User:%s]]. ~~~~\n" % sock
        if restrict == False:text + "*:{{done|Waited until user edited to post.}} ~~~~\n"
        if not checkBlocked(user):page.put(pagetxt + text, comment=summary)
        else:print user+ " is blocked. Skip reporting."
def waitTillEdit(user):
        print user
        if checkRegisterTime(user, 7):
                checkUser(user)
                print 'Over 7 days '+user
                return
        summary = "[[User:DeltaQuadBot|DeltaQuadBot]] Task UAA listing - Waiting for [[User:"+user+"]] ([[Special:Block/"+user+"|Block]]) to edit"
        site = wikipedia.getSite()
        pagename = localconfig.waitlist
        page = wikipedia.Page(site, pagename)
        pagetxt = page.get()
        text = "\n*{{User|" + user+"}}"
        if text in pagetxt:
                return
        page.put(pagetxt + text, comment=summary)
def checkLastRun():
        site = wikipedia.getSite()
        pagename = localconfig.timepage
        page = wikipedia.Page(site, pagename)
        time = page.get()
        return time
def postCurrentRun():
        site = wikipedia.getSite()
        summary = localconfig.editsumtime
        pagename = localconfig.timepage
        page = wikipedia.Page(site, pagename)
        page.put(str(currentTime()), comment=summary)
        print 'Time of check: ' + str(currentTime())
def cutup(array):
    i=1
    while i < len(array)-1:
        try:
            while array[i][0] != ";":
                i=i+1
            #array[i] = array[i].replace(";","")
            array[i] = array[i].split(":")
            #print array[i]
            i = i + 1
        except:
            return array
        return array
def getlist(req):
    site = wikipedia.getSite()
    if req == "bl":
        pagename = localconfig.blacklist
    if req == "wl":
        pagename = localconfig.whitelist
    if req == "sl":
        pagename = localconfig.simlist
    page = wikipedia.Page(site, pagename)
    templist = page.get()
    templist = templist.replace("{{cot|List}}\n","")
    templist = templist.replace("{{cot}}\n","")
    templist = templist.replace("{{cob}}","")
    if req != "wl":templist = templist.replace("\n","")
    if req != "wl":templist = templist.split(";")
    if req == "wl":templist = templist.split("\n;")
    templistarray = cutup(templist)
    return templistarray
def startAllowed():
        site = wikipedia.getSite()
        pagename = localconfig.gopage
        page = wikipedia.Page(site, pagename)
        start = page.get()
        if start == "Run":
                return True
        if start == "Dry":
                print "Notice - Running Checkwait.py only"
                import checkwait #import as it's a py file
                return False
        else:
                return False
def checkWait():
        print 'Checkwait running'
        newlist=""#blank variable for later
        site = wikipedia.getSite()
        pagename = localconfig.waitlist
        page = wikipedia.Page(site, pagename)
        waiters = page.get()
        waiters = waiters.replace("}}","")
        waiters = waiters.replace("*{{User|","")
        waiters = waiters.split("\n")
        for waiter in waiters:
                if checkBlocked(waiter):#If user is blocked, skip putting them back on the list.
                        print "Blocked"
                elif getEditCount(waiter) == True:#If edited, send them to UAA
                        checkUser(waiter,False)
                        print "Send to UAA"
                elif waiter == "":holder=1#Non-existant user
                else:
                        if waiter in newlist:#If user already in the list, in case duplicates run over
                                print "already in list"
                        else:
                                newlist = newlist + "\n*{{User|" + waiter + "}}"
                                #print "\n*{{User|" + waiter + "}}"
        summary = localconfig.editsumwait
        site = wikipedia.getSite()
        pagename = localconfig.waitlist
        page = wikipedia.Page(site, pagename)
        pagetxt = page.get()
        newlist.replace("\n*{{User|}}","")
        page.put(newlist, comment=summary)
global bl
bl = getlist("bl")
global wl
wl = getlist("wl")
global sl
sl = getlist("sl")
