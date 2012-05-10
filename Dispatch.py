#!/usr/bin/env python

import os, re, time
import Cobalt.Proxy, Cobalt.Util
from Excepts import *
from Log import *
from Mail import *
from Vault import *

def _passed_wall_time(status):
  if status['starttime'] in ('-1', 'BUG', 'N/A', None):
    return False
  # Sometimes clearing a job takes a little while and we don't want to send any fake messages
  # I therefore give it ten minutes over the strict wall time
  wall_time = int(status['walltime']) + 10 
  run_time = int(time.time() - float(status['starttime'])) / 60
  return run_time > wall_time

def _file_is_quiet(status):
  vault = Vault()
  if status['starttime'] in ('-1', 'BUG', 'N/A', None):
    return False
  vault = Vault()
  if not os.path.isfile(vault['recent_output']):
    return False
  output_path = vault['run_path'] + '/' + vault['recent_output']
  last_time = os.path.getmtime(output_path)
  down_time = ((int(time.time()) - last_time) / 60) - vault['BGL_time_diff']
  return (down_time > 15) # i.e., file has not changed over the last fifteen minutes

def dispatch(cmd_sub):
  vault = Vault()
  subreport = os.popen(cmd_sub) # Submit the job and store the std out report
  job_id = subreport.readlines()
  subreport.close() # Can't hurt to potentially free up these resources
  
  if len(job_id) != 1 or not re.match("^[0-9]+$", job_id[0]): # See if the output is malformed
    raise DispatchError(job_id) # We'll let the calling function handle this problem

  job_id = job_id[0].strip()
  vault.registerJob(job_id)
  log("Submitted successfully at %s." % time.asctime(time.localtime()))
  log("The job was assigned the ID %s." % job_id)
  
  try:
    cqm = Cobalt.Proxy.queue_manager()
  except Cobalt.Proxy.CobaltComponentError:
    log("Failed to connect to Cobalt queue manager")
    sys.exit(1)
  
  query = [{'tag':'job', 'jobid':job_id, 'walltime':'*', 'starttime':'*'}]
  
  suspicious_report = False
  while True:
    qresult = cqm.GetJobs(query)
    if len(qresult) == 0:
      break # The job terminated
    status = qresult[0]

    if _passed_wall_time(status):
      pass # mail_hung(job_id)
      raise DispatchError(['Job passed its wall time!', 'Aborting run.'])
    if not suspicious_report: # We want to send this mail only once...
      if _file_is_quiet(status):
        suspicious_report = True
        # mail_suspicious(job_id)
    time.sleep(300) # Wait for 5 minutes before checking again

  log("Registered termination at %s." % time.asctime(time.localtime()))
  return job_id
