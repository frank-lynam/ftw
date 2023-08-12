from ftw import ftw

def hidden(x, y):
  return x+y

@ftw({"x":{"value":1},
      "y":{"value":2}})
def visible(x, y):
  return hidden(x, y)
