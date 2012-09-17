#!/usr/bin/env python
import datetime
import re
import properties as props
from google.appengine.ext import db
from google.appengine.ext import ndb


class Venue(ndb.Model):
    # def __init__(self, *args, **kwargs):
    #     if not kwargs.has_key('key'):
    #         kwargs['key_name'] = kwargs['venue_name']
    #     super(self.__class__, self).__init__(*args, **kwargs)
    display_name = ndb.StringProperty(required=True)
    contact_email = props.EmailProperty()
    public_email = props.EmailProperty()
    contact_phone = props.PhoneNumberProperty()
    public_phone = props.PhoneNumberProperty()
    address = ndb.PostalAddressProperty()
    website = props.URLProperty()

    def _pre_put_hook(self):
      if self.id != self.__format_name_for_id(self.display_name):
        raise ValueError('Venue name can not be changed after assignment.')

    def __format_name_for_id(self):
      return re.sub(r'[\s\W]','')

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
    venue = db.ReferenceProperty(reference_class=Venue,required=True)

class Question(db.Model):
    question_type = db.StringProperty(required=True,choices=('basic','picture','list','set','bio'))
    question_text = db.TextProperty(required=True)
    question_multiplier = db.IntegerProperty(required=True,default=1)

class QuestionGameMap(db.Model):
    question = db.ReferenceProperty(required=True,reference_class=Question)
    game = db.ReferenceProperty(required=True,reference_class=Game)

class Clue(db.Model):
    question = db.ReferenceProperty(required=True,reference_class=Question)
    clue_text = db.TextProperty(required=True)
    order = db.IntegerProperty(required=True)

class Answer(db.Model):
    question = db.ReferenceProperty(required=True,reference_class=Question)
    answer_text = db.ListProperty(db.Text,required=True)

class Team(db.Model):
    def __init__(self, *args, **kwargs):
        kwargs['key_name'] = kwargs['team_name']
        super(self.__class__, self).__init__(*args, **kwargs)
    team_name = db.StringProperty
    team_notes = db.TextProperty

class TeamGameMap(db.Model):
    team = db.ReferenceProperty(required=True,reference_class=Team)
    game = db.ReferenceProperty(required=True,reference_class=Game)

class bid(db.Model):
    team_instance = db.ReferenceProperty(required=True,reference_class=TeamGameMap)
    question = db.ReferenceProperty(required=True,reference_class=QuestionGameMap)
    bid_value = db.IntegerProperty(required=True,choices=(1,2,3,4,5,6,7,8,10))
    correct = db.BooleanProperty(required=True,default=False)
