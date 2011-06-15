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
agent = "Mozilla/5.0 (X11; Linux x86_64; rv:2.0.1) Gecko/20110506 Firefox/4.0.1"

reBodytext = re.compile("bodytext")
reOpenPar = re.compile("\(")
reClosePar = re.compile("\)")

class NotFoundException(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Page not found: " + self.name

def find_next_article(name):
    if __name__=="__main__":
        url = "https://secure.wikimedia.org/wikipedia/en/wiki/" + name
        f = urllib2.urlopen(url)
        html = f.read()
    else:
        url = "http://en.wikipedia.org/wiki/" + name
        res = fetch(url, headers={'UserAgent' : agent})
        html = res.content
    soup = BeautifulSoup(html)

    if "Wikipedia does not have an article with this exact name" in str(soup):
        raise NotFoundException(name)

    comment = soup.find(text=reBodytext)
    sibs = comment.findNextSiblings('p')
    count = 0
    links = None

    while True:
        if count >= len(sibs):
            links = comment.findAllNext('a')
        else:
            links = sibs[count].findAll('a')
        count += 1
        done = False
        if links:
            for j in links:
                jopens = j.findAllPrevious(text=reOpenPar)
                jcloses = j.findAllPrevious(text=reClosePar)
                opencounts = [str(i).count("(") for i in jopens]
                closecounts = [str(i).count(")") for i in jcloses]
                opentotal = sum(opencounts)
                closetotal = sum(closecounts)

                if "Wikipedia:" in j['href']:
                    continue
                elif "cite_note" in j['href']:
                    continue
                elif "Wiktionary" in j['href']:
                    continue
                elif "File:" in j['href']:
                    continue
                elif not j['href'].startswith(url_prefix):
                    continue
                elif j.parent.name == 'i':
                    continue
                elif j.parent.name == 'span':
                    continue
                elif opentotal == closetotal:
                    done = True
                    break
        if done:
            break
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
