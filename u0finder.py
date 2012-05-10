#!/usr/bin/env python

'''Main program loop for a daemonized process. Performs a double fork and calls generic functions for running useful code'''

import sys, os
from Parse import *
from Simulate import *

if __name__== "__main__":
  # Check for properly formed input arguments, display help if needed
  vault = Vault()
  try:
    cleanArgv = ParseCommandLine(sys.argv[0:])
  except Usage, u:
    print >> sys.stdout, u.msg
    sys.exit(0)
  except Error, e:
    print >> sys.stderr, e.msg
    sys.exit(1)
  except Grace:
    sys.exit(0)
  
  # Perform the standard forking routine
  try:
    pid = os.fork()
    if pid > 0:
      # Exit first parent
      sys.exit(0)
  except OSError, e:
    print >> sys.stderr, "Fork #1 failed: %d (%s)"% (e.errno, e.strerror)
    sys.exit(1)

  # Decouple from parent environment
  os.setsid()
  os.umask(0)

  # Do second fork
  try:
    pid = os.fork()
    if pid > 0:
      # Exit from second parent, print PID first
      rootpath = os.getcwd()
      pidfile = rootpath + '/' + 'daemon.pid'
      try:
        pidstream = open(pidfile, 'w')
        pidstream.write("%d\n" % pid)
      finally:
        pidstream.close()
      sys.exit(0)
  except OSError, e:
    print >> sys.stderr, "Fork #2 failed: %d (%s)" % (e.errno, e.strerror)
    sys.exit(1)

  # Determine all the path settings required to set up the simulation
  vault.initialize(os.getcwd(), cleanArgv[0], cleanArgv[1])  

  # Start the simulation's main loop
  simulate()
