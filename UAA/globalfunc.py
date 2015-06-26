# -*- coding: utf-8 -*-
from datetime import datetime
import sys
import platform
import time
import json
import re
import traceback

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
def checkRegisterTime(user, maxDays,advanced):
        """Returns True if the given user is more than maxDays old, else False."""
        maxSeconds = maxDays * 24 * 60 * 60
        site = wikipedia.getSite()
        params = {"action": "query", "list": "users", "ususers": user, "format": "json", "usprop": "registration","rawcontinue":"1"}
        response, raw = site.postForm(site.apipath(), params)
        result = json.loads(raw)
        try:reg = result["query"]["users"][0]["registration"]
        except:return [False,False]
        then = time.strptime(reg, "%Y-%m-%dT%H:%M:%SZ")
        now = time.gmtime()
        thenSeconds = time.mktime(then)
        nowSeconds = time.mktime(now)
        if advanced:
                if thenSeconds < nowSeconds - maxSeconds:
                        return [True, True]
                return [False, True]
        else:
                if thenSeconds < nowSeconds - maxSeconds:
                        return True
                return False

def searchlist(line, listtype):
    try:line=line.decode("utf-8")
    except:noNeedToTryAndPlayWithEncoding = True #not a real var
    if line == "":return
    if listtype == "bl":
        i=0
        while i < len(bl):
            if bl[i].lower().split(":")[0] != "":check = re.search(bl[i].lower().split(":")[0], line.lower())
            else: check = None
            if not (check == "None" or check == None):
                return [True, bl[i].split(":")[0], ' '.join(bl[i].split(":")[1:])]
            i = i+1
        return [False, None, None]
    if listtype == "wl":
        for entry in wl:
            if entry.lower() in line.lower():
                return True
        return False
    if listtype == "sl":
        i=0
        while i < len(sl):#can be omptimized with for statement
            if re.search(".", sl[i]) != None:
                stringline = sl[i].split(":")[1]
                stringline = stringline.split(" ")
                for everyexpr in stringline:
                    if everyexpr in line:
                        if re.search(".", everyexpr.lower()) != None:
                            newline = line.lower().replace(everyexpr.lower(), sl[i].lower().split(":")[0])
                            blslcheck = searchlist(newline.lower(), "bl")
                            if blslcheck[0] and re.search(".", everyexpr) != None:
                                wlcheck = searchlist(newline, "wl")
                                if not wlcheck:
                                    return [False, 'Used '+everyexpr.lower()+ ' instead of '+sl[i][0]+' attempting to skip filter: '+blslcheck[1],blslcheck[2]]
                                else:return [True, None, None]
            i = i+1
        matchnum = 0
        for eachline in sl:
                if eachline == "":continue
                splitline = eachline.split(": ")[1]
                splitline = splitline.split(" ")
                for entry in splitline:                        
                        if entry in line:
                                if not re.search('[a-z]|[A-Z]|[0-9]',entry) == None:continue
                                matchnum = matchnum +1
        if matchnum > 1:return [False, 'Attempting to skip filters using multiple similiar charecters','LOW_CONFIDENCE,NOTE(Multiple characters like ν and ә can be contained in the same phrase, this rule detects when one or more occurs)']
        return True
def checkUser(user,waittilledit,noEdit):
        bltest = searchlist(user, "bl")
        try:line = str(bltest[1])
        except UnicodeEncodeError:
                line = bltest[1]
        except:
                post(user,"This bot does not support the encoding in this username or filter. Please consider reporting this to my master. Tripped on: " + bltest[1],"LOW_CONFIDENCE",False)
                trace = traceback.format_exc() # Traceback.
                print trace # Print.
                return
        flags = str(bltest[2])
        if searchlist(user, "wl"):
                return
        if bltest[0]:
                if noEdit:
                        #print 'No edit - 1' + str(bltest[1]) +" "+ str(bltest[2])
                        return 
                else:return post(user,str(bltest[1]),str(bltest[2]),str(waittilledit))
        if "NO_SIM_MATCH" in flags:return
        slcheck = searchlist(user, "sl")
        if slcheck == True:a=1
        elif waittilledit != False and 'WAIT_TILL_EDIT' in str(slcheck[2]):waittilledit = True
        try:
                if not slcheck[0] and not bltest[0]:
                        if noEdit:
                                #print "No edit - 2 "+str(slcheck[1]) +" "+ str(slcheck[2])
                                return
                        return post(user,str(slcheck[1]),str(slcheck[2]),str(waittilledit))
        except:
                if not slcheck and not bltest[0]:
                        if noEdit:
                                #print "No edit - 3"+str(slcheck[1]) +" "+ str(slcheck[2])
                                return
                        return post(user,str(slcheck[1]),str(slcheck[2]),str(waittilledit))
        return
