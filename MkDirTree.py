#!/usr/bin/env python

import os

def mkdirtree(newdir):
  """Works the way a good mkdir should
      - Directory already exists: silently complete
      - Regular file in the way: raise an exception
      - Parent directory doesn't exist: create recursively"""

  if os.path.isdir(newdir):
    pass
  elif os.path.isfile(newdir):
    raise OSError("Attempted to create a directory '%s', but a regular file of that name existed." % newdir)
  else:
    head, tail = os.path.split(newdir)
    if head and not os.path.isdir(head):
      mkdirtree(head)
    if tail:
      os.mkdir(newdir)
