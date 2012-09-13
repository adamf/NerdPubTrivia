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


class BaseHandler(webapp.RequestHandler):
  def get_string(self,request_key,default_value=None):
    if self.request.get(request_key).strip():
      return self.request.get(request_key).strip()
    else:
      return default_value

  def render_template(self,template_file,template_values):
    template_path = os.path.join(os.path.dirname(__file__),
                                 'templates',template_file)
    self.response.out.write(template.render(template_path,
                                            template_values))

class DeleteHandler(webapp.RequestHandler):
  def get(self):
    db.Model.get(db.Key(self.request.get('edit'))).delete()
  self.redirect(self.request.environ['HTTP_REFERER'])

class VenueHandler(BaseHandler):
  def get(self):
    edit_key = self.request.get('edit',None)
    venues = models.Venue.all().fetch(100)
    if not edit_key is None:
      edit_venue = [v for v in venues
                    if (("%s" % v.key()) == edit_key)][0]
    else:
      edit_venue = None
    self.render_template('venue.html', { 'venues': venues,
                                         'edit_key': edit_key,
                                         'edit_venue': edit_venue })
  def post(self):
    v = self.get_string('vname')
    if v:
      venue = models.Venue(venue_name=v)
      venue.venue_address = self.get_string('vaddress')
      venue.venue_contact_email = self.get_string('cemail')
      venue.venue_contact_phone = self.get_string('cphone')
      venue.put()
    else:
      self.error(501,'Venue Name is required but was not provided')
    self.redirect('/admin/venue')

class GameHandler(BaseHandler):
  def get(self):
    edit_key = self.request.get('edit',None)
    venues = models.Venue.all().fetch(100)
    if not edit_key is None:
      edit_game = models.Game.get(db.Key(edit_key))
    else:
      edit_game = None
    self.render_template('game.html', { 'venues': venues,
                                        'edit_key': edit_key,
                                        'edit_game': edit_game })
  def post(self):
    v = self.request.get('vkey')
    d = datetime.datetime.fromtimestamp(
      time.mktime(time.strptime(
          self.request.get('play-date'),'%m/%d/%Y'))).date()
    t = datetime.datetime.fromtimestamp(
      time.mktime(time.strptime("01/01/1970 %s" %
                                self.request.get('start-time'),
                                '%m/%d/%Y %H:%M'))).time()
    if v and d and t:
      venue = models.Venue.get(db.Key(v))
      g = models.Game(play_date = d,
                      start_time = t,
                      venue = venue)
      g.put()
    else:
      self.error(501,
                 ('Venue, Play Date and Start Time '
                  'are required but was not provided'))
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
