#!/usr/bin/python
# -*- coding: utf-8 -*-
#$ -l h_rt=168:0:00
#$ -j y
#$ -o $HOME/mytool.out

#Global Variables
baseuser = "User:DeltaQuad"
username = "DeltaQuad"
botuser = "User:DeltaQuadBot"
botname = "DeltaQuadBot"
 
########################################
########################################
# Routines for typo patrol
########################################
 
def store_warning(type,param):
# compiles warnings to send to user
 
    global user_warning
 
    if type == "not contained":
        if user_warning != "":
            user_warning = user_warning + "; "
        user_warning = user_warning + "search phrase is not contained in safe phrase \""+param+"\""
 
########################################
 
def give_warning():
# delivers stored user warning if any
 
    global user_warning, my_username, warning_page
 
    if user_warning != "":
        user_warning = "==Warning from " + my_username + "==\n" + my_username + " has the following warning: " + user_warning + ". ~~~~"
 
        print user_warning
 
########################################
 
def perform_search(search_phrase,safe_page_list,safe_phrase_list):
# finds all pages matching search_phrase not contained in any element of safe_phrase_list, and where the page is not on safe_page_list. also returns number of pages processed, and number ignored due to containing safe phrases.
 
    print "Performing search for \"" + search_phrase + "\". Max number of pages is " + str(max_pages) + ". Pages processed:"
 
    num_total = 0
    num_safe_phrase = 0
    num_safe_page = 0
 
    regexp_list = []
    for safe_phrase in safe_phrase_list:
 
        # check that the safe_phrase contains the search_phrase
        if re.search(search_phrase,safe_phrase,re.IGNORECASE):
 
            # split the prepend and append from the safe phrase, ignoring repeats
            # e.g. search_phrase "b" and safe_phrase "abcbd" gives prepend "a" and append "cbd"
            split_list = safe_phrase.partition(search_phrase)
            prepend = split_list[0]
            append = split_list[2]
 
            # create regular expression which matches any occurence of search_phrase not contained within safe_phrase
            regexp_string = "(((?<!"+prepend+")"+search_phrase+")|("+search_phrase+"(?!"+append+")))"
            safe_regexp = re.compile(regexp_string,re.IGNORECASE)
            regexp_list.append(safe_regexp)
 
        # if safe phrase is empty, we don't care
        elif safe_phrase == "":
            pass
 
        # any other safe phrase is an error
        else:
            store_warning("not contained",safe_phrase)
 
    # returns a generator function with search results
    search_results = site.search("\""+search_phrase+"\"","0|10|100",number=1e10)
 
    checked_search_results = []
    num_returned = 0
 
    try:
        while num_returned < max_pages:
        #while num_total == 0: # zzzz
            # check for regexp match on each search result
            result = search_results.next()
            page = result[0]
 
            try:
                page_is_safe = False
                # first check if this is a 'safe page'
                if safe_page_list.count(page.title()) > 0:
                    page_is_safe = True
                    num_safe_page += 1
                else:
                    # now check if search term appears only in safe phrases
                    pagetext = page.get()
                    for safe_regexp in regexp_list:
                        if not(safe_regexp.search(pagetext)):
                            page_is_safe = True
                    if page_is_safe:
                        num_safe_phrase += 1
                if not page_is_safe:
                    checked_search_results.append(page.title())
                    num_returned += 1
                    if (num_returned % 10) == 0:
                        print (num_returned)
                num_total += 1
            except IsRedirectPage:
                print ("(Ignoring redirect)")
 
    #catch end of search
    except StopIteration:
        pass
 
    print (num_total, num_safe_page, num_safe_phrase, num_returned)
 
    return checked_search_results, (num_total, num_safe_page, num_safe_phrase, num_returned)
 
########################################
 
