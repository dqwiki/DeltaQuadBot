import sys,imaplib,localconfig,platform
if platform.system() == "Windows":
        sys.path.append(localconfig.winpath)
else:sys.path.append(localconfig.linuxpath)
import wikipedia

def getMsgDate(messagenum):
    msg= mail.fetch(messagenum,'(RFC822)')[1][0][1]
    date= msg.split("Return-Path:")[0].split(";")[1]
    date=date.replace("\r\n","")
    date=date.replace("        ","")
    date=date.split("(PST)")[0]
    return date
def post(num,date):
    txt="""{{fontcolor|green|'''Last message without a reply''':}} %s
<br />{{fontcolor|green|'''Current number of messages that need reply''':}} %s
<br />{{fontcolor|green|I have a light work week and some <br />things going on, replies to messages <!--will be delayed--><br />will likely get a response within 24 hours.}}
<small><br />If your message came on or after this date, your email is still being
<br />attended to. If the date passes and you don't receive a reply, let me know.</small>
""" % (str(date),str(num))
    print txt
    summary = "[[User:"+localconfig.botname+"|"+localconfig.botname+"]] "+ localconfig.primarytaskname
    site = wikipedia.getSite()
    pagename = localconfig.postpage
    page = wikipedia.Page(site, pagename)
    pagetxt = page.get()
    page.put(txt, comment=summary)
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(localconfig.email,localconfig.password)
mail.select("Inbox",readonly=True)
listNums=' '.join(mail.search(None, "UnSeen")[1]).split(" ")
num=len(listNums)
date=getMsgDate(listNums[0])
post(num,date)
mail.close()
mail.logout()


