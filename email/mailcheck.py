# -*-coding: utf-8 -*-
import sys,imaplib,localconfig,platform
if platform.system() == "Windows":
        sys.path.append(localconfig.winpath)
else:sys.path.append(localconfig.linuxpath)
import pywikibot

def getMsgDate(messagenum,mailserver):
    msg= mailserver.fetch(messagenum,'(RFC822)')[1][0][1]
    date= msg.split("Return-Path:")[0].split(";")[1]
    try: date= date.split("X-Received")[0]
    except: x=1#null statement
    date=date.replace("\r\n","")
    date=date.replace("        ","")
    date=date.split("(PST)")[0]
    return date
def post(num,date):
    txt="""{{fontcolor|green|'''Last message without a reply''':}} %s
<br />{{fontcolor|green|'''Current number of messages that need reply''':}} %s
<br />{{fontcolor|red|Normal response times are about 72 hours currently <br />due to the amount of email I am receiving.<br />The most urgent of emails will be responded to first,<br />and there may be additional delay beyond 72 hours.}}
<small><br />If your message came on or after this date, your email is still being
<br />attended to. If the date passes and you don't receive a reply, let me know.
<br />This page is automatically updated by [[User:DeltaQuadBot|a bot]].</small>
""" % (str(date),str(num))
    summary = "[[User:"+localconfig.botname+"|"+localconfig.botname+"]] "+ localconfig.primarytaskname
    site = pywikibot.getSite()
    pagename = localconfig.postpage
    page = pywikibot.Page(site, pagename)
    pagetxt = page.get()
    page.put(txt, comment=summary)
    return

def run():    
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(localconfig.email,localconfig.password)
        mail.select("Inbox",readonly=True)
        listNums=' '.join(mail.search(None, "UnSeen")[1]).split(" ")
        if listNums==['']:num=0
        else:num=len(listNums)
        if num==0:
                post(num,date="NULL")
                return
        date=getMsgDate(listNums[0],mail)
        post(num,date)
        mail.close()
        mail.logout()
        return
run()
