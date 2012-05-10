#!/usr/bin/env python

import operator
import random
from Vault import *

def _average(seq):
  return reduce(operator.add, seq, 0)/float(max(1, len(seq)))

def _variance(seq):
  sqave = _average(seq) ** 2
  avesq = _average([elem ** 2 for elem in seq])
  return (avesq - sqave)

def _read_plaq():
  vault = Vault()
  results = []

  fstream = open(vault['recent_output'], 'r')
  for line in fstream:
    line = line.lower()
    if line.startswith("warmups completed"):
      break
  for line in fstream: # Now starting the line AFTER "warmups completed"
    if line.lower().startswith('plaq:'): # NB: There's also a 'plaquette action' tag
      fragments = line.split()
      results.extend([float(frag) for frag in fragments[1:]]) # We can use both
  fstream.close() # Tidy up the file descriptor, this could get ugly otherwise
  vault['meas_stats'].extend(results)

def _calc_u0_val(average_value):
  return round(pow((average_value / 3.0), 0.25), 4)

def _bootstrap_sample(seq):
  sample = []
  for idx in range(1, len(seq)):
    sample.append(random.choice(seq))
  return sample

def check_u0():
  vault = Vault()
  _read_plaq()

  conf_meas_total = reduce(operator.add, vault['configs_meas'], 0)
  if (conf_meas_total < vault['configs_minimum']):
    log('[DEBUG] Detected a number of configurations below the minimum needed,')
    log('[DEBUG] so calculating u0 is skipped altogether at this point.')
    # The following is a bit of hack, that should allow the program to continue properly.
    vault['noise_ratio'] = (float(vault['configs_minimum']) / float(max(conf_meas_total, 1)))**0.5
    return -1 # This is obviously inconclusive...

  # Calculate the new u0 values from the plaquettes
  newu0 = _calc_u0_val(_average(vault['meas_stats']))
  blocks = []
  for idx in range(0, len(vault['meas_stats']) / vault['block_size']):
    blocks.append(_average(vault['meas_stats'][idx * vault['block_size'] : \
                           idx * vault['block_size'] + vault['block_size']]))
  blocked_vals = (len(vault['meas_stats']) / vault['block_size']) * vault['block_size']
  if blocked_vals < len(vault['meas_stats']):
    blocks.append(_average(vault['meas_stats'][blocked_vals : ]))
  if vault["debug"]:
    log('[DEBUG] Blocks are determined at %s.' % str(blocks))

  # Bootstrap the sample to get an error estimate
  bootvals = []
  for index in range(0, 1000):
    bootvals.append(_calc_u0_val(_average(_bootstrap_sample(blocks))))
  
  # We now have a series of bootstrap samples of the blocks that should estimate the variance
  newu0sd = _variance(bootvals) ** 0.5
  if vault["debug"]:
    log('[DEBUG] Standard deviation was found to be %6.5f.' % newu0sd)

  # Compare with the previous result
  newu0 = round(newu0 * 2, 3) / 2
  if vault["debug"]:
    log('[DEBUG] The rounded value for u0 for these runs is %5.4f.' % newu0)
    log('[DEBUG] This implies a difference in u0 of %5.4f.' % abs(newu0 - vault['u0']))
  if (newu0 == vault['u0']) and (newu0sd < 1.25E-4):
    return 0 # Found a stable u0 value
  if (newu0 < vault['u0'] - 2 * max(newu0sd, 1.25E-4)) or (newu0 > vault['u0'] + 2 * max(newu0sd, 1.25E-4)):
    vault['u0'] = newu0
    return 1 # New u0 value found
  else: # Inconclusive, more statistics needed
    vault['noise_ratio'] = newu0sd / max(abs(newu0 - vault['u0']), 1.25E-4) # u0dif might be 0...
    if vault["debug"]:
      log('[DEBUG] Noise ratio was found to be %2.1f.' % vault['noise_ratio'])
    return -1
