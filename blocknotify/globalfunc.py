import sys
import platform
import localconfig
if platform.system() == "Windows":
        sys.path.append(localconfig.winpath)
else:sys.path.append(localconfig.linuxpath)
import wikipedia
import json, re
def getBlockInfo(IP):
        test = re.search("(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",IP)
        if test == None:#user
            passdict = {"action":"query", "list":"blocks", "bkprop":"id|user|by|timestamp|expiry|reason|flags", "bklimit":"1","bkusers":IP,"format":"json"}
            isUser=True
        else:#ip
            passdict = {"action":"query", "list":"blocks", "bkprop":"id|user|by|timestamp|expiry|reason|range|flags", "bklimit":"1","bkip":IP,"format":"json"}
            isUser=False
        site = wikipedia.getSite()
        #predata = {'action': 'query',
       #     'list': 'allusers',
       #     'augroup': 'ipblock-exempt',
       #     'aulimit':'5000',
       #     'format':'json'}
        response, raw = site.postForm(site.apipath(), passdict)
        result = json.loads(raw)
        reg = result["query"]["blocks"][0]
        #existance test
        try:blockid = reg[u'id']
        except:return
        user = reg[u'user']
        blocktime = reg[u'timestamp']
        blockend = reg[u'expiry']
        admin = reg[u'by']
        reason = reg[u'reason']
        #templates
        if "{{" in reason:
                reason = reason.replace("{{","{{tl|")
        try:
                autoblock = reg[u'automatic']
                autoblock = "{{done|Yes}}"
        except:autoblock = "{{Notdone|No}}"
        try:
                anononly = reg[u'anononly']
                anononly = "{{done|Yes}}"
        except:
                if isUser:anononly = "N/A"
                else:anononly = "{{notdone|No}}"
        try:
            nocreate = reg[u'nocreate']
            nocreate = "{{Notdone|No}}"
        except:nocreate = "{{done|Yes}}"
        try:
            setautoblock = reg[u'autoblock']
            setautoblock = "{{done|Yes}}"
        except:setautoblock = "{{Notdone|No}}"
        try:
            noemail = reg[u'noemail']
            noemail = "{{done|Yes}}"
        except:noemail = "{{Notdone|No}}"
        try:
            allowtalk = reg[u'allowusertalk']
            allowtalk = "{{done|Yes}}"
        except:allowtalk = "{{Notdone|No}}"
        return [blockid, user, admin, blocktime, blockend, reason, autoblock, allowtalk, noemail, anononly, nocreate, setautoblock]
def getBlockList():
    site = wikipedia.getSite()
    passdict = {
        "action":"query",
        "list":"categorymembers",
        "cmtitle":"Category:Requests for unblock",
        "cmprop":"title",
        "format":"json"}
    response, raw = site.postForm(site.apipath(), passdict)
    result = json.loads(raw)
    reg = result["query"]["categorymembers"]
    userlist = "" #predeclare
    for member in reg:
        if member["ns"] == 3:userlist += member["title"].split(":")[1]+"\n" #kill ns
    buildtable(userlist.split("\n"))
def buildtable(userlist):
    tabletop = """{| class="wikitable" style="text-align: center;"
|-
!ID!!User!!Blocking admin!!Starting!!Expiry!!Reason!!Autoblock!!Talkpage access!!Email block!!Anon. Only!!Account Creation Blocked!!Autoblock IP"""
    tablebody=""
    for user in userlist:
        intel = getBlockInfo(user)
        tablebody += "\n|-\n|%s||[[User talk:%s]]||[[User:%s]]||%s||%s||%s||%s||%s||%s||%s||%s||%s" % (intel[0], intel[1], intel[2], intel[3], intel[4], intel[5], intel[6], intel[7], intel[8], intel[9], intel[10], intel[11])
    table = tabletop + tablebody + "\n|}"
    sendPage(table)
def sendPage(text):
    #print text
    summary = localconfig.summary
    site = wikipedia.getSite()
    pagename = localconfig.pagelocation
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

