import csv
from google.appengine.ext import ndb
from google.appengine.ext.webapp import util
from google.appengine.ext import webapp
import os
from site_db import models
from site_db import properties


class ReloadFromCSV(webapp.RequestHandler):

  QueryOptions = ndb.QueryOptions(keys_only=True)

  def _delete_class(self, cls):
    for k in cls.Query(default_options=ReloadFromCSV.QueryOptions).fetch():
      k.delete()

  def get(self):
    self.response.write(os.environ.get('HTTP_HOST'))

def main():
  application = webapp.WSGIApplication([
      ('/reload.*', ReloadFromCSV)
      ], debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
