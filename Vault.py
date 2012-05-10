#!/usr/bin/env python

import os, random, sys
from Log import *

class Vault:
  """ A python Vault """
  
  # Stores the reference instance
  __vault_instance = None
 
  class __vault_impl:
    """ Implementation of the Vault interface """   
    
    def keys(self):
      return self.__dict__.keys()
    
    def __getitem__(self, key):
      return self.__dict__[key]
    
    def __setitem__(self, key, value):
      return self.__dict__.__setitem__(key, value)
    
  def initialize(self, root_path, run_name, rationals_file):
    """ Sets the initial values of a Vault instance """
    self.__vault_instance.u0 = 0
    self.__vault_instance.recent_output = ''
    self.__vault_instance.recent_error = ''
      
    self.__vault_instance.warms_done_flag = False
    self.__vault_instance.lattice_written_flag = False
  
    self.__vault_instance.warms_done = 0
  
    self.__vault_instance.configs_meas = []
    self.__vault_instance.configs_total = []
    self.__vault_instance.meas_done = []
  
    self.__vault_instance.meas_stats = []
    self.__vault_instance.noise_ratio = 100
    
    self.__vault_instance.root_path = root_path
    self.__vault_instance.run_name = run_name
    self.__vault_instance.run_path = root_path + '/' + run_name + '_u0'
  
    self.__vault_instance.rationals_file = root_path + '/' + rationals_file
    self.__vault_instance.temp_rationals_file = self.__vault_instance.run_path + '/' + rationals_file
  
    self.__vault_instance.lattice_file = self.__vault_instance.run_path + '/' + run_name + '.lat.sav'
    self.__vault_instance.lattice_exists = os.path.isfile(self.__vault_instance.lattice_file)
  
    self.__vault_instance.script_file = root_path + '/' + run_name
    self.__vault_instance.temp_script_file = self.__vault_instance.run_path + '/' + run_name
  
    self.__vault_instance.program = root_path + '/su3_u0'
    self.__vault_instance.temp_program = self.__vault_instance.run_path + '/su3_u0'
  
    self.__vault_instance.submit_command = 'cqsub -q %(queue)s -t %(wall_time)u -n %(nodes)u -m vn -C %(run_path)s %(temp_program)s %(temp_script_file)s' % {'queue' : self.__vault_instance.queue, 'wall_time' : self.__vault_instance.wall_time, 'nodes' : self.__vault_instance.nodes, 'run_path' : self.__vault_instance.run_path, 'temp_program' : self.__vault_instance.temp_program, 'temp_script_file' : self.__vault_instance.temp_script_file}
 
  def registerJob(self, job_number):
    self.__vault_instance.recent_output = job_number + '.output'
    self.__vault_instance.recent_error = job_number + '.error'

  def pop_job(self):
    self.__vault_instance.recent_output = ''
    self.__vault_instance.recent_error = ''
    self.__vault_instance.configs_total.pop()
    self.__vault_instance.configs_meas.pop()
    self.__vault_instance.meas_done.pop()
  
  def log(self):
    self.__vault_instance._log = Log(open(self.run_path + '/daemon.log', 'a+'))
    sys.stdout = sys.stderr = self.__vault_instance._log
    return self.__vault_instance._log
  
  def closeLog(self):
    self.__vault_instance._log.close()

  def __init__(self):
    """ Create Vault instance """
    # Check whether we already have an instance
    if Vault.__vault_instance is None:
      # Create and remember instance
      Vault.__vault_instance = Vault.__vault_impl()
      
    # Store instance reference as the only member in the handle
    self.__dict__['_Vault__instance'] = Vault.__vault_instance

  def __getattr__(self, attr):
    """ Delegate access to implementation """
    return getattr(self.__vault_instance, attr)

  def __setattr__(self, attr, value):
    """ Delegate access to implementation """
    return setattr(self.__vault_instance, attr, value)
