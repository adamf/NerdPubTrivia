import re
import datetime
from google.appengine.ext import ndb

class CustomStringProperty(ndb.StringProperty):
  def _strip(self, value):
    return str(value).strip()

class PhoneNumberProperty(CustomStringProperty):
  def _strip(self, value):
    return re.sub(r'\D','',str(s))

  def _validate(self, value):
    s=self._strip(value)
    l=len(s)
    f=s[:1]
    if l==10 and f == '1':
      raise ValueError('Invalid U.S. Phone Number')
    elif l==11 and f != '1':
      raise ValueError('Invalid Country Code for U.S. Phone Number')
    elif len(s) not in (10,11):
      raise ValueError('Invalid Phone Number Format')

  def _to_base_type(self, value):
    s = self._strip(value)
    if len(s)==11 and s[:1] == '1':
      s=s[1:]
    if s == value:
      return None
    else:
      return s

  def _from_base_type(self, value):
    s = self._strip(value)
    return '(%s) %s-%s' % (s[:2],s[3:5],s[6:])

class EmailProperty(CustomStringProperty):
  def _to_base_type(self, value):
    return self._strip(value).lower()

  def _validate(self, value):
    s=self._strip(value)
    if not re.match(
        r'^[^\s@]+@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,4}$', s):
      raise ValueError('Unsupported or Invalid Email Address')

class PostalAddressProperty(CustomStringProperty):
  pass

class URLProperty(CustomStringProperty):
  pass

class TwitterProperty(CustomStringProperty):
  def _strip(self, value):
    s=super(TwitterProperty, self)._strip(value).lower()
    if s[:1]=='@':
      s=s[1:]

  def _validate(self, value):
    s=self._strip(value)
    if not re.match(r'^[\w\d_]{2,15}$',value):
      raise ValueError('Invalid Twitter Handle')

  def _to_base_type(self, value):
    s=self._strip(value)
    if s==value:
      return None
    else:
      return s

  def _from_base_type(self, value):
    return '@%s' % (value)

class MultiplierProperty(ndb.IntegerProperty):
  def _validate(self, value):
    if value < 1 and value != -1:
      raise ValueError('Multiplier must be positive or be -1')

class DateSerializerMixin(object):
  def __init__(self, *args, **kwargs):
    super(DateSerializerMixin, self).__init__(*args, **kwargs)

  def _get_for_dict(self, entity):
    try:
      return self._get_value(entity).isoformat()
    except AttributeError:
      pass
    return super(DateSerializerMixin, self)._get_for_dict(entity)

class DateTZInfoMixin(object):
  class UTCTZInfo(datetime.tzinfo):
    def utcoffset(self, dt):
      return datetime.timedelta(0)
    def dst(self, dt):
      return datetime.timedelta(0)
    def tzname(self, dt):
      return 'UTC'
  class EasternTZInfo(datetime.tzinfo):
    def utcoffset(self, dt):
      return datetime.timedelta(hours=-5)
    def dst(self, dt):
      return datetime.timedelta(hours=-4)
    def tzname(self, dt):
      return 'local'

  def __init__(self, *args, **kwargs):
    super(DateTZInfoMixin, self).__init__(*args, **kwargs)

  def _to_base_type(self, value):
    return value.replace(tzinfo=None)

  def _from_base_type(self, value):
    return value.replace(tzinfo=self.EasternTZInfo())

class SafeDateTime(DateTZInfoMixin, DateSerializerMixin, ndb.DateTimeProperty):
  pass

class SafeTime(DateTZInfoMixin, DateSerializerMixin, ndb.TimeProperty):
  pass

class SafeDate(DateSerializerMixin, ndb.DateProperty):
  pass
