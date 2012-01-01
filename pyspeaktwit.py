#!/usr/bin/env python
# -*- coding: utf-8 -*-

# leggiamo i tweet con espeak con python-twitter


# errori random dalle librerie.. perfortuna rarissimi
"""
Traceback (most recent call last):
  File "./pyspeaktwit.py", line 158, in <module>
    t.FetchTimeline()
  File "./pyspeaktwit.py", line 82, in FetchTimeline
    self.timeline_raw = self.api.GetFriendsTimeline() #self.timeline_raw = self.api.GetPublicTimeline()
  File "/usr/local/lib/python2.6/dist-packages/python_twitter-0.8.2-py2.6.egg/twitter.py", line 2580, in GetFriendsTimeline
    data = self._ParseAndCheckTwitter(json)
  File "/usr/local/lib/python2.6/dist-packages/python_twitter-0.8.2-py2.6.egg/twitter.py", line 3671, in _ParseAndCheckTwitter
    raise TwitterError("Capacity Error")
twitter.TwitterError: Capacity Error
"""


import twitter
import datetime
import os
from time import sleep
import copy
import daemon
#api = twitter.Api()

#####################
# CONF
timeout_lettura_twits = 30 #in secondi
pronuncia_intestazione = True
DAEMON_MODE = False
LANGUAGE='it'
COMANDO = """espeak -v %s -s 100 -p 100 "%s" """ % LANGUAGE
auth_dict = dict(consumer_key='',consumer_secret='', access_token_key='', access_token_secret='')
#
# END CONF
#####################

class Tweet:
	def __init__(self, msg):
		self.data = datetime.datetime.strptime(msg.created_at.replace('+0000', ''), "%c" ) 
		self.testo = msg.GetText()
		self.testo = self.testo.encode('utf-8', 'ignore').replace("\"", "'")
		self.user = msg.GetUser()
		self.creato_da = self.user.GetName()
		self.creato_da = self.creato_da.encode('utf-8', 'ignore')
		self.msg_raw = msg
	def __hash__(self):
		return hash(('testo', self.testo, 'date', self.data))
	def __eq__(self, other):
	    return self.testo==other.testo and self.data==other.data
	def __str__(self):
		return "[%s %s] %s".encode('ascii', 'ignore') % (self.creato_da, self.data, self.testo[:37])
	def __repr__(self):
		return "[%s %s] %s".encode('ascii', 'ignore') % (self.creato_da, self.data, self.testo[:37])
	#def __unicode__(self):
	#	return "[%s %s] %s".encode('utf-8', 'xmlcharrefreplace') % (self.user, self.data, self.testo[:12])
	
class TweetSpeak:
	def __init__(self, **auth_dict):
		self.COMANDO = COMANDO
		self.timeout = timeout_lettura_twits
		self.twitter = twitter.Api(**auth_dict)
		self.username = 'verdebinario'		
		self.api = self.twitter
		self.last = None
		self.latests = []
		self.timeln_username = []
		self.timeln_username_old = []
		self.timeln_all = []
		self.timeln_all_old = []		
	def FetchTimeline(self, username=None, numero_di_tweet=None):
		self.n = numero_di_tweet
		# setto l'alias per generalizzare il resto del codice
		if username: 
			self.timeln_username_old = copy.deepcopy(self.timeln_username)
			self.timeln_username = []
			self.timeline_raw = self.api.GetUserTimeline(username)	
			for i in self.timeline_raw: self.timeln_username.append(Tweet(i))
			self.timeln = self.timeln_username ; self.timeln_old = self.timeln_username_old 
		else:
			self.timeln_all_old = copy.deepcopy(self.timeln_all)
			self.timeln_all = []
			self.timeline_raw = self.api.GetFriendsTimeline() #self.timeline_raw = self.api.GetPublicTimeline()
			self.timeline_raw += self.api.GetUserTimeline(self.username)	
			for i in self.timeline_raw: self.timeln_all.append(Tweet(i))
			# pulisco i doppioni
			self.timeln_all = [i for i in set(self.timeln_all)]
			# riordino in base alla data di creazione (la fiera dei trucchi in python !)
			self.timeln_all = sorted(self.timeln_all, key=lambda x: x.data, reverse=True)
			self.timeln = self.timeln_all ; self.timeln_old = self.timeln_all_old 
		try: self.last = self.timeln[0]
		except: print 'Nessun messaggio trovato !'	
		return self.timeln[:numero_di_tweet]
	def GetLatests(self,username=None):
		#if not self.timeln_old: self.timeln(self.username)
		#if not username: self.timeline()
		#else: self.timeline(username)
		if self.timeln_old:
			clean_dup = set(self.timeln + self.timeln_old)
			self.latests = [i for i in clean_dup if not i in self.timeln_old ]
		# stile vecchio :)
		#if self.timeln_old:
		#	for i in self.timeln:
		#		try: [u.data for u in self.timeln_old].index(i.data)
		#		except: self.latests.append(i)
		#if not self.latests:
		#	self.latests = [self.last]	
		print 'ho trovato %d twits nuovi' % len(self.latests)
		return self.latests	
	def SayIt(self, i):
		if pronuncia_intestazione != None:
			g_d = self.last.msg_raw.created_at.split(' ')
			ore = g_d[3].split(':')
			creato_il = '' #"giorno %s %s ore %s e %s" % (g_d[2], g_d[1], ore[0], ore[1]  )
			f_msg = "Twittato da %s %s" % ( i.creato_da, creato_il)
			os.system(self.COMANDO % f_msg)
		os.system(self.COMANDO % i.testo)
	def SayLatests(self):
		#self.GetLatest(username)
		for i in self.latests:
			self.SayIt(i)
			print i
	def SayLast(self):
		#self.GetLatest(username)
		self.SayIt(self.timeln[0])			
	def SayAll(self):
		#self.GetLatest(username)		
		for i in self.timeln:
			self.SayIt(i)
	def CleanTimeLine(self):
		self.last = None
		self.latests = []
		self.timeln = None
		self.timeln_old = None
		self.timeln_username = None
		self.timeln_username_old = None
		self.timeln_all = None
		self.timeln_all_old = None	
				

# solo per python 2.6
# with daemon.DaemonContext():
if __name__ == '__main__':
	t = TweetSpeak(**auth_dict)
	
	if DAEMON_MODE:
		context = daemon.DaemonContext()
		context.open()
		try:
			while 1:
				t.FetchTimeline()
				t.GetLatests()
				t.SayLatests()
				sleep(t.timeout)
		finally: context.close()
	else:
		while 1:
			print 'leggo i twits'
			t.FetchTimeline()
			print 'la time line è composta da %d elementi' % len(t.timeln)
			t.GetLatests()
			t.SayLatests()
			# ogni 30 secondi legge gli ultimi tweets
			sleep(t.timeout)


