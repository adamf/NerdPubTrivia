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


class TestHandler(webapp.RequestHandler):
    def get(self):
        v = models.Venue(venue_name='ThinkTank',venue_contact_email='vc@thinktankcambridge.com')
        v.venue_address = 'One Kendall Square, Cambridge, MA 02139 USA'
        v.put()
        g = models.Game(play_date = datetime.date(2011,4,6), 
                        start_time = datetime.time(19), 
                        venue = v)
        g.put()
        print "Hello World"
        for ven in models.Venue.all().fetch(10):
            for gam in ven.game_set:
                print "Game started at %s" % (gam.start_time)

class VenueHandler(webapp.RequestHandler):
    def get(self):
        edit_key = self.request.get('edit',None)
        venues = models.Venue.all().fetch(100)
        if not edit_key is None:
            edit_venue = [v for v in venues if (("%s" % v.key()) == edit_key)][0]
            self.response.out.write('<!-- %s -->' % (edit_venue.venue_name))
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
        template_values = { 'venues': venues, 'edit_key': edit_key }
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
            self.error(501,'Venue Name is required but was not provided')
        self.redirect('/admin/venue')

class PlayHandler(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates/play.html')
        self.response.out.write(template.render(path,template_values))

    def post(self):
        pass

def main():
    application = webapp.WSGIApplication([
            ('/admin/test', TestHandler),
            ('/admin/venue', VenueHandler),
            ('/admin/game', GameHandler),
            ('/admin/play', PlayHandler)
            ],debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
