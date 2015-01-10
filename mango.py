import asyncore, socket
import re

class ConnMgr(asyncore.dispatcher_with_send):
	def __init__(self):
		self.out_buffer = b''
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ping_re = re.compile('^PING (?P<payload>.*)', re.IGNORECASE)
		self.join_re = re.compile(':(?P<nick>.*?)!\S+\s+?JOIN\s+:\s*#(?P<channel>[-\w]+)')
		self.part_re = re.compile(':(?P<nick>.*?)!\S+\s+?PART\s+#(?P<channel>[-\w]+)')
		self.chanmsg_re = re.compile(':(?P<nick>.*?)!\S+\s+?PRIVMSG\s+#(?P<channel>[-\w]+)\s+:(?P<message>[^\n\r]+)')
		self.registeredRe = re.compile(':(?P<server>.*?)\s+(?:376|422)')
		self.privmsg_re = re.compile(':(?P<nick>.*?)!~\S+\s+?PRIVMSG\s+[^#][^:]+:(?P<message>[^\n\r]+)')
		#self.userlist_re = re.compile('^:.* 353 %s = (?P<chan>.*?) :(?P<names>.*)' %  self.nick)
		self._channels = None
		self.nick = None


	def handle_close(self):
		self.close()


	def _patterns(self):
		return (
			(self.ping_re, self._handlePing),
			(self.join_re, self._joinHandler),
			(self.chanmsg_re, self._msgHandler),
			(self.registeredRe, self._handleRegistered),
			(self.privmsg_re, self._handlePrivmsg),
			(self.part_re, self._handlePart),
		)

	def _send(self, data):
		data = data + "\r\n"
		self.send(data.encode("utf-8"))

	def writeable(self):
		return True

	def _msgHandler(self, nick, channel, message):
		pass


	def _joinHandler(self, nick, channel):
		pass

	def _handlePrivmsg(self, nick, message):	
		pass

	def _handlePart(self, nick, channel):
		pass


	def respond(self, message, channel = None, nick = None):
		try:
			message = message.decode("utf-8")
		except:
			message = message
		if channel:
			self._send("PRIVMSG %s :%s" % (channel, message))

	def auth(self):
		self._send("NICK %s" % self.nick)
		self._send("USER %s %s blah :%s" % (self.nick, "a", self.nick))


	def _handlePing(self, payload):
		self._send("PONG %s" % payload)

	def _handleRegistered(self, server):
		print("Registered at %s" % server)
		self._send("MODE %s +B" % self.nick)
		self.registered = True
		self._chanloop()

	def _chanloop(self):
		for chan in self._channels:
			print(">> %s " % chan)
			self.join(chan)


	def join(self, chan):
		self._send("JOIN %s" % chan)
		if not chan in self._channels:
			self._channels.append(str(chan))

	def _connect(self, server, port):
		self.connect((server, port))
		self.auth()


	def _run(self, server, port, nick, chans):
		self.nick = nick
		self._channels = chans
		self._connect(server, port)

	def state(self):
		return self._state

	def handle_read(self):
		data = self.recv(3024).decode()
		for d in data.split("\r\n"):
			patterns = self._patterns()
			for pattern, callback in patterns:
				match = pattern.match(d)
				if match:
					callback(**match.groupdict())
