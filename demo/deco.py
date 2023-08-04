from ftw import ftw

def hidden(x, y):
  return x+y

@ftw
def visible(x, y):
  return hidden_method(x, y)
