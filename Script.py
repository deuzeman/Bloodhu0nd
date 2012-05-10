#!/usr/bin/env python

import random

class Script:
  
  def __init__(self, fileName):
    self.d_fileName = fileName
    stream = open(self.d_fileName, 'r')
    self.d_lines = stream.readlines()
    stream.close()
    self.d_seeder = random.Random()

  def __getitem__(self, key):
    for line in self.d_lines:
      frags = line.split()
      if (len(frags) > 0) and (key == frags[0]):
          return ' '.join(frags[1:])
    return ''
  
  def __setitem__(self, key, value):
    for idx in range(0, len(self.d_lines)):
      frags = self.d_lines[idx].split()
      if (len(frags) > 0) and key == frags[0]:
        self.d_lines[idx] = key + ' ' + str(value)
  
  def setFresh(self):
    for idx in range(0, len(self.d_lines)):
      frags = self.d_lines[idx].split()
      if (len(frags) > 0) and frags[0] == 'reload_serial':
        self.d_lines[idx] = 'fresh'

  def setReload(self, value):
    for idx in range(0, len(self.d_lines)):
      frags = self.d_lines[idx].split()
      if (len(frags) > 0) and frags[0] == 'fresh':
        self.d_lines[idx] = 'reload_serial ' + str(value)
  
  def setForget(self):
    for idx in range(0, len(self.d_lines)):
      frags = self.d_lines[idx].split()
      if (len(frags) > 0) and frags[0] == 'save_serial':
        self.d_lines[idx] = 'forget'

  def setSave(self, value):
    for idx in range(0, len(self.d_lines)):
      frags = self.d_lines[idx].split()
      if (len(frags) > 0) and ((frags[0] == 'forget') or (frags[0] == 'save_serial')):
        self.d_lines[idx] = 'save_serial ' + str(value)

  def reseed(self):
    for idx in range(0, len(self.d_lines)):
      frags = self.d_lines[idx].split()
      if (len(frags) > 0) and frags[0] == 'iseed':
        self.d_lines[idx] = 'iseed ' + str(self.d_seeder.randint(1, 9999999))

  def write(self):
    stream = open(self.d_fileName, 'w')
    for line in self.d_lines:
      if not (line[-1] == '\n'):
        line += '\n'
      stream.write(line)
    stream.close()
