import re
import properties as props
from google.appengine.ext import ndb


class SelfKeyModel(ndb.Model):
  def _strip(self, value):
    return re.sub(r'[\s\W]', '', value).lower()

  def _pre_put_hook(self):
    auto_key = self._to_key_string()
    if auto_key:
      if not self.key.id():
        self.key = ndb.Key(self.key.kind(), auto_key,
                           parent=self._get_parent_column())
    if self._is_static_key():
      if self.key.id() != auto_key:
        raise ValueError(('Static Key Column[s] may not be changed '
                          'after assignment.'))
      if self.key.parent() != self._get_parent_column():
        raise ValueError(('Static Key Parent Columns may not be '
                          'changed after assignment.'))

  def _to_key_string(self):
    auto_key = []
    for key_part in self._get_key_columns():
      if isinstance(key_part, (ndb.DateTimeProperty,
                               ndb.DateProperty,
                               ndb.TimeProperty)):
        auto_key.append(key_part.isoformat())
      elif isinstance(key_part, ndb.GeoPtProperty):
        auto_key.append('%f, %f' % (key_part.lat, key_part.lon))
      elif isinstance(key_part, (ndb.KeyProperty, ndb.Key)):
        try:
          auto_key.append(key_part.get()._to_key_string())
        except AttributeError:
          raise ValueError(('KeyProperty attributes incorporated in '
                            'auto-key generation must refer to models '
                            'which support auto-key generation.'))
      else:
        try:
          auto_key.append(self._strip(str(key_part)))
        except:
          auto_key.append(self._strip(repr(key_part)))
    return '.'.join(auto_key)

  def _is_static_key(self):
    return False

  def _get_key_columns(self):
    return ()

  def _get_parent_column(self):
    if self.key:
      return self.key.parent()
    return None


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


class Team(ndb.Model):
  name = ndb.StringProperty(required=True)
  notes = ndb.TextProperty
  twitter_handle = props.TwitterProperty()


class Game(SelfKeyModel):
  play_date = props.SafeDate(required=True)
  play_time = props.SafeTime(required=True)
  game_name = ndb.StringProperty(default='Nerd Pub Trivia')
  venue = ndb.KeyProperty(kind=Venue, required=True)

  def _get_key_columns(self):
    return (self.play_date, self.venue)


class Question(ndb.Model):
  question_type = ndb.StringProperty(required=True,
                                     choices=('basic',
                                              'picture',
                                              'list',
                                              'set',
                                              'bio'))
  question_text = ndb.TextProperty(required=True)
  multiplier = props.MultiplierProperty(default=1)


class Clue(ndb.Model):
  question = ndb.KeyProperty(required=True, kind=Question)
  clue_text = ndb.TextProperty(required=True)
  order = ndb.IntegerProperty(required=True)


class Answer(ndb.Model):
  question = ndb.KeyProperty(required=True, kind=Question)
  answer_text = ndb.TextProperty(required=True)
  validation_url = props.URLProperty()
  answer_search_key = ndb.ComputedProperty(
      lambda self: self.answer_text[:499].strip().lower())


class QuestionGameMap(ndb.StaticKeyModel):
  question = ndb.KeyProperty(required=True, kind=Question)
  game = ndb.KeyProperty(required=True, kind=Game)
  round_type = ndb.StringProperty(required=True,
                                  choices=('first',
                                           'second',
                                           'third',
                                           'fourth',
                                           'final',
                                           'picture',
                                           'matching',
                                           'long-form'))
  order = ndb.IntegerProperty(required=True)

  def _get_key_columns(self):
    return (self.game, self.round_type, self.order)

  def _get_parent_column(self):
    return self.game


class TeamGameMap(ndb.StaticKeyModel):
  team = ndb.KeyProperty(required=True, kind=Team)
  game = ndb.KeyProperty(required=True, kind=Game)

  def _get_key_columns(self):
    return (self.game, self.team)

  def _get_parent_column(self):
    return self.game


class Bid(ndb.StaticKeyModel):
  team_instance = ndb.KeyProperty(required=True, kind=TeamGameMap)
  question = ndb.KeyProperty(required=True, kind=QuestionGameMap)
  bid_value = ndb.IntegerProperty(required=True, choices=(1, 2, 3, 4, 5,
                                                          6, 7, 8, 10))
  correct = ndb.BooleanProperty(default=False)

  def _get_key_columns(self):
    return (self.team_instance, self.question)

  def _get_parent_column(self):
    return self.team_instance
