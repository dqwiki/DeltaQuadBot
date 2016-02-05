# -*- coding: utf-8 -*-
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
import pywikibot
from pywikibot.data import api

useWiki= pywikibot.Site('en','wikipedia')

def callAPI(params):
    req = api.Request(useWiki, **params)
    return req.submit()

def getCurrentCases(category):
    category = "Category:" + category
    site= pywikibot.getSite()
    params = {'action': 'query',
        	'list': 'categorymembers',
        	'cmtitle': category,
                'cmnamespace':'4',
                'cmlimit':'500',
                'format':'json',
                'rawcontinue':'1'
                }
    raw = callAPI(params)
    reg = raw["query"]["categorymembers"]
    reg = formatArray(reg)
    return reg

def getCurrentCasesBeta():
    print "Null"

def formatArray(database):
    i = 0
    cases = []
    for entry in database:
        cases = cases + [entry["title"]]
    return cases

def getAllCases(ctype):
    if ctype=="inprogress":return getCurrentCases('SPI cases currently being checked')
    if ctype=="endorsed":return getCurrentCases('SPI cases awaiting a CheckUser‎')
    if ctype=="relist":return getCurrentCases('SPI cases relisted for a checkuser')
    if ctype=="curequest":return getCurrentCases('SPI cases requesting a checkuser‎')
    if ctype=="checked":return getCurrentCases('SPI cases CU complete')
    if ctype=="ADMIN":return getCurrentCases('SPI cases needing an Administrator')
    if ctype=="declined":return getCurrentCases('SPI cases declined for checkuser by clerk‎')
    if ctype=="cudeclined":return getCurrentCases('SPI cases declined for checkuser by CU‎')
    if ctype=="open":return getCurrentCases('SPI cases awaiting review‎')
    if ctype=="moreinfo":return getCurrentCases('SPI cases requesting more information‎')
    if ctype=="hold":return getCurrentCases('SPI cases on hold by clerk‎')
    if ctype=="cuhold":return getCurrentCases('SPI cases on hold by checkuser‎')
    if ctype=="close":return getCurrentCases('SPI cases awaiting archive‎')

def getHistory(title):
    site= pywikibot.getSite()
    params = {'action':'query',
              'prop':'revisions',
              'titles':title,
              'rvlimit':'500',
              'rvprop':'timestamp|user|comment|size',
              'format':'json',
              'rawcontinue':'1'}
    history = callAPI(params)
    full = history["query"]["pages"]
    for singleid in full:
        pageid = singleid
    history = history["query"]["pages"][pageid]['revisions']
    return history
def getFiler(revisions):
        i=0
        for revision in revisions:
                try:
                        if "archiv" in revision["comment"].lower():# or "archiving" in revision["comment"].lower():
                                return revisions[i-1]["user"],revisions[i-1]["timestamp"]
                except:
                        null=1 #nullifier due to "commenthidden"
                i+=1
        last = revisions.pop()
        return [last["user"],last["timestamp"]]
                
def getLastEdit(title):
    history=getHistory(title)
    last = history[0]
    return [last["user"],last["timestamp"]]
def getLastClerk(title):
    revisions = getHistory(title)
    i=0
    while True:
        #print '-----------------------------------------'
        try:last = revisions[i]
        except:
                #print "!!!!NO!!!!"
                return "None"
        #except:return ""
        #print "Last: "
        #print last
        site = pywikibot.getSite()
        pagename = "User:DeltaQuad/Clerks list"
        page = pywikibot.Page(site, pagename)
        clerks = page.get()
        try:
                if "archive" in last["comment"].lower() or "archiving" in last["comment"].lower():
                    return "None"
                if last["user"] in clerks:
                    return last["user"]
        except:
                null=1#placeholder
        i+=1
    return "None"
    

def formatTableRow(case, status,filer,dateFiled,lastEdit,timestamp,lastClerk):
    return "{{SPIstatusentry|" + case + "|" + status + "|" + filer + "|" + dateFiled + "|" + lastEdit + "|" + timestamp + "|" + lastClerk +"}}"

def caseHistoryCompile(caseTypes):
        table=""
        for entry in caseTypes:
                caselist=getAllCases(entry)
                if caselist == None:
                    continue
                for case in caselist:
                    history=getHistory(case)
                    historyDup=history
                    filer=getFiler(history)
                    lastEdit=getLastEdit(case)
                    lastClerk=getLastClerk(case)
                    if lastClerk=="None":lastClerk=""

                    dateFiled=filer[1]
                    filer = filer[0]
                    timestamp = lastEdit[1]
                    lastEdit = lastEdit[0]
                    if len(filer)>30:filer="[[User:"+filer+"|An IPv6 address]]"
                    else:filer="[[User:"+filer+"|"+filer+"]]"
                    if len(lastEdit)>30:lastEdit="[[User:"+filer+"|An IPv6 address]]"
                    else:lastEdit="[[User:"+lastEdit+"|"+lastEdit+"]]"
                    try:table+=formatTableRow(case.split("/")[1],entry,filer,dateFiled,lastEdit,timestamp,lastClerk)+"\n"
                    except:
                            print 'Main SPI page ignored'
        return table

def addHeader(name):
        return "\n== "+name+" ==\n"

def makeTable(content):
        tabletop="""
{|class="wikitable sortable" width="100%"
!Investigation!!Status!!Filer!!Date filed!!Last user to<br /> edit case!!timestamp!!Last clerk/CU<br /> to edit case
|-
"""
        tablebottom="|}"
        return tabletop + content + tablebottom
def caseProcessor():
    print "CU results table"
    categories=["checked"]
    cursftable = addHeader("CU Result Cases")+makeTable(caseHistoryCompile(categories))
    print "!!!DONE!!!"
    print "CU endorsed table"
    categories=["endorsed","relist"]
    cueftable = addHeader("CU Endorsed Cases")+makeTable(caseHistoryCompile(categories))
    print "!!!DONE!!!"
    print "CU review table"
    categories=["curequest"]
    curftable = addHeader("CU Review Cases")+makeTable(caseHistoryCompile(categories))
    print "!!!DONE!!!"
    print "CU decline table"
    categories=["declined","cudeclined"]
    cudftable = addHeader("CU Declined Cases")+makeTable(caseHistoryCompile(categories))
    print "!!!DONE!!!"
    print "Open table"
    categories=["open"]
    oftable = addHeader("Open Cases")+makeTable(caseHistoryCompile(categories))
    print "!!!DONE!!!"
    print "Wait table"
    categories=["inprogress","ADMIN","moreinfo","hold","cuhold"]
    wftable = addHeader("Waiting Cases")+makeTable(caseHistoryCompile(categories))
    print "!!!DONE!!!"
    print "Archive table"
    categories=["close"]
    arcftable = addHeader("To Archive Cases")+makeTable(caseHistoryCompile(categories))
    print "!!!DONE!!!"
    print "Processing master table..."
    
    final = cursftable + cueftable + curftable + cudftable + oftable + wftable + arcftable
    print "!!!DONE!!!"
    print "----POSTING----"
    site = pywikibot.getSite()
    pagename = "User:DeltaQuad/SPI case list"
    page = pywikibot.Page(site, pagename)
    page.put(final, comment="Updating SPI caselist")
    print "!!!DONE!!!"
caseProcessor()
