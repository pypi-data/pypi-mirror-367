#  jack_midi_split/__init__.py
#
#  Copyright 2025 liyang <liyang@veronica>
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
Provides a jack client which can be instructed to split noteon/noteoff events
between multiple output ports.
"""
import struct, logging
from jack import Client as JackClient, JackError

__version__ = "1.0.0"

NOTE_ON_MASK = 0xE0
NOTE_ON_STAT = 0x80
ALL_NOTES_OFF_MSG = bytearray.fromhex('B07B')


class MidiSplitter(JackClient):

	def __init__(self, client_name = 'jack-midi-splitter'):
		super().__init__(client_name, no_start_server = True)
		self.__real_process_callback = self.__normal_process_callback
		self.set_process_callback(self.__process_callback)
		self.set_shutdown_callback(self.__shutdown_callback)
		self.input_port = self.midi_inports.register('input')
		self.output_ports = {
			port_number:self.midi_outports.register(f'output-{port_number:02d}') \
			for port_number in range(16) }
		self.all_off_messages = [ bytearray([ cc, 0x7B ]) for cc in range(0xB0, 0xC0) ]
		self.clear_all_assignements()
		self.bypassed = False
		self.activate()

	def clear_all_assignements(self):
		self.note_assignments = { note_number:0x00 for note_number in range(128) }

	def assign_note(self, note_number, port_number):
		self.note_assignments[note_number] |= (2 ** port_number)

	def clear_note_assignment(self, note_number, port_number):
		self.note_assignments[note_number] ^= (2 ** port_number)

	def assign_all_notes(self, port_number):
		mask = 2 ** port_number
		for note_number in range(128):
			self.note_assignments[note_number] |= mask

	def clear_port_assignments(self, port_number):
		mask = 2 ** port_number
		for note_number in range(128):
			self.note_assignments[note_number] ^= mask

	def __process_callback(self, frames):
		self.__real_process_callback(frames)

	def __normal_process_callback(self, frames):
		self.__clear_output_buffers()
		if self.bypassed:
			for port in self.output_ports.values():
				for msg in self.all_off_messages:
					port.write_midi_event(0, msg)
			self.__real_process_callback = self.__bypassed_process_callback
		else:
			for offset, data in self.input_port.incoming_midi_events():
				if len(data) == 3:
					status, val_1, val_2 = struct.unpack('3B', data)
					if status & NOTE_ON_MASK == NOTE_ON_STAT:
						bits = self.note_assignments[val_1]
						for port_number in range(16):
							if (bits >> port_number) & 1:
								self.output_ports[port_number].write_midi_event(offset, data)
					else:
						self.__write_all_ports(offset, data)
				else:
					self.__write_all_ports(offset, data)

	def __bypassed_process_callback(self, frames):
		self.__clear_output_buffers()
		if not self.bypassed:
			self.__real_process_callback = self.__normal_process_callback

	def __clear_output_buffers(self):
		for port in self.output_ports.values():
			port.clear_buffer()

	def __write_all_ports(self, offset, data):
		for port in self.output_ports.values():
			port.write_midi_event(offset, data)

	def __shutdown_callback(self, status, reason):
		self.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

	def close(self):
		self.deactivate()
		super().close()


#  end jack_midi_split/__init__.py
