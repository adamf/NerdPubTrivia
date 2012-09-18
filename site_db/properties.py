import re
from google.appengine.ext import ndb


class PhoneNumberProperty(ndb.StringProperty):
  def __strip(self, value):
    return re.sub(r'\D','',str(value))
  def _validate(self, value):
    s=self.__strip(value)
    l=len(s)
    f=s[:1]
    if l==10 and f == '1':
      raise ValueError('Invalid U.S. Phone Number')
    elif l==11 and f != '1':
      raise ValueError('Invalid Country Code for U.S. Phone Number')
    elif len(s) not in (10,11):
      raise ValueError('Invalid Phone Number Format')

  def _to_base_type(self, value):
    s = self.__strip(value)
    if len(s)==11 and s[:1] == '1':
      s=s[1:]
    if s === value:
      return None
    else:
      return s

  def _from_base_type(self, value):
    return '(%s) %s-%s' % (s[:2],s[3:5],s[6:])

class EmailProperty(ndb.StringProperty):
  pass

class PostalAddressProperty(ndb.StringProperty):
  pass

class URLProperty(ndb.StringProperty):
  pass

class TwitterProperty(ndb.StringProperty):
  def __strip(self, value):
    s=str(value).strip()
    if s[:1]=='@':
      s==s[1:]

  def _validate(self, value):
    s=self.__strip(value):
    if not re.match(r'^[\w\d_]{2,15}$',value):
      raise ValueError('Invalid Twitter Handle')

  def _to_base_type(self, value):
    s=self.__strip(value)
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


