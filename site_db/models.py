#!/usr/bin/env python
import datetime
from google.appengine.ext import db

class Venue(db.Model):
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('key'):
            kwargs['key_name'] = kwargs['venue_name']
        super(self.__class__, self).__init__(*args, **kwargs)
    venue_name = db.StringProperty(required=True)
    venue_contact_email = db.EmailProperty()
    venue_contact_phone = db.PhoneNumberProperty()
    venue_address = db.PostalAddressProperty()

class Game(db.Model):
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('key'):
            v = kwargs['venue'].venue_name
            d = kwargs['play_date']
            k = "%s-%s" % (v,d.isoformat())
            kwargs['key_name'] = k
        super(self.__class__, self).__init__(*args, **kwargs)
    play_date = db.DateProperty(required=True)
    start_time = db.TimeProperty(required=True)
    finish_time = db.TimeProperty()
    venue = db.ReferenceProperty(reference_class=Venue,required=True)

class Category(db.Model):
    category_text = db.StringProperty(required=True)

class Question(db.Model):
    question_type = db.StringProperty(required=True,choices=('basic','picture','list','set','bio', 'wager'))
    question_text = db.TextProperty(required=True)
    category = db.ReferenceProperty(required=True,reference_class=Category)

class QuestionGameMap(db.Model):
    question = db.ReferenceProperty(required=True,reference_class=Question)
    game = db.ReferenceProperty(required=True,reference_class=Game)
    game_round = db.IntegerProperty(required=True)
    question_index = db.IntegerProperty(required=True)

class Clue(db.Model):
    question = db.ReferenceProperty(required=True,reference_class=Question)
    clue_text = db.TextProperty(required=True)
    order = db.IntegerProperty(required=True)

class Answer(db.Model):
    question = db.ReferenceProperty(required=True,reference_class=Question)
    answer_text = db.ListProperty(db.Text,required=True)

class Team(db.Model):
    team_name = db.StringProperty(required=True)
    team_notes = db.TextProperty()

class TeamGameMap(db.Model):
    team = db.ReferenceProperty(required=True,reference_class=Team)
    game = db.ReferenceProperty(required=True,reference_class=Game)

class Bid(db.Model):
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('key'):
            g = kwargs['game']
            t = kwargs['team']
            q = kwargs['question']
            k = "%s-%s-%s" % (g,t,q)
            kwargs['key_name'] = k
        super(self.__class__, self).__init__(*args, **kwargs)
    game = db.ReferenceProperty(required=True,reference_class=Game)
    team = db.ReferenceProperty(required=True,reference_class=Team)
    question = db.ReferenceProperty(required=True,reference_class=QuestionGameMap)
    bid_value = db.IntegerProperty(required=True)
    correct = db.BooleanProperty(required=True,default=False)
