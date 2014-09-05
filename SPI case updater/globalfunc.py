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
    if ctype=="endorse":return getCurrentCases('SPI cases awaiting a CheckUser‎')
    if ctype=="open":return getCurrentCases('SPI cases awaiting administration‎')
    if ctype=="ADMIN":return getCurrentCases('SPI requests needing an Administrator‎')
    if ctype=="hold":return getCurrentCases('SPI cases currently in progress‎')
    if ctype=="curequest":return getCurrentCases('SPI requests for pre-CheckUser review‎')
    if ctype=="close":return getCurrentCases('SPI cases pending close‎')

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
        if "archive" in revision["comment"].lower():
            return revisions[i-1]["user"],revisions[i-1]["timestamp"]
        else:
            last = revisions.pop()
            return [last["user"],last["timestamp"]]
        i+=1
def getLastEdit(title):
    last = getHistory(title).pop()
    return [last["user"],last["timestamp"]]
def getLastClerk(title):
    revisions = getHistory(title)
    while True:
        try:last = revisions[0]
        except:return "None"
        #except:return ""
        site = wikipedia.getSite()
        pagename = "User:DeltaQuad/Clerks list"
        page = wikipedia.Page(site, pagename)
        clerks = page.get()
        if last["user"] in clerks:
            return last["user"]
        revisions = revisions.remove(last)
    return "None"
    

def formatTableRow(case, status,filer,dateFiled,lastEdit,timestamp,lastClerk):
    return "{{SPIstatusentry|" + case + "|" + status + "|" + filer + "|" + dateFiled + "|" + lastEdit + "|" + timestamp + "|" + lastClerk +"}}"

def caseProcessor():
    table="""
{|class="wikitable sortable" width="100%"
!Investigation!!Status!!Date filed!!Last user to edit case!!timestamp!!Last clerk/checkuser to edit case!!timestamp
|-
"""
    caseTypes=["endorse","curequest","ADMIN","open","hold","close"]
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

            dateFiled=filer[1]
            filer = filer[0]
            timestamp = lastEdit[1]
            lastEdit = lastEdit[0]
            table+=formatTableRow(case.split("/")[1],entry,filer,dateFiled,lastEdit,timestamp,lastClerk)+"\n"
    table+="|}"
    site = wikipedia.getSite()
    pagename = "User:DeltaQuad/Clerks list"
    page = wikipedia.Page(site, pagename)
    print table
    page.put(table, comment="Updating SPI caselist")
caseProcessor()
