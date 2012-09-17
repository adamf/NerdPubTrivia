#!/usr/bin/env python
#
import datetime
import time
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.dist import use_library
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
use_library('django', '1.3')
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

class TestModel(ndb.Model):
  pass

class BaseHandler(webapp.RequestHandler):
  def get_string(self,request_key,default_value=None):
    if self.request.get(request_key).strip():
      return self.request.get(request_key).strip()
    else:
      return default_value

  def render_template(self,template_file,template_values={}):
    template_path = os.path.join(os.path.dirname(__file__),
                                 'templates',template_file)
    self.response.out.write(template.render(template_path,
                                            template_values))

class TestHandler(BaseHandler):
  def get(self):
    self.render_template('test.html')
  def post(self):
    pass

def main():
  application = webapp.WSGIApplication([
      ('/test/test', TestHandler)
      ],debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
