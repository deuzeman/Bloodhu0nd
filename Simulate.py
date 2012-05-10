#!/usr/bin/env python
import operator, os, shutil, sys, time
from Calcu0 import *
from Dispatch import *
from Mail import *
from MkDirTree import *
from Sanity import *
from Script import *
from Vault import *

def simulate():
  
  vault = Vault()
  # Turn additional output on or off
  vault["debug"] = True
  
  # We set some of the simulation parameters explicitly here
  vault['meas_skip'] = 2
  vault['configs_minimum'] = 4 * vault['corr_length'] # We need at least some blocks eventually
  # A block needs to roughly be the size of the correlation length,
  # and we need to take into account the double measurement per configuration
  vault['block_size'] = 2 * vault['corr_length'] / vault['meas_skip']
  vault['BGL_time_diff'] = 0 # Correction for the BG/L clock running late (!!!)
  
  if vault['lattice_exists']:
    vault['warms_target'] = vault['warms_base'] / 2
  else:
    vault['warms_target'] = vault['warms_base']
  
  try:
    mkdirtree(vault['run_path']) # Create a new directory, relative to the root
  except OSError, error:
    print >> sys.stderr, error.value # Will still go to terminal
    sys.exit(1) # Somehow, the directory couldn't be created

  vault.log() # Initializes all logging
  os.chdir(vault['run_path']) # Change to our newly created directory

  # Write some initial comments
  log('Daemon initialized at %s.' % time.asctime(time.localtime()))
  log('Now running in quiet mode, all output piped to logfile.')

  # First, make a local copy of the original script and code
  shutil.copyfile(vault['script_file'], vault['temp_script_file'])
  shutil.copyfile(vault['program'], vault['temp_program'])
  shutil.copyfile(vault['rationals_file'], vault['temp_rationals_file'])
  os.chmod(vault['temp_program'], 0755)

  # Now open the script and change it for its initial values
  script = Script(vault['temp_script_file'])
  vault['u0'] = round(2 * float(script['u0']), 3) / 2.0  # Read and round the supplied value for u0
  script['u0'] = vault['u0'] # Make sure the script reflects the internal u0 value
  script.reseed() # Changes the seed value to a random new one
  script['warms'] = min(vault['warms_target'], vault['max_confs'])
  if vault['lattice_exists']:
    script.setReload(vault['lattice_file'])
  else:
    script.setFresh()
  script.setSave(vault['lattice_file'])
  # We start with a smallish sample and make sure to never go above the remaining trajectory space
  script['trajecs'] = min(vault['configs_minimum'], (vault['max_confs'] - int(script['warms']))) # min = 0, see above
  script['traj_between_meas'] = vault['meas_skip']
  script['load_rhmc_params'] = vault['temp_rationals_file'] # This should use the supplied rationals file
  script.write()

  while True: # Start eternal
    try:
      # We dispatch the job and derive its output files from the job number
      vault.registerJob(dispatch(vault["submit_command"]))
    except DispatchError, error:
      log('Attempted execution of BGL run failed!')
      log('\n'.join(error.value))
      sys.exit(1)

    # The submitting worked if we got here.
    check_output_sanity()

    if not vault['lattice_written_flag']:
      # We're apparently asking too much. We need to decrease maxconfs
      log('Lattice not saved yet! Decreasing maximum size of simulation...')
      vault['max_confs'] = int(int(vault['configs_total'][-1]) * 0.95)
      log('Maximum number of configurations changed to %u.' % vault['max_confs'])
      # This job might still contain a lot of useful data, though.
      # We'll use it, unless it didn't even finish its warmups

    if not vault['warms_done_flag']:
      # This is a pretty bad situation, since it means we just wasted time
      # We'll need to break up the warms and make sure to save the lattice regularly
      log("Warmups did not finish! Switching to chaining the thermalization.")
      vault.pop_job() # Remove the useless job

      warms_needed = vault['warms_target'] - vault['warms_done']      
      if vault['debug']:
        log('[DEBUG] Found that %u warms are needed still.' % warms_needed)
      warms_feasible = min(warms_needed, vault['max_confs'])
      if vault['debug']:
        log('[DEBUG] That means %u warms will be done this round,' % warms_feasible)
      confs_feasible = max(vault['max_confs'] - warms_needed, 0)
      if vault['debug']:
        log('[DEBUG] while %u trajectories can be run.' % confs_feasible)

      script.reseed()
      script['warms'] = warms_feasible
      script['trajecs'] = min(int(script['trajecs']), confs_feasible)
      if (int(script['warms']) + int(script['trajecs'])) == 0:
        log('Detected zero-size simulation requested - aborting.')
        sys.exit(1) # We don't want to run this
      if (float(script['u0']) <= 0.0000):
        log('Detected a zero value set for u0 - aborting.')
        sys.exit(1)
      script.write()
      continue

    result_code = check_u0()
    if result_code == 0: # We made it!
      log('A stable value for u0 was found at %.4f.' % vault['u0'])
      log('Killing daemon at %s.' % time.asctime(time.localtime()))
      vault.closeLog()
      mail_success()
      sys.exit(0)
    elif result_code == 1: # We found a different value for u0
      log("A different value for u0 was found at %.4f." % vault['u0'])
      log("Restarting the simulation with the new value.")
      script['u0'] = vault['u0']
      script.reseed()
      if vault['lattice_written_flag']:
        vault['warms_target'] = vault['warms_base'] / 2
      else:
        vault['warms_target'] = vault['warms_base']
      script['warms'] = vault['warms_target']
      if vault['lattice_exists']:
        script.setReload(vault['lattice_file'])
      else:
        script.setFresh()
      # We'll take the previous total as a guide for the number of configs needed here
      confs_meas_total = reduce(operator.add, vault['configs_meas'])
      confs_feasible = max(0, min(vault['max_confs'] - vault['warms_target'], max(reduce(operator.add, vault['configs_total'], 0), vault['configs_minimum'])))
      script['trajecs'] = confs_feasible
      if (int(script['warms']) + int(script['trajecs'])) == 0:
        log('Detected zero-size simulation requested - aborting.')
        sys.exit(1) # We don't want to run this
      if (float(script['u0']) <= 0.0000):
        log('Detected a zero value set for u0 - aborting.')
        sys.exit(1)
      script.write()

      # Reset all values for the previous run in the vault variable
      vault['warms_done'] = 0
      vault['configs_meas'] = []
      vault['configs_total'] = []
      vault['meas_done'] = []
      vault['meas_stats'] = []
      vault['noise_ratio'] = 100 # This is a dummy value...

    else: # We have to have code -1 now - incomplete
      log("Precision insufficient to determine result, extending run")
      log("Signal to noise ratio was found to be %3.2f" % vault['noise_ratio'])
      conf_meas_total = reduce(operator.add, vault['configs_meas'], 0)
      confs_still_needed = max((int((vault['noise_ratio'] ** 2) - 1) * conf_meas_total), \
                                     vault['corr_length'])
      log("Concluded that about %u configurations are needed at least" % confs_still_needed)
      log("to push the 2-sem range down to the difference between u0 values.")
      log("Changing the script accordingly.")

      warms_still_needed = vault['warms_target'] - vault['warms_done']
      if vault['debug']:
        log('[DEBUG] Found that %u warms are needed still.' % warms_still_needed)
      warms_feasible = min(warms_still_needed, vault['max_confs'])
      if vault['debug']:
        log('[DEBUG] That means %u warms will be done this round,' % warms_feasible)
      confs_feasible = max(vault['max_confs'] - warms_still_needed, 0)
      if vault['debug']:
        log('[DEBUG] and there is room for %u configs following that.' % confs_feasible)
      script.reseed()
      script['warms'] = warms_feasible
      if vault['lattice_exists']:
        script.setReload(vault['lattice_file'])
      else:
        script.setFresh()
      script['trajecs'] = min(confs_still_needed, confs_feasible)
      if (script['warms'] + script['trajecs']) == 0:
        log('Detected zero-size simulation requested - aborting.')
        sys.exit(1) # We don't want to run this
      if (script['u0'] == 0):
        log('Detected a zero value set for u0 - aborting.')
        sys.exit(1)
      script.write()
