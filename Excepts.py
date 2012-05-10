#!/usr/bin/env python

class Usage(Exception):
  '''Provides usage information.'''
  def __init__(self):
    self.msg = """
  u0finder - Daemonized submitting and analysis tool for finding MILC's u0 parameter, version 1.00

  Reads a MILC input and rationalization file and uses them to run a sequence of tuning runs on a
  BG/L through the Cobalt queuing system. 

  SYNTAX: u0finder [opts] <MILC_input_file> <MILC_rationals_file>
  Possible options:
      -c [--corr]     (20)               : Sets assumed autocorrelation length
      -h [--help]                        : Display this help message and exit
      -m [--maxtraj]  (1000)             : Sets the maximum number of trajectories in a single run
      -n [--nodes]    (32)               : Sets the number of nodes the job will be submitted on
      -q [--queue]    (DEFAULT|long|rug) : Sets the queue the job will be submitted to
      -v [--version]                     : Print the program's version number and exit
      -w [--wall]     (240)              : Sets the wall time for the run
      -W [--warms]    (100)              : Sets the default number of warms done

  Written by A. Deuzeman (a.deuzeman@rug.nl).
  Coded in Python 2.5.1 on Kubuntu 7.10 - released under GPLv3.

  **************************************************************************
  *** This is a beta version - some bugs might still be encountered      ***
  *** Bug reports and suggestions are welcome at the above email address ***
  **************************************************************************
  """
  def __str__(self):
    return repr(self.msg)
  
class Grace(Exception):
  '''Provides a mechanism for graceful exiting.'''
  def __init__(self):
    self.msg = "Graceful exit requested"
  def __str__(self):
    return repr(self.msg)
  
class Error(Exception):
  '''Provides an error reporting mechanism.'''
  def __init__(self, msg):
    __myStrings = (["Error encountered!"])
    __myStrings.extend(msg)
    self.msg = '\n'.join(__myStrings)
  def __str__(self):
    return repr(self.msg)

class DispatchError(Exception):
  def __init__(self, value):
      self.value = value
  def __str__(self):
      return repr(self.value)