from ftw import ftw

def hidden_function(x, y):
  return x+y

@ftw({"x":{"value":1},
      "y":{"value":2}})
def visible_wrapper(x, y):
  return hidden_function(x, y)
