#!/usr/bin/env python

import logging
import datetime
import time
import os
import webapp2
from google.appengine.ext.webapp import util
from google.appengine.dist import use_library
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
use_library('django', '1.2')
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from site_db import models
import json
import gqlencoder


class TestHandler(webapp2.RequestHandler):
    def createStandardGame(self, game):
        self.createTeams(10, game)
        self.createBasicRound(game, 4, 1)
        self.createPictureRound(game, 2)
        self.createBasicRound(game, 4, 3)
        self.createBioRound(game, 4)
        self.createBasicRound(game, 4, 5)
        self.createListRound(game, 6)
        self.createBasicRound(game, 4, 7)
        self.createWagerRound(game, 2, 8)

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
        g = models.Game(play_date = datetime.date(1990,1,1), 
                        start_time = datetime.time(10), 
                        venue = v)
        g.put()
        self.createStandardGame(g)

        print "Hello World"
        for ven in models.Venue.all().fetch(10):
            for gam in ven.game_set:
                print "Game started at %s" % (gam.start_time)

class VenueHandler(webapp2.RequestHandler):
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

class GameHandler(webapp2.RequestHandler):
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

class PlayHandler(webapp2.RequestHandler):
    def get(self):
        use_json = self.request.get('json',None)
        game_key = self.request.get('game',None)
        game = db.get(game_key)

        maps = models.TeamGameMap.all().filter('game =', game).fetch(100)
        teams = []
        for m in maps:
            team = db.to_dict(m.team)
            team["key"] = m.team.key()
            teams.append(team)

        maps = models.QuestionGameMap.all().filter('game =', game).fetch(100)
        questions = []
        for m in maps:
            questions.append({'question': db.to_dict(m.question), 'round': m.game_round, 
                              'index': m.question_index, 'key': m.key()})

        maps = models.Bid.all().filter('game =', game).fetch(1000)
        bids = {}
        for m in maps:
            team_key = str(m.team.key())
            question_key = str(m.question.key())
            bid_key = str(m.key())
            bids[(team_key, question_key)] = {'team_key': team_key, 'question_key': question_key, 'value': m.bid_value, 'correct': m.correct, 'key': bid_key}
        


        template_values = {'game_key': game_key, 'game': db.to_dict(game), 'teams': teams, 'questions': questions, 'bids': bids}

        if use_json:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(template_values, cls=gqlencoder.GqlEncoder))
        else:
            path = os.path.join(os.path.dirname(__file__), 'templates/play.html')
            self.response.out.write(template.render(path,template_values))

class ScoreHandler(webapp2.RequestHandler):
    def get(self):
        game_key = self.request.get('game')
        game = db.get(game_key)
        teams = models.TeamGameMap.all().filter('game =', game).fetch(1000)
        maps = models.Bid.all().filter('game =', game).fetch(1000)

        score = {}
        for t in teams:
            score[t.team.team_name] = 0

        for m in maps:
            q_type = m.question.question.question_type
            logging.info("team: " + m.team.team_name + " q: " + q_type + " c: " + str(m.correct))
            if m.correct:
                if q_type == 'basic' or q_type == 'bio' or q_type == 'wager':
                    score[m.team.team_name] += m.bid_value
                else:
                    score[m.team.team_name] += (m.bid_value * 2)
            else:
                if q_type == 'wager':
                    score[m.team.team_name] -= (m.bid_value / 2)
            
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(score, cls=gqlencoder.GqlEncoder))


class GuessHandler(webapp2.RequestHandler):
    def get(self):
        changed_since = int(self.request.get('changed_since', None))
        game_key = self.request.get('game')
        game = db.get(game_key)
        # search by seconds since the epoch to avoid time bullshit
        if not changed_since:
            changed_since = 0;
   
        logging.info(changed_since)
        maps = models.Bid.all().filter('game =', game).filter("modify_time > ", changed_since).fetch(1000)
        #maps = models.Bid.all().filter('game =', game).fetch(1000)

        bids = []
        for m in maps:
            team_key = str(m.team.key())
            question_key = str(m.question.key())
            bid_key = str(m.key())
            bids.append({ 'bid_key': bid_key, 'question_key': question_key, 'team_key': team_key,
                          'modify_time': m.modify_time, 'wager': m.bid_value, 'correct': m.correct})

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(bids, cls=gqlencoder.GqlEncoder))

    def post(self):
        game_key = self.request.get('game')
        question_map_key = self.request.get('question') 
        team_key = self.request.get('team')
        wager = self.request.get('wager')
        correct = self.request.get('correct')
        if (correct == "false"):
            correct = False
        else:
            correct = True


        logging.info(correct)

        team = db.Key(team_key)
        question = db.Key(question_map_key)
        game = db.Key(game_key)

        bid_key = "%s-%s-%s" % (game_key, team_key, question_map_key)
        logging.info("correct %s wager %s bid key %s" % (correct, wager, bid_key)) 

        if wager == "":
            bid = models.Bid.get_by_key_name(bid_key)
            logging.info(bid)
            if bid:
                bid.delete()
        else:
            wager = int(wager)
            bid = models.Bid.get_or_insert(bid_key, team=team, 
                            question=question, game=game, correct=correct, bid_value=wager)

            if bid.bid_value != wager or bid.correct != correct:
                bid.bid_value = wager
                bid.correct = correct
                now = datetime.datetime.utcnow()
                bid.modify_time = int(now.strftime('%s'))
                bid.put()


app = webapp2.WSGIApplication([
        ('/admin/test', TestHandler),
        ('/admin/venue', VenueHandler),
        ('/admin/game', GameHandler),
        ('/admin/play', PlayHandler),
        ('/admin/play/guess', GuessHandler),
        ('/admin/play/score', ScoreHandler)
        ],debug=True)
