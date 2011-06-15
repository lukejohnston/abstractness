#A couple of functions for finding the first link on a wikipedia page that
#is not in parenthesis or italics.

from BeautifulSoup import BeautifulSoup
if __name__=="__main__":
    import urllib2
else:
    from google.appengine.api.urlfetch import fetch
import sys
import re

if __name__=="__main__":
    url_prefix = "/wikipedia/en/wiki"
else:
    url_prefix = "/wiki"

#Need to make wikipedia think we're a real browser otherwise we get 403s
agent = "Mozilla/5.0 (X11; Linux x86_64; rv:2.0.1) Gecko/20110506 Firefox/4.0.1"

reBodytext = re.compile("bodytext")
reOpenPar = re.compile("\(")
reClosePar = re.compile("\)")

class NotFoundException(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Page not found: " + self.name

def valid_link(j):
    """Returns True if j is the type of link we're looking for"""

    if "Wikipedia:" in j['href']:
        return False
    elif "cite_note" in j['href']:
        return False
    elif "Wiktionary" in j['href']:
        return False
    elif "File:" in j['href']:
        return False
    elif not j['href'].startswith(url_prefix):
        return False
    elif j.parent.name == 'i':
        return False
    elif j.parent.name == 'span':
        return False
    else:
        return True

def find_next_article(name):
    """Start at the wikipedia article name, find the first link not in 
    parenthesis or italics and return the name of that page.

    Raises a NotFoundException if there is no page on Wikipedia with that name
    """
    #Grab the html and make soup
    if __name__=="__main__":
        url = "https://secure.wikimedia.org/wikipedia/en/wiki/" + name
        f = urllib2.urlopen(url)
        html = f.read()
    else:
        url = "http://en.wikipedia.org/wiki/" + name
        res = fetch(url, headers={'UserAgent' : agent})
        html = res.content
    soup = BeautifulSoup(html)

    #Not a real page
    if "Wikipedia does not have an article with this exact name" in str(soup):
        raise NotFoundException(name)

    #Start our search at the start of the body text
    comment = soup.find(text=reBodytext)
    sibs = comment.findNextSiblings('p')
    count = 0
    links = None

    while True:
        #Find the links in each paragraph and check them, try the rest of the 
        #page once the paragraphs have been checked
        if count >= len(sibs):
            links = comment.findAllNext('a')
        else:
            links = sibs[count].findAll('a')

        count += 1

        if not links:
            continue

        for j in links:
            #Check that the brackets are balanced
            jopens = j.findAllPrevious(text=reOpenPar)
            jcloses = j.findAllPrevious(text=reClosePar)
            opencounts = [str(i).count("(") for i in jopens]
            closecounts = [str(i).count(")") for i in jcloses]
            opentotal = sum(opencounts)
            closetotal = sum(closecounts)

            if valid_link(j) and opentotal == closetotal:
                return j['href'].split("/")[-1]

if __name__=="__main__":
    name = sys.argv[1]
    count = 0

    while(name != "Philosophy"):
        sys.stdout.write(name + " --> ")
        sys.stdout.flush()
        name = find_next_article(name)
        count += 1
    sys.stdout.write("Philosophy\n\n")
    print "Got to philosophy in %d steps" % (count)
