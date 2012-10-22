from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from site_db import models
from site_db import properties

class RESTfulAPI(webapp.RequestHandler):
  def __init__(self, request, response):
    super(RESTfulAPI, self).initialize(request, response)
    self.request.path_info_pop()
    self.requested_api = self.request.path_info_pop()
    self.api_key = None
    self.uri_keys = []
    self.uri_map = {}

  def _validate(self):
    if self.requested_api != self.api_key:
      self.abort(400, ("Requested Handler %s didn't"
                       "match api handler %s") % (self.requested_api,
                                                  self.api_key))

  def _map_uri_keys(self):
    for k in self.uri_keys:
      self.uri_map[k] = self.request.path_info_pop()

  def get(self):
    self._validate()
    self._map_uri_keys()
    self._get()

  def _get(self):
    pass

  def put(self):
    pass

class VenueAPI(RESTfulAPI):
  def __init__(self, request, response):
    super(VenueAPI, self).__init__(request, response)
    self.api_key = 'venue'
    self.uri_keys.append('key_name')

  def _get(self):
    q = models.Venue.query()
    for v in q.fetch():
      print v
    v=models.Venue(display_name='ThinkTank Bistro')
    v.key=ndb.Key('Venue','ThinkTankBistro')
    print v
    v.id = v.display_name
    v.put()
    print v.key

def main():
  application = webapp.WSGIApplication([
      ('/data/venue.*', VenueAPI)
      ], debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
