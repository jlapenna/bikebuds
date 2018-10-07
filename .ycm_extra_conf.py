from os.path import expanduser

def Settings( **kwargs ):
  return {
    'interpreter_path': expanduser("~/appengine_env/bin/python")
  }
