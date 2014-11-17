# https://djangosnippets.org/snippets/1412/

from django.template import Library

register = Library()

@register.filter(name='get')
def get(dict, key, default = ''):
  """
  Usage: 

  view: 
  some_dict = {'keyA':'valueA','keyB':{'subKeyA':'subValueA','subKeyB':'subKeyB'},'keyC':'valueC'}
  keys = ['keyA','keyC']
  keyA = 'keyA'
  template: 
  {{ some_dict|get:"keyA" }}
  {{ some_dict|get:keyA }}
  {{ some_dict|get:"keyB"|get:"subKeyA" }}
  {% for key in keys %}{{ some_dict|get:key }}{% endfor %}
  """

  try:
    return dict.get(key,default)
  except:
    return default
