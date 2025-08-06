#  jack_audio_player/test.py
#
#  Copyright 2025 liyang <liyang@veronica>
#
import logging
from os.path import dirname, join
from threading import Timer
from time import sleep
import soundfile as sf
from jack_audio_player import JackAudioPlayer

def stop():
	global player
	player.stop()


if __name__ == "__main__":
	global player
	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)4d] %(levelname)-8s %(message)s"
	)

	player = JackAudioPlayer(auto_connect = True)
	for filename in [
		'mono-16bit-int.wav',
		'mono-32bit-float.wav',
		'stereo-16bit-int.wav',
		'stereo-32bit-float.wav'
	]:
		logging.debug('Playing %s', filename)
		player.play_file(join(dirname(__file__), 'res', filename))
		while player.playing():
			logging.debug('Playing ...')
			sleep(0.25)

	filename = 'harley-davison.wav'
	logging.debug('Playing %s', filename)
	path = join(dirname(__file__), 'res', filename)
	t = Timer(2.0, stop)
	t.start()
	player.play_file(path)
	while player.playing():
		logging.debug('Playing ...')
		sleep(0.25)
	sleep(0.5)

	logging.debug('Playing and prematurely closing %s', filename)
	with sf.SoundFile(path) as soundfile:
		player.play_python_soundfile(soundfile)
		sleep(0.5)



#  end jack_audio_player/test.py
