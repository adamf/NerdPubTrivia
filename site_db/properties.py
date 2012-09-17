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
      raise TypeError('Invalid U.S. Phone Number')
    elif l==11 and f != '1':
      raise TypeError('Invalid Country Code for U.S. Phone Number')
    elif len(s) not in (10,11):
      raise TypeError('Invalid Phone Number Format')

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
