#!/usr/bin/env python

import smtplib

def mail_success():
  global vault

  recipients = []
  mssgstream = open('/home5/pallante/usr/bin/u0finder_bin/mssg_success.txt', 'r')
  mssg = mssgstream.read()
  mssg = mssg.replace('<run_name>', vault.run_name)
  mssg = mssg.replace('<log_file>', vault.run_path + '/daemon.log')
  mssgstream.close()
  logstream = open(vault.run_path + '/daemon.log', 'r') ## NB
  mssg += logstream.read()
  logstream.close()

  session = smtplib.SMTP('localhost')
  smtpresult = session.sendmail('pallante@bglfen5.service.rug.nl', recipients, mssg)

  if smtpresult:
    pass # Not handled for the moment

def mail_hung(job_number):
  global vault

  recipients = []
  mssgstream = open('/home5/pallante/usr/bin/u0finder_bin/mssg_hung.txt', 'r')
  mssg = mssgstream.read()
  mssgstream.close()
  mssg = mssg.replace('<job_number>', job_number)

  session = smtplib.SMTP('localhost')
  smtpresult = session.sendmail('pallante@bglfen5.service.rug.nl', recipients, mssg)

  if smtpresult:
    pass # Not handled for the moment

def mail_suspicious(job_number):
  global vault

  recipients = []
  mssgstream = open('/home5/pallante/usr/bin/u0finder_bin/mssg_suspicious.txt', 'r')
  mssg = mssgstream.read()
  mssgstream.close()
  mssg = mssg.replace('<job_number>', job_number)

  session = smtplib.SMTP('localhost')
  smtpresult = session.sendmail('pallante@bglfen5.service.rug.nl', recipients, mssg)

  if smtpresult:
    pass # Not handled for the moment
