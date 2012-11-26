from BeautifulSoup import BeautifulSoup
import urllib2

def get_page(url):
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'ArbCom Voting Module - Python BOT. Built on pywikipedia. Coded for DeltaQuadBot on enwikipedia.')
    opener = urllib2.build_opener()
    data = opener.open(request).read()
    return BeautifulSoup(data)

base_url = "http://en.wikipedia.org/wiki/Special:SecurePoll/list/130"

def find_voter_info(row):
    stuff = {}
    p = row.find('td', 'TablePager_col_vote_voter_name').a['title']
    assert p.startswith('User:')
    if p.endswith(' (page does not exist)'):
        p = p.partition(' (page does not exist)')[0]
    stuff['name'] = p[5:]
    timestamp = row.find('td', 'TablePager_col_vote_timestamp').string
    stuff['timestamp'] = timestamp
    stuff['dupe'] = True
    return stuff

def format_voter_info(info):
    return u"# {{User|%s}} %s" % (info['name'], info['timestamp'])

def get_votes(page):
    table = page.find('table', {'class': 'TablePager'})
    rows = table.tbody.findAll('tr')
    voter_info = []
    for row in rows:
        #if row['class'] == '':
        voter_info.append(find_voter_info(row))
    return voter_info

def recursive_get_votes(url):
    print "Getting", url
    page = get_page(url)
    votes = get_votes(page)
    nexttag = page.find('a', 'mw-nextlink', rel='next')
    if nexttag:
        dest = nexttag['href']
        return votes + recursive_get_votes("http://en.wikipedia.org"+dest)
    else:
        return votes

def get_voter_list():
    return sorted(recursive_get_votes(base_url))

def full_output():
    voters = get_voter_list()
    return '\n'.join(format_voter_info(v) for v in voters if not v['dupe'])

def main():
    print full_output()

if __name__ == '__main__': main()
