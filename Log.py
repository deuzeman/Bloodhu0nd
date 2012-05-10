#!/usr/bin/env python

import sys

class Log:
  """Behaves like a file, but flushes after each writing operation to provide atomic logging.
  Should ensure proper event description, even when an unexpected exit occured."""
  def __init__(self, f):
    self.f = f
  def write(self, s):
    self.f.write(s)
    self.f.flush()
  def close(self):
    self.f.close()

def log(message):
  print >> sys.stdout, message