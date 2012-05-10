#!/usr/bin/env python

from getopt import gnu_getopt
from getopt import GetoptError
from Excepts import *
from Vault import *

def ParseCommandLine(argv = None) :
  """Parses command line arguments and options

  Returns clean list of arguments """
  vault = Vault()
  
  vault['queue'] = 'default'
  vault['wall_time'] = 240
  vault['nodes'] = 32
  vault['warms_base'] = 100
  vault['version'] = 'v1.00'
  vault['corr_length'] = 20
  vault['max_confs'] = 1000
  
  if argv == None:
    argv = sys.argv[1:]

  if argv == []:
    raise Usage()

  shortOpts = 'c:hm:n:q:vw:W:'
  longOpts  = ['corr=', 'help', 'maxtraj=', 'nodes=' 'queue=', 'version', 'wall=', 'Warms=']
  try:
    (optlist, args) = gnu_getopt(argv, shortOpts, longOpts)
  except GetoptError, e:
    print >>sys.stderr, 'Option parsing error:', e.msg
    print >>sys.stderr, 'Call u0finder with --help for usage information.'
    sys.exit(1)

  for op, ar in optlist:
    if op in ("-c", "--corr"):
      try:
        vault['corr_length'] = int(ar)
      except:
        raise Error(["Value given to 'corr' ('c') flag was not recognized.",
                     "Valid choices are integer numbers."])
    elif op in ("-h", "--help"):
      raise Usage()
    elif op in ("-m", "--maxtraj"):
      try:
        vault['max_confs'] = int(ar)
      except:
        raise Error(["Value given to 'maxtraj' ('m') flag was not recognized.",
                     "Valid choices are integer numbers."])
    elif op in ("-n", "--nodes"):
      try:
        vault['nodes'] = int(ar)
      except:
        raise Error(["Value given to 'nodes' ('n') flag was not recognized.",
                     "Valid choices are integer numbers."])
    elif op in ("-q", "--queue"):
      if not ar in ['default', 'long', 'rug']:
        raise Error(["The 'queue' ('q') flag needs a queue name as an argument.",
                     "Current valid choices are 'default', 'long' and 'rug'."])
      vault['queue'] = ar
    elif op in ("-v", "--version"):
      print >>sys.stderr, 'u0finder', vault['version']
      raise Grace()
    elif op in ("-w", "--wall"):
      try:
        vault['wall_time'] = int(ar)
      except:
        raise Error(["Value given to 'wall' ('w') flag was not recognized.",
                     "Valid choices are integer numbers, describing time in minutes."])
    elif op in ("-W", "--warms"):
      try:
        vault['warms_base'] = int(ar)
      except:
        raise Error(["Value given to 'warms' ('W') flag was not recognized.",
                     "Valid choices are integer numbers."])

  if len(args) <= 1:
    raise Error(["Provide at least a MILC input file and a rationals file as arguments.",
                 "Call u0finder with the -h or --help option for usage information."])

  return args[1:]