def read_section_as_string_or_list(section_name,section_level,pagename,list):
# gets a string or list containing the lines in section section_name on page pagename. section_level should be a string containing the appropriate number of = signs. list should be True to get output as a list.
 
    page = Page(site,pagename)
    pagetext = page.get()
 
    # first get everything from header downwards
    header = section_level+section_name+section_level
    split_list = pagetext.partition(header)
    section_and_below = split_list[2]
 
    # now look for next header and drop everything below it
    # (if no more headers, it will go to end of the page)
    header = section_level
    split_list = section_and_below.partition(header)
    section = split_list[0]
 
    # convert to list if desired
    if (list):
        output_list = section.splitlines()
 
        # remove blanks
        while output_list.count("") > 0:
            output_list.remove("")
 
        return output_list
    else:
        return section
 
########################################
 
def typo_patrol(search_phrase,safe_pages_pagename,safe_phrases_pagename):
# performs a patrol for pages containing search_phrase, taking safe phrases and pages into account. second and third inputs tell it where to search for safeties. returns list of page names and number of pages containing phrase, number dropped due to safe phrase, and number dropped due to being safe pages.
 
    # read safe pages and phrases from user subpages
    safe_phrase_list = read_section_as_string_or_list("Safe phrases","===",safe_phrases_pagename,True)
    safe_page_list = read_section_as_string_or_list("Safe pages","===",safe_pages_pagename,True)
 
    # strip leading/trailing spaces and wikilink from page names
    for i,string in enumerate(safe_page_list):
        safe_page_list[i] = string.strip('][ ')
 
    # search for occurences outside safe phrases, pages
    search_results, numbers = perform_search(search_phrase,safe_page_list,safe_phrase_list)
 
    return search_results, numbers
 
########################################
 
def report_patrol_results(results,numbers,search_phrase,pagename,user_warning):
# outputs results of patrol, including warning and wikilinks for articles
 
    page = Page(site,pagename)
    print ("Saving report to " + pagename)
    if readonly_mode:
        pagetext = ""
    else:
        pagetext = page.get()
    newtext = pagetext + "\n===Typo Patrol results for \""+search_phrase+"\"==="
    newtext = newtext + "\n" + str(numbers[0]) + " pages containing the phrase were processed in total. " + str(numbers[1]) + " were on the safe page list and " + str(numbers[2]) + " were deemed safe using the safe phrases; the remainder are listed below."
    if numbers[3] < max_pages:
        newtext = newtext + " All pages were processed."
    else:
        newtext = newtext + " Maximum page number was reached so additional hits may exist."
    if user_warning != "":
        newtext = newtext + "\nWarning: " + user_warning
    newtext = newtext + " ~~~~~"        # date
    for item in results:
        newtext = newtext + "\n*[[" + item + "]]"
 
    setAction("Patrol results for \""+search_phrase+"\"")
    if readonly_mode:
        print(newtext)
    else:
        page.put(newtext)
 
########################################
########################################
# Main program
########################################
 
def get_all_job_requests(pagename,request_template_name):
# gets an iterator containing all new jobs from job request page
 
    jobs_section = read_section_as_string_or_list("Job requests","==",pagename,False)
    # find a job using regexpressions to scoop out template interior
    # DOTALL makes . match newlines too
    regexp = re.compile("\{\{"+request_template_name+"(.*?)\}\}",re.DOTALL)
    results_list = regexp.finditer(jobs_section)    
    print results_list.next()
    return(results_list)
 
########################################
 
def get_next_job(jobs_iterator):
# gets next job from the iterator and returns [search_phrase,safe_pagename,results_pagename]

    try:
        job = jobs_iterator.next()
        if(job):
            parameters = job.group(1)
            # now look for parameter names and get values after them
            regexp = re.compile("\|phrase *= *\"(.*?)\"[ \n]*\|safe_page *= *(.*?)\n*\|results_page *= *(.*)\n*")
            result = regexp.search(parameters)
            new_job = result.group(1,2,3)
        else:
            new_job = []
        return new_job
    except:
        return "DONE"
 
########################################
 
