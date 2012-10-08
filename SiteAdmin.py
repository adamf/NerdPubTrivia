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
    def createStandardGame(self, game):
        self.createTeams(10, game)
        self.createBasicRound(game, 4, 1)
        self.createBasicRound(game, 4, 2)
        self.createPictureRound(game, 3)
        self.createBasicRound(game, 4, 4)
        self.createBasicRound(game, 4, 5)
        self.createBioRound(game, 6)
        self.createBasicRound(game, 4, 7)
        self.createBasicRound(game, 4, 8)
        self.createListRound(game, 9)
        self.createBasicRound(game, 4, 10)
        self.createBasicRound(game, 4, 11)
        self.createWagerRound(game, 2, 12)

    def createTeams(self, numTeams, game):

        for i in range(0, numTeams):
            t = models.Team(team_name='Test Team ' + str(i))
            t.put()
            teamToGame = models.TeamGameMap(team=t, game=game)
            teamToGame.put()
            print t.team_name


    def createBasicRound(self, game, questionCount, gameRound):
        for i in range(0, questionCount):
            c = models.Category(category_text = 'Category ' + str(i * gameRound) + ' '  + str(i) )
            c.put()
            q = models.Question(category=c, question_type = 'basic', 
                    question_text = 'Who is question ' + str(i * gameRound) + '?')
            q.put()
            a = models.Answer(answer_text = [db.Text(str(i * gameRound) + ', obviously')],question = q)
            a.put()
            print c.category_text, q.question_text, a.answer_text

            questionToGame = models.QuestionGameMap(question=q, game=game, game_round=gameRound, question_index=i)
            questionToGame.put()

    def createWagerRound(self, game, questionCount, gameRound):
        for i in range(0, questionCount):
            c = models.Category(category_text = 'Category ' + str(i * gameRound) + ' '  + str(i) )
            c.put()
            q = models.Question(category=c, question_type = 'wager', 
                    question_text = 'Name four of the ' + str(i * gameRound) + ' foos?')
            q.put()
            a = models.Answer(answer_text = [db.Text(str(i * gameRound) + ', obviously')],question = q)
            a.put()
            print c.category_text, q.question_text, a.answer_text

            questionToGame = models.QuestionGameMap(question=q, game=game, game_round=gameRound, question_index=i)
            questionToGame.put()

    def createPictureRound(self, game, gameRound):
        c = models.Category(category_text = 'Picture round ' + str(gameRound))
        c.put()
        q = models.Question(category=c, question_type = 'picture', 
                question_text = 'Identify the nerds')
        q.put()
        a = models.Answer(answer_text = [db.Text('bill'), db.Text('frank'), db.Text('jill')],question = q)
        a.put()

        print c.category_text, q.question_text, a.answer_text

        questionToGame = models.QuestionGameMap(question=q, game=game, game_round=gameRound, question_index=1)
        questionToGame.put()

    def createListRound(self, game, gameRound):
        self.createSpecialRound(game, 'list', gameRound)

    def createPuzzleRound(self, game, gameRound):
        self.createSpecialRound(game, 'list', gameRound)

    def createBioRound(self, game, gameRound):
        self.createSpecialRound(game, 'bio', gameRound)

    def createSpecialRound(self, game, roundType, gameRound):
        c = models.Category(category_text = roundType + ' round ' + str(gameRound))
        c.put()
        q = models.Question(category=c, question_type = roundType, 
                question_text = 'Solve the ' + roundType)
        q.put()
        a = models.Answer(answer_text = [db.Text('The Correct Answer')],question = q)
        a.put()

        print c.category_text, q.question_text, a.answer_text

        questionToGame = models.QuestionGameMap(question=q, game=game, game_round=gameRound, question_index=1)
        questionToGame.put()


    def get(self):
        v = models.Venue(venue_name='Fake Trivia Bar',venue_contact_email='fakebar@example.com')
        v.venue_address = 'One Fake Square, Fake, MA 02111 USA'
        v.put()
        g = models.Game(play_date = datetime.date(1900,1,1), 
                        start_time = datetime.time(10), 
                        venue = v)
        g.put()
        self.createStandardGame(g)

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
        games = models.Game.all().fetch(100)
        template_values = { 'venues': venues, 'edit_key': edit_key, 'games': games }
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
        game_key = self.request.get('game',None)
        game = db.get(game_key)

        maps = models.TeamGameMap.all().filter('game =', game).fetch(100)
        teams = []
        for m in maps:
            teams.append(m.team)

        maps = models.QuestionGameMap.all().filter('game =', game).fetch(100)
        questions = []
        for m in maps:
            questions.append({'question': m.question, 'round': m.game_round, 'index': m.question_index})

        maps = models.Bid.all().filter('game =', game).fetch(100)
        bids = {}
        for m in maps:
            bids[(m.team.team_name, m.question.question_index)] = {'value': m.bid_value, 'correct': m.correct}
        


        template_values = {'game': game, 'teams': teams, 'questions': questions, 'bids': bids}
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