def main():
        site = wikipedia.getSite()
        params = {'action': 'query',
        	'list': 'logevents',
        	'letype': 'newusers',
        	'leend':checkLastRun(),
        	'lelimit':'5000',
        	'leprop':'user',
                'rawcontinue':'1',
        	'format':'json'        
                }
        response, raw = site.postForm(site.apipath(), params)
        result = json.loads(raw)
        reg = result["query"]["logevents"]
        postCurrentRun()
        for entry in reg:
                try:user = entry["user"]
                except KeyError:
                        #Placeholder for OS'd users
                        oversighted=True
                        continue
                if user == "":continue
                checkUser(user, True, False)
def runDry():
        site = wikipedia.getSite()
        params = {'action': 'query',
        	'list': 'logevents',
        	'letype': 'newusers',
        	'leend':checkLastRun(),
        	'lelimit':'5000',
        	'leprop':'user',
        	'format':'json',
                'rawcontinue':'1'
                }
        response, raw = site.postForm(site.apipath(), params)
        result = json.loads(raw)
        reg = result["query"]["logevents"]
        for entry in reg:
                user = entry["user"]
                if user == "":continue
                checkUser(user, True, True)
def post(user, match, flags, restrict):
        summary = "[[User:"+localconfig.botname+"|"+localconfig.botname+"]] "+ localconfig.primarytaskname +" - [[User:"+user+"]] ([[Special:Block/"+user+"|Block]])"
        site = wikipedia.getSite()
        pagename = localconfig.postpage
        page = wikipedia.Page(site, pagename)
        pagetxt = page.get()
        if user in pagetxt:
                return
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
def waitTillEdit(user):
        registertime=checkRegisterTime(user, 7,True)
        if not registertime[1]:
                return
        if registertime[0]:
                checkUser(user, False, True)
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
def cutup(array):
    i=1
    while i < len(array)-1:
        try:
            while array[i][0] != ";":
                i=i+1
            array[i] = array[i].split(":")
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
def startAllowed(override):
        if override:return True
        site = wikipedia.getSite()
        pagename = localconfig.gopage
        page = wikipedia.Page(site, pagename)
        start = page.get()
        if start == "Run":
                return True
        if start == "Dry run":
                runDry()
        if start == "Dry":
                print "Notice - Running Checkwait.py only"
                import checkwait #import as it's a py file
                return False
        else:
                return False
def checkWait():
        newlist=""#blank variable for later
        site = wikipedia.getSite()
        pagename = localconfig.waitlist
        page = wikipedia.Page(site, pagename)
        waiters = page.get()
        waiters = waiters.replace("}}","")
        waiters = waiters.replace("*{{User|","")
        waiters = waiters.split("\n")
        for waiter in waiters:
                if waiter == "":continue#Non-existant user
                if checkRegisterTime(waiter, 7,False):continue
                if checkBlocked(waiter):continue#If user is blocked, skip putting them back on the list.
                if getEditCount(waiter) == True:#If edited, send them to UAA
                        checkUser(waiter,False,False)
                        continue
                if waiter in newlist:continue#If user already in the list, in case duplicates run over
                #Continue if none of the other checks have issues with the conditions for staying on the waitlist
                newlist = newlist + "\n*{{User|" + waiter + "}}"
                #print "\n*{{User|" + waiter + "}}"
        summary = localconfig.editsumwait
        site = wikipedia.getSite()
        pagename = localconfig.waitlist
        page = wikipedia.Page(site, pagename)
        pagetxt = page.get()
        newlist = newlist.replace("\n*{{User|}}","")
        page.put(newlist, comment=summary)
