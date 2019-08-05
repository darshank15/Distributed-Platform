from playsound import playsound
class AlarmDevice():
	def __init__(self,name):
		self.deviceName = name
	def ring(self):	
		playsound('warning.mp3')

# s = AlarmDevice('test')
# s.ring()