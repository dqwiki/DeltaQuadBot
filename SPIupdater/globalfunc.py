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
import wikipedia
import userlib

def getCurrentCases(category):
    category = "Category:" + category
    site= wikipedia.getSite()
    params = {'action': 'query',
        	'list': 'categorymembers',
        	'cmtitle': category,
                'cmnamespace':'4',
                'cmlimit':'500',
                'format':'json'
                }
    response, raw = site.postForm(site.apipath(), params)
    result = json.loads(raw)
    reg = result["query"]["categorymembers"]
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
    site= wikipedia.getSite()
    params = {'action':'query',
              'prop':'revisions',
              'titles':title,
              'rvlimit':'500',
              'rvprop':'timestamp|user|comment|size',
              'format':'json'}
    response, raw = site.postForm(site.apipath(), params)
    history = json.loads(raw)
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
                print "!!!!NO!!!!"
                return "None"
        #except:return ""
        #print "Last: "
        #print last
        site = wikipedia.getSite()
        pagename = "User:DeltaQuad/Clerks list"
        page = wikipedia.Page(site, pagename)
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

def caseProcessor():
    table="""
{|class="wikitable sortable" width="100%"
!Investigation!!Status!!Filer!!Date filed!!Last user to<br /> edit case!!timestamp!!Last clerk/CU<br /> to edit case
|-
"""
    caseTypes=["inprogress","endorsed","relist","curequest","checked","ADMIN","declined","cudeclined","open","moreinfo","hold","cuhold","close"]
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
    table+="|}"
    site = wikipedia.getSite()
    pagename = "User:DeltaQuad/SPI case list"
    page = wikipedia.Page(site, pagename)
    page.put(table, comment="Updating SPI caselist")
caseProcessor()
