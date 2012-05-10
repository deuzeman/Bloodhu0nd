from Vault import *
import operator

def check_output_sanity():
  vault = Vault()
  output_file = vault['recent_output']

  if os.path.getsize(vault.recent_error) > 0:
    # Somehow an error occurred. This could be a walltime thing, 
    # or something more sinister. Problem is, with the latest changes
    # Stella is not telling us outright anymore! We could try to be
    # super clever about this, but that would probably just introduce
    # more sophisticated ways of being completely wrong.
    # Until proper functionality is restored, I'm just going to go the easy
    # way here and assume it was a walltime error.
    # It probably is 90% of the times.
    # Caveat emptor, however!
    pass

  # Reset all values
  configs_total = 0
  configs_meas = 0
  accepts = 0
  meas_done = 0
  vault['warms_done_flag'] = False
  vault['lattice_written_flag'] = False

  output_stream = open(output_file, 'r')

  for line in output_stream:
    line = line.lower()
    if line.startswith('accept') or line.startswith('reject'):
      configs_total += 1
    elif line.startswith('warmups completed'):
      vault['warms_done_flag'] = True
      break
  if vault['debug']:
    log('[DEBUG] Found a total of %u warmups in the output file.' % configs_total)
  for line in output_stream: # Now starting the line AFTER "warmups completed"
    line = line.lower()
    if line.startswith('accept') or line.startswith('reject'):
      configs_total += 1
      configs_meas += 1
      if line.startswith('accept'):
        accepts += 1
    elif line.startswith('plaq:'):
      meas_done += 2
    elif line.startswith('saved gauge configuration'):
      vault['lattice_written_flag'] = True

  output_stream.close() # Tidy up the file descriptor, this could get ugly otherwise

  if vault['lattice_written_flag']:
    vault['lattice_exists'] = True
    vault['warms_done'] += (configs_total - configs_meas)

  vault['configs_total'].append(configs_total)
  vault['configs_meas'].append(configs_meas)
  if vault['debug']:
    log('[DEBUG] Found a total of %u measured configs so far.' % reduce(operator.add, vault['configs_meas'], 0))
  vault['meas_done'].append(meas_done)
