#  jack_midi_split/test.py
#
#  Copyright 2025 liyang <liyang@veronica>
#
"""
Test functions for jack_midi_split
"""
import sys, os, threading, mido, struct, logging
from jack import Client as JackClient, JackError
from jack_midi_split import MidiSplitter, NOTE_ON_MASK, NOTE_ON_STAT

PORT_NUMBER_MASK = 0x0F

class MidiSource(JackClient):

	def __init__(self):
		super().__init__(f'msplt-source', no_start_server = True)
		self.output_port = self.midi_outports.register('output')
		self.set_process_callback(self.__process_callback)
		self.activate()
		self.messages = [
			mido.Message('control_change', channel = 0, control = 0x00, value = 0),
			mido.Message('control_change', channel = 0, control = 0x20, value = 0),
			mido.Message('program_change', channel = 0, program = 77)
		]
		for note_number in range(128):
			self.messages.append(mido.Message('note_on', note = note_number))
			self.messages.append(mido.Message('note_off', note = note_number))
		self.emit = False

	def __process_callback(self, frames):
		global finish_event
		self.output_port.clear_buffer()
		if self.emit:
			if len(self.messages):
				msg = self.messages.pop(0)
				self.output_port.write_midi_event(0, msg.bytes())
			else:
				finish_event.set()


class Checker(JackClient):

	def __init__(self, port_number):
		super().__init__(f'msplt-checker-{port_number:02d}', no_start_server = True)
		self.port_number = port_number
		self.input_port = self.midi_inports.register('input')
		self.set_process_callback(self.__process_callback)
		self.activate()

	def __process_callback(self, frames):
		for offset, data in self.input_port.incoming_midi_events():
			if len(data) == 3:
				status, val_1, val_2 = struct.unpack('3B', data)
				if status & NOTE_ON_MASK == NOTE_ON_STAT:
					test_result = 'OK' if val_1 & PORT_NUMBER_MASK == self.port_number else 'FAIL'
					print(f'port {self.port_number:02d}: note {val_1:02x} {test_result}')
				else:
					msg = mido.Message.from_bytes([status, val_1, val_2])
					print(f'port {self.port_number:02d}: {msg}')
			elif len(data) == 2:
				msg = mido.Message.from_bytes(struct.unpack('2B', data))
				print(f'port {self.port_number:02d}: {msg}')
			else:
				logging.error('Invalid MIDI message len: %d', len(data))


if __name__ == "__main__":
	global finish_event
	finish_event = threading.Event()
	try:
		midi_source = MidiSource()
	except JackError:
		print('Could not connect to JACK server. Is it running?')
		sys.exit(1)
	splitter = MidiSplitter('msplt-splitter')
	midi_source.output_port.connect(splitter.input_port)
	checkers = { port_number:Checker(port_number) for port_number in range(16) }
	for port_number, checker in checkers.items():
		splitter.output_ports[port_number].connect(checker.input_port)
		for note_number in range(128):
			if note_number & PORT_NUMBER_MASK == port_number:
				splitter.assign_note(note_number, port_number)
	print('Press Enter key to start...')
	try:
		input()
		print('starting')
		midi_source.emit = True
		finish_event.wait()
	except KeyboardInterrupt:
		pass
	sys.exit(0)


#  end jack_midi_split/test.py
