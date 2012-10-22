#!/usr/bin/env python
import datetime
import re
import properties as props
from google.appengine.ext import db
from google.appengine.ext import ndb

class SelfKeyModel(ndb.Model):

  def __format_name_for_id(self):
    return re.sub(r'[\s\W]','',self.display_name)


class Venue(SelfKeyModel):
  display_name = ndb.StringProperty(required=True)
  contact_email = props.EmailProperty()
  public_email = props.EmailProperty()
  contact_phone = props.PhoneNumberProperty()
  public_phone = props.PhoneNumberProperty()
  address = props.PostalAddressProperty()
  website = props.URLProperty()
  twitter_handle = props.TwitterProperty()

  def _pre_put_hook(self):
    if self.key is None:
      self.key = ndb.Key(self.__class__,
                         self.__format_name_for_id())

    if self.id != self.__format_name_for_id(self.display_name):
      raise ValueError('Venue name can not be changed after assignment.')

class Game(ndb.Model):
    play_date = ndb.DateTimeProperty(required=True)
    game_name = ndb.StringProperty(default='Nerd Pub Trivia')
    venue = ndb.KeyProperty(kind=Venue, required=True)

class Question(ndb.Model):
    question_type = db.StringProperty(required=True,
                                      choices=('basic',
                                               'picture',
                                               'list',
                                               'set',
                                               'bio'))
    question_text = db.TextProperty(required=True)
    multiplier = props.MultiplierProperty(default=1)

class QuestionGameMap(ndb.Model):
    question = ndb.KeyProperty(required=True,kind=Question)
    game = ndb.KeyProperty(required=True,kind=Game)

class Clue(ndb.Model):
    question = ndb.KeyProperty(required=True,kind=Question)
    clue_text = ndb.TextProperty(required=True)
    order = ndb.IntegerProperty(required=True)

class Answer(ndb.Model):
    question = ndb.KeyProperty(required=True,kind=Question)
    answer_text = db.ListProperty(db.Text,required=True)

class Team(ndb.Model):
    name = ndb.StringProperty(required=True)
    notes = ndb.TextProperty
    twitter_handle = props.TwitterProperty()



class TeamGameMap(ndb.Model):
    team = ndb.KeyProperty(required=True,kind=Team)
    game = ndb.KeyProperty(required=True,kind=Game)

class bid(ndb.Model):
    team_instance = ndb.KeyProperty(required=True,kind=TeamGameMap)
    question = ndb.KeyProperty(required=True,kind=QuestionGameMap)
    bid_value = ndb.IntegerProperty(required=True,choices=(1,2,3,4,5,6,7,8,10))
    correct = ndb.BooleanProperty(default=False)
