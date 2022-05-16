#coding:utf-8
"""
    Copyright (C) 2010 Igor zalomskij <igor.kaist@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import os
import socket
import _thread
import time
import ping
import queue
import urllib.request, urllib.parse, urllib.error
import sys



class SDCard:
	def __init__(self,home_dir=''):
		self.home_dir=home_dir
		self.ip=socket.gethostbyname(socket.gethostname())
		self.card_ip=None
		self.all_files=[]
		
		self.download_list=queue.Queue()
		self.in_queue=[]
		

		
		
	def find_card(self,callback=None):
		_thread.start_new_thread(self.find_card_thread,(callback,))

		
	def find_card_thread(self,callback=None):
		while not self.card_ip:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.settimeout(5)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			try:s.bind((self.ip, 58255))
			except socket.error:
				s.close()
				time.sleep(1)
				continue



			s.sendto(b'', ('<broadcast>', 55777))
			try:
				resp=s.recv(400)
				s.close()
				try:
					self.card_ip=resp.split('ip=')[1].split('\n')[0]
				except IndexError:
					if callback:callback(None)
		
				if callback:callback(self.card_ip)
			
			except socket.timeout:
				callback(self.card_ip)
			finally:
				time.sleep(2)
			
			
	def start_listen(self,callback=None,download_callback=None,download_complete=None):
		self.listen_flag=True
		_thread.start_new_thread(self.listener_thread,(callback,))
		_thread.start_new_thread(self.ping_card,())
		_thread.start_new_thread(self.download_thread,(download_callback,download_complete))
		

		
	def ping_card(self):
		while self.listen_flag:
			try:
				resp=ping.do_one(self.card_ip)
			except socket.error:
				pass
			time.sleep(20)
				
			
	def listener_thread(self,callback):
		sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((self.card_ip, 5566))
		while self.listen_flag:
			message=sock.recv(1024)
			new_files=message.split('\00')
			for x in new_files:
				if x:
					self.all_files.append(x[1:])
			self.download_list.put(self.all_files[-1])
			self.in_queue.append(self.all_files[-1])
			if callback:callback(self.all_files[-1])

			
	def download_thread(self,download_callback,download_complete):
		while self.listen_flag:
			if not self.download_list.empty():
				fl=self.download_list.get(block=0)
				self.download_now=fl
				urllib.request.urlretrieve(
				    f'http://{self.card_ip}/cgi-bin/wifi_download?fn={fl}',
				    self.home_dir + fl.split('/')[-1],
				    download_callback or None,
				)
				if download_complete:download_complete(self.download_now)
			time.sleep(0.1)


def monitor(ip):
	if not ip:return
	print(('Find card on ip:',ip))
	sd.start_listen(download_complete=print_complete)
	

def print_complete(fname):
	print(f"New image: {HOME_DIR + fname.split('/')[-1]}")
	
		
if __name__=='__main__':
	from optparse import OptionParser
	parser = OptionParser()
	parser.add_option("-d", "--dir", dest="dir",default=None,help="directory for storing images")
	parser.add_option(
	    "-i",
	    "--ip",
	    dest="ip",
	    default=None,
	    help=
	    f"ip address of the computer (default {socket.gethostbyname(socket.gethostname())})",
	)
	(options, args) = parser.parse_args()

	HOME_DIR=os.path.expanduser('~')
	if not os.path.exists(f'{HOME_DIR}/ShootAndView'):
		os.mkdir(f'{HOME_DIR}/ShootAndView')
	HOME_DIR = options.dir or f'{HOME_DIR}/ShootAndView/'
	sd=SDCard(home_dir=HOME_DIR)	


	if options.ip:sd.ip=options.ip
	print('Finding sd card...')
	sd.find_card(callback=monitor)


	while 1:
		time.sleep(1)
		
			



