import datetime
import re
import properties as props
from google.appengine.ext import db
from google.appengine.ext import ndb

class SelfKeyModel(ndb.Model):

  def __format_name_for_id(self):
    return re.sub(r'[\s\W]','',self.display_name)

  def _pre_put_hook(self):
    auto_key = self._to_key_string()
    if auto_key:
      if not self.key.id():
        self.key = ndb.Key(self.key.kind(), auto_key, parent=self.key.parent())
      if self.key.id() != auto_key:
        if self._is_static_key():
          raise ValueError(('Static Key Column[s] may not be changed '
                            'after assignment.'))

  def _is_static_key(self):
    return False

  def _to_key_string(self):
    auto_key = []
    for key_part in self._get_key_columns():
      if isinstance(key_part, (ndb.DateTimeProperty,
                               ndb.DateProperty,
                               ndb.TimeProperty)):
        auto_key.append(key_part.isoformat())
      elif isinstance(key_part, ndb.GeoPtProperty):
        auto_key.append("%f,%f" % (key_part.lat, key_part.lon))
      elif isinstance(key_part, (ndb.KeyProperty,ndb.Key)):
        try:
          auto_key.append(key_part.get()._to_key_string())
        except AttributeError:
          raise ValueError(('KeyProperty attributes incorporated in '
                            'auto-key generation must refer to models '
                            'which support auto-key generation.'))
      else:
        try:
          auto_key.append(str(key_part))
        except:
          auto_key.append(repr(key_part))
    return '.'.join(auto_key)

  def _get_key_columns(self):
    return ()

class StaticKeyModel(SelfKeyModel):
  def _is_static_key(self):
    return True

class Venue(StaticKeyModel):
  display_name = ndb.StringProperty(required=True)
  contact_email = props.EmailProperty()
  public_email = props.EmailProperty()
  contact_phone = props.PhoneNumberProperty()
  public_phone = props.PhoneNumberProperty()
  address = props.PostalAddressProperty()
  website = props.URLProperty()
  twitter_handle = props.TwitterProperty()

  def _get_key_columns(self):
    return (self.display_name,)

class Game(SelfKeyModel):
  play_date = props.SafeDate(required=True)
  play_time = props.SafeTime(required=True)
  game_name = ndb.StringProperty(default='Nerd Pub Trivia')
  venue = ndb.KeyProperty(kind=Venue, required=True)

  def _get_key_columns(self):
    return (self.play_date, self.venue)

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
