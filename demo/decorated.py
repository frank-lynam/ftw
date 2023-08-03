from ftw import ftw

def hidden_method(x, y):
  return x+y

@ftw
def visible_method(x, y):
  return hidden_method(x, y)
