#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import os
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from wiki import find_next_article


class MainHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, {}))

class Article(db.Model):
    nextArticle = db.StringProperty()

def article_key(article):
    return db.Key.from_path('Article', article)

def get_from_db(name):
    articles = Article.gql("WHERE ANCESTOR IS :1", article_key(name))
    result = articles.get()
    if result:
        return result.nextArticle

def put_in_db(name, nextname):
    article = Article(parent=article_key(name))
    article.nextArticle = nextname
    article.put()

class WikiAbstractness(webapp.RequestHandler):
    def post(self):
        name = self.request.get('article')
        count = 0
        names = []
        loop = False
        
        while(name != "Philosophy"):
            if name in names:
                names.append(name)
                loop = True
                break
            names.append(name)
            nextname = get_from_db(name)
            if not nextname:
                nextname = find_next_article(name)
                put_in_db(name, nextname)
            count += 1
            name = nextname

        template_values = {
            'names' : names,
            'count' : count,
            'loop' : loop
        }

        path = os.path.join(os.path.dirname(__file__), 'get.html')
        self.response.out.write(template.render(path, template_values))

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/get', WikiAbstractness)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
