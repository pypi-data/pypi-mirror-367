#  jack_audio_player/jack_audio_player/__init__.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Python Jack client which plays audio files.
"""
import sys, queue, threading, logging
from math import floor
import jack
import numpy as np
import soundfile as sf

__version__ = "1.0.1"


class JackAudioPlayer:

	BUFFER_SIZE	= 25

	def __init__(self, client_name = 'jack_player', auto_connect = False):
		self.__q = queue.Queue(maxsize = self.BUFFER_SIZE)
		self.client = jack.Client(client_name, no_start_server=True)
		self.client.set_shutdown_callback(self.shutdown_callback)
		self.client.set_xrun_callback(self.xrun_callback)
		self.client.set_process_callback(self.__process_callback)
		self.__real_process_callback = self.__play_callback
		self.client.activate()
		self.client.get_ports()
		self.client.outports.register('left')
		self.client.outports.register('right')
		self.__native_dtype = np.dtype('float32')
		if auto_connect:
			self.auto_connect()
		self.__playing = False

	@property
	def client_name(self):
		return self.client.name

	@property
	def output_ports(self):
		return self.client.outports

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		pass

	def auto_connect(self):
		target_ports = self.client.get_ports(is_physical=True, is_input=True, is_audio=True)
		for source, target in zip(self.client.outports, target_ports):
			source.connect(target)

	def play_file(self, filename):
		soundfile = sf.SoundFile(filename)
		self.play_python_soundfile(soundfile)

	def play_python_soundfile(self, soundfile):
		blocksize = self.client.blocksize
		timeout = self.client.blocksize * self.BUFFER_SIZE / self.client.samplerate
		self.__playing = True
		def __fill_buffer():
			block_generator = soundfile.blocks(blocksize = blocksize,
				dtype = self.__native_dtype, fill_value = 0)
			if soundfile.channels == 1:
				for data in block_generator:
					if soundfile.closed or not self.__playing: break
					self.__q.put((data, data), timeout = timeout)
			else:
				for data in block_generator:
					if soundfile.closed or not self.__playing: break
					stereo_data = np.hsplit(data, 2)
					self.__q.put((
						stereo_data[0].reshape(blocksize),
						stereo_data[1].reshape(blocksize)
					), timeout = timeout)
		threading.Thread(target = __fill_buffer, daemon = True).start()

	def play_native_stereo(self, left, right):
		if len(left) != len(right):
			raise RuntimeError("Channels must be the same length")
		chunk_len = self.client.blocksize
		self.__playing = True
		def __fill_buffer():
			for start in range(0, len(left), chunk_len):
				if not self.__playing: break
				left_chunk = left[ start : start + chunk_len ]
				right_chunk = right[ start : start + chunk_len ]
				if len(left_chunk) < chunk_len:
					left_chunk = self.pad(left_chunk, chunk_len)
					right_chunk = self.pad(right_chunk, chunk_len)
				self.__q.put( ( left_chunk, right_chunk ) )
		threading.Thread(target = __fill_buffer, daemon = True).start()

	def play_native_interleaved(self, samples):
		chunk_len = self.client.blocksize * 2
		self.__playing = True
		def __fill_buffer():
			for start in range(0, len(samples), chunk_len):
				if not self.__playing: break
				chunk = samples[ start : start + chunk_len ]
				if len(chunk) < chunk_len:
					chunk = self.pad(chunk, chunk_len)
				self.__q.put( ( chunk[::2], chunk[1::2] ) )
				if not self.__playing: break
		threading.Thread(target = __fill_buffer, daemon = True).start()

	def play_int16_stereo(self, left, right):
		return self.play_native_stereo(self.int16_to_native(left), self.int16_to_native(right))

	def play_int16_interleaved(self, samples):
		return self.play_native_interleaved(self.int16_to_native(samples))

	def stop(self):
		if self.__playing:
			self.__real_process_callback = self.__stopping_callback

	def __process_callback(self, frames):
		self.__real_process_callback(frames)

	def __play_callback(self, frames):
		try:
			stereo_samples = self.__q.get_nowait()
		except queue.Empty:
			self.__zero_ports()
		except Exception as e:
			self.__callback_exit(str(e))
		else:
			for samples, port in zip(stereo_samples, self.client.outports):
				a = port.get_array()
				a[:] = samples

	def __stopping_callback(self, frames):
		try:
			while self.__q.get_nowait():
				pass
		except queue.Empty:
			self.__zero_ports()
			self.__real_process_callback = self.__play_callback

	def __callback_exit(self, msg):
		logging.error(msg)
		self.__zero_ports()
		raise jack.CallbackExit

	def __zero_ports(self):
		for port in self.client.outports:
			port.get_array().fill(0)
		self.__playing = False

	def playing(self):
		return self.__playing

	def shutdown_callback(self, status, reason):
		"""
		The argument status is of type jack.Status.
		"""
		self.__callback_exit('Server shutdown!')

	def xrun_callback(self, delayed_usecs):
		"""
		The callback argument is the delay in microseconds due to the most recent XRUN
		occurrence. The callback is supposed to raise CallbackExit on error.
		"""

	def pad(self, ar, chunk_len):
		return np.concatenate((ar, np.zeros(chunk_len - len(ar), dtype = self.__native_dtype)))

	def int16_to_native(self, ar):
		scaled = ar / 32768
		return scaled.astype(self.__native_dtype)


#  end jack_audio_player/__init__.py
