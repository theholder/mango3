import mango
import asyncore

class Bot(mango.ConnMgr):

	def _msgHandler(self, nick, channel, message):
		print("%s %s %s" % (nick, channel, message))
		if message == "!o":
			self.respond("o;", "#" + channel)

	def _joinHandler(self, nick, channel):
		print("%s joined %s" % (nick, channel))

	def _handlePart(self, nick, channel):
		print("%s parted %s" % (nick, channel))


c = Bot()
c._run("irc.thetechshed.com", 6667, "testy", ["#ruur"])

asyncore.loop()