def remove_job_request(pagename,request_template_name):
# removes job request template from open requests section and adds it to completed requests section on pagename (ACTUALLY, to the END of the page regardless)
 
    jobs_section = read_section_as_string_or_list("Job requests","==",pagename,False)
 
    # find a job using regexpressions to scoop out template interior
    # DOTALL makes . match newlines too
    regexp = re.compile("\{\{"+request_template_name+"(.*?)\}\}",re.DOTALL)
    result = regexp.search(jobs_section)
 
    # remove this template instance, and following newlines, add it end to end of the page, and save page
    if (result):
        page = Page(site,pagename)
        pagetext = page.get()
        parameters = result.group(1)
        text_to_remove = "{{"+request_template_name+parameters+"}}"
        split_list = pagetext.partition(text_to_remove)
        new_pagetext = split_list[0] + split_list[2].lstrip("\n")
        new_pagetext = new_pagetext + "\n\n" + "{{"+request_template_name+parameters+"}}"
        setAction("Moving completed job request to end of page.")
        if not(readonly_mode):
                page.put(new_pagetext)
 
########################################
 
def reset_job_list(pagename):
# swaps job request list and completed list
 
    page = Page(site,pagename)
    pagetext = page.get()
 
    # look for completed requests header
    header = "\n==Completed requests==\n"
    split_list = pagetext.partition(header)
 
    # reorder so header comes at end
    new_pagetext = split_list[0]+split_list[2]+split_list[1]
 
    if not(readonly_mode):
        page.put(new_pagetext)
 
 
########################################
 
# initialisation
 
# import wikipedia modules
pwbdir = "C:\\pywikipedia\\"
#pwbdir = "/home/deltaquad/pywikipedia/pywikipedia"
import sys
sys.path.append(pwbdir)
from wikipedia import *
from userlib import *
 
# setup site as enwiki
language = "en"
family = "wikipedia"
site = getSite(language,family)
 
# these determine where to find pages on wiki, and who to email about errors
my_username = botuser
operator_username = username
job_requests_pagename = botuser +"/Job requests"
request_template_name = baseuser + "/Templates/Request"
print request_template_name
 
# import regular expressions
from re import *
 
# ==============================
# these can be changed for testing
# defaults are remove_old_jobs = give_results = True and max_jobs = 100

max_pages = 50# most pages to process (actually counts pages after safe phrase removal but before safe list)
remove_old_jobs = True # NOTE: do not set to false if max_jobs > 1!
max_jobs = 100
give_results = True
readonly_mode = False # usually False; if true, print to screen instead of saving pages
# ==============================
 
done = False
jobs_completed = 0
 
jobs_iterator = get_all_job_requests(job_requests_pagename,request_template_name)
while not done:
 
    # warning message for operator's talk page
    user_warning = ""
 
    # check for a job request
    new_job = get_next_job(jobs_iterator)
    if new_job == "DONE":
        print "No new jobs."
        done = True    
    else:
 
        [search_phrase,safe_pagename,results_pagename] = new_job
 
        # patrol for this typo
        patrol_results, numbers = typo_patrol(search_phrase,safe_pagename,safe_pagename)
 
        # check numbers of pages add up
        (num_total, num_safe_page, num_safe_phrase, num_returned) = numbers
        if (num_returned + num_safe_page + num_safe_phrase == num_total):
 
            # give report on patrol
            if (give_results):
                report_patrol_results(patrol_results,numbers,search_phrase,results_pagename,user_warning)
 
            if (remove_old_jobs):
                # remove completed job request
                remove_job_request(job_requests_pagename,request_template_name)
 
            # deliver any warnings generated for operator
            give_warning()
 
            jobs_completed += 1
            if (jobs_completed >= max_jobs):
                print ("Max jobs reached: "+str(jobs_completed))
                done = True
 
        else:
            print ("Error: inconsistent number of pages. Results not written.")
            print num_returned, num_safe_page, num_safe_phrase, num_total
            done = True
 
# reset job list by swapping completed requests and new requests headers
reset_job_list(botuser + "/Job requests")
 
print botname+ " done. " + str(jobs_completed) + " jobs completed."
