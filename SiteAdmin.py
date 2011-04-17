#!/usr/bin/env python
#
import datetime
import time
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.dist import use_library
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
use_library('django', '1.2')
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from site_db import models


class DeleteHandler(webapp.RequestHandler):
    def get(self):
        db.Model.get(db.Key(self.request.get('edit'))).delete()
        self.redirect(self.request.environ['HTTP_REFERER'])

class VenueHandler(webapp.RequestHandler):
    def get(self):
        edit_key = self.request.get('edit',None)
        venues = models.Venue.all().fetch(100)
        if not edit_key is None:
            edit_venue = [v for v in venues if (("%s" % v.key()) == edit_key)][0]
        else:
            edit_venue = None
        template_values = { 'venues': venues, 'edit_key': edit_key, 'edit_venue': edit_venue }
        path = os.path.join(os.path.dirname(__file__), 'templates/venue.html')
        self.response.out.write(template.render(path,template_values))
        
    def post(self):
        v = self.request.get('vname').strip()
        if v:
            venue = models.Venue(venue_name=v)
            if self.request.get('vaddress').strip():
                venue.venue_address = self.request.get('vaddress').strip()
            else:
                venue.venue_address = None
            if self.request.get('cemail').strip():
                venue.venue_contact_email = self.request.get('cemail').strip()
            else:
                venue.venue_contact_email = None
            if self.request.get('cphone').strip():
                venue.venue_contact_phone = self.request.get('cphone').strip()
            else:
                venue.venue_contact_phone = None
            venue.put()
        else:
            self.error(501,'Venue Name is required but was not provided')
        self.redirect('/admin/venue')

class GameHandler(webapp.RequestHandler):
    def get(self):
        edit_key = self.request.get('edit',None)
        venues = models.Venue.all().fetch(100)
        if not edit_key is None:
            edit_game = models.Game.get(db.Key(edit_key))
        else:
            edit_game = None
        template_values = { 'venues': venues, 'edit_key': edit_key, 'edit_game': edit_game }
        path = os.path.join(os.path.dirname(__file__), 'templates/game.html')
        self.response.out.write(template.render(path,template_values))
        
    def post(self):
        v = self.request.get('vkey')
        d = datetime.datetime.fromtimestamp(
            time.mktime(time.strptime(self.request.get('play-date'),'%m/%d/%Y'))).date()
        t = datetime.datetime.fromtimestamp(
            time.mktime(time.strptime("01/01/1970 %s" % 
                                      self.request.get('start-time'),'%m/%d/%Y %H:%M'))).time()
        if v and d and t:
            venue = models.Venue.get(db.Key(v))
            g = models.Game(play_date = d,
                            start_time = t,
                            venue = venue)
            g.put()
        else:
            self.error(501,'Venue, Play Date and Start Time are required but was not provided')
        self.redirect('/admin/game')

def main():
    application = webapp.WSGIApplication([
            ('/admin/venue', VenueHandler),
            ('/admin/delete', DeleteHandler),
            ('/admin/game', GameHandler)
            ],debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