def pageCleanup():
        resolvedDatabase = ["{{UAA\|w}}",
                            "{{UAA\|wt}}",
                            "{{UAA\|wait}}",
                            "{{UAA\|m}}",
                            "{{UAA\|moniter}}",
                            "{{UAA\|mon}}",
                            "{{UAA\|d}}",
                            "{{UAA\|disc}}",
                            "{{UAA\|discussing}}",
                            "{{UAA\|dc}}",
                            "{{UAA\|dcon}}",
                            "{{UAA\|change}}",
                            "{{UAA\|request}}",
                            "{{UAA\|rc}}",
                            "{{UAA\|rcu}}"
                            ]
        declinedDatabase = ["{{UAA\|a}}",
                            "{{UAA\|afc}}",
                            "{{UAA\|s}}",
                            "{{UAA\|st}}",
                            "{{UAA\|stale}}",
                            "{{UAA\|rn}}",
                            "{{UAA\|real}}",
                            "{{UAA\|name}}",
                            "{{UAA\|b}}",
                            "{{UAA\|bl}}",
                            "{{UAA\|blatant}}",
                            "{{UAA\|no}}",
                            "{{UAA\|not}}",
                            "{{UAA\|e}}",
                            "{{UAA\|eye}}",
                            "{{UAA\|ci}}",
                            "{{UAA\|coi}}",
                            "{{UAA\|coin}}",
                            "{{UAA\|r}}",
                            "{{UAA\|rfcn}}"
                            ]
        newlist=""#blank variable for later
        rawnewlist=""
        movelist=""
        site = wikipedia.getSite()
        pagename = localconfig.postpage
        page = wikipedia.Page(site, pagename)
        uaapage = page.get()
        #print uaapage
        uaapage = uaapage.replace("==[[Wikipedia:UAA/BOT|Bot-reported]]==\n","")
        usergrid = uaapage.split("*{{user-uaa|1=")
        for cell in usergrid:
                declined = False
                if cell == "":continue
                user = cell.split("}}")[0]
                if checkBlocked(user):continue#If user is blocked, skip putting them back on the list.
                if checkRegisterTime(user, 14,False):continue#Requests over 14 days are removed for inaction
                if user in newlist:continue
                for entry in resolvedDatabase:
                        if re.search(entry.lower(), cell.lower()) == None:
                                continue
                        else:
                                movelist = movelist + "*{{user-uaa|1=" + ''.join(cell)
                                declined = True
                                break
                if declined:continue
                for entry in declinedDatabase:
                        if re.search(entry.lower(), cell.lower()) == None:
                                continue
                        else:
                                declined = True
                                break
                if declined:continue
                rawnewlist = rawnewlist + "\n" + user
                newlist = newlist + "*{{user-uaa|1=" + ''.join(cell)
                #print user
        ## UAA Bot page posting ##
        summary = localconfig.editsumclear
        site = wikipedia.getSite()
        pagename = localconfig.postpage
        page = wikipedia.Page(site, pagename)
        pagetxt = page.get()
        newlist = "==[[Wikipedia:UAA/BOT|Bot-reported]]==\n" + newlist
        page.put(newlist, comment=summary)
        ## UAA Holding pen posting ##
        site = wikipedia.getSite()
        pagename = localconfig.holdpage
        page = wikipedia.Page(site, pagename)
        holdpage = page.get()
        if movelist == "":return
        if time.strftime("%B") not in holdpage:
                holdpage = holdpage + "\n==" + time.strftime("%B") + "=="
        if time.strftime("%d") not in holdpage.split(time.strftime("%B"))[1]: #or time.strftime("%d").split("0")[1] not in holdpage.split(time.strftime("%B"))[1]:
                holdpage = holdpage + "\n===" + time.strftime("%d") + "===\n"
        holdpage = holdpage + "\n" + movelist
        page.put(holdpage, comment=summary)
        return
global bl
bl = getlist("bl")
global wl
wl = getlist("wl")
global sl
sl = getlist("sl")
