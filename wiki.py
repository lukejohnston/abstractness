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

    comment = soup.find(text=re.compile("bodytext"))
    sibs = comment.findNextSiblings('p')
    count = 0
    links = None

    while True:
        if count >= len(sibs):
            links = comment.findAllNext('a')
            opens = comment.findAllPrevious(text=re.compile("\("))
            closes = comment.findAllPrevious(text=re.compile("\)"))
        else:
            links = sibs[count].findAll('a')
            opens = sibs[count].findAllPrevious(text=re.compile("\("))
            closes = sibs[count].findAllPrevious(text=re.compile("\)"))
        count += 1
        done = False
        if links:
            for j in links:
                print j
                opens = len(j.findAllPrevious(text=re.compile("\("))) 
                print "%d open brackets before" % opens
                closes = len(j.findAllPrevious(text=re.compile("\)"))) 
                print "%d close brackets before" % closes
                if "Wikipedia:" in j['href']:
                    continue
                elif "cite_note" in j['href']:
                    continue
                elif "Wiktionary" in j['href']:
                    continue
                elif not j['href'].startswith(url_prefix):
                    continue
                elif j.get('class'):
                    continue
                elif not j.findPrevious(text=re.compile("\(")):
                    done = True
                    break
                elif (len(j.findAllPrevious(text=re.compile("\("))) - opens) ==\
                    (len(j.findAllPrevious(text=re.compile("\)"))) - closes):
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
