#mydir = "C:\\"
#pwbdir = mydir + "pywikipedia\\"
pwbdir = "/home/deltaquad/pywikipedia/pywikipedia"
import sys
sys.path.append(pwbdir)
from wikipedia import *
import voterlist
from collections import defaultdict
import re
import traceback
from time import strftime, gmtime, sleep

site = wikipedia.getSite()
page = 'Wikipedia:Arbitration Committee Elections December 2012/Log'
thepage = wikipedia.Page(site, page)

def timestamp():
    return strftime("%H:%M (UTC) %d %b %Y", gmtime())

def current_page_text():
    return thepage.get()#.decode('utf-8')

def update_page(pagetext):
    votes = voterlist.get_voter_list()
    names = set(vote['name'] for vote in votes)
    lines = pagetext.split(u'\n')
    
    named_lines = defaultdict(list)
    current_name = '[TOP]'
    for line in lines:
        replace = False
        if line.startswith(u'{{div col end}}'):
            current_name = '[BOTTOM]'
        elif current_name != '[BOTTOM]':
            name_match = re.search(r"\{\{UserEL\|([^}]+)\}\}", line)
            if name_match:
                if name_match.group(1) not in names:
                    current_name = '[UNKNOWN]'
                else:
                    current_name = name_match.group(1)
                    if current_name in named_lines: replace=True
        if replace:
            # don't replace struck-out or indented votes
            if named_lines[current_name][0].startswith('# '):
                named_lines[current_name][0] = line
        else:
            named_lines[current_name].append(line)
    
    outlines = named_lines['[TOP]']

    used_names = set()
    for vote in votes:
        name = vote['name']
        if name not in used_names:
            if name in named_lines:
                outlines.extend(named_lines[name])
                used_names.add(name)
            else:
                outlines.append(voterlist.format_voter_info(vote))
                used_names.add(name)

    found_orphaned = False
    outlines.extend(named_lines['[BOTTOM]'])
    if '[UNKNOWN]' in named_lines:
        if not u'=== Orphaned comments ===' in named_lines['[BOTTOM]']:
            outlines.append(u'=== Orphaned comments ===')
        outlines.extend(named_lines['[UNKNOWN]'])
    for i in xrange(len(outlines)):
        if re.search("== ?Log as", outlines[i]):
            outlines[i] = "== Log as of %s ==" % timestamp()
    return ('\n'.join(outlines))#.encode('utf-8')

def commit(newtext):
    #print newtext
    thepage.put(
      newtext,
      u"BOT: Updating voter list"
    )

def run_example():
    print update_page(current_page_text())

def run_once():
    commit(update_page(current_page_text()))

def run():
    try:
        run_once()
    except Exception, e:
        traceback.print_exc()
    print "Updated at", gmtime()[:6]

if __name__ == '__main__': run()

