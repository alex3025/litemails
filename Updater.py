import os
import sys
import sqlite3
import shutil
import requests
import threading
import zipfile
import locale
import time
import urllib.request
import html2text as h2t
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

if 'en' in str(locale.getdefaultlocale()):
	string = 'Downloading new version...'
	string2 = 'Installing new version...'
	string3 = 'The update is running, exit now will cause error! Do you want continue?'
	string4 = 'Warning'

elif 'it' in str(locale.getdefaultlocale()):
	string = 'Download della nuova versione...'
	string2 = 'Installazione della nuova versione...'
	string3 = "Aggiornamento in corso, uscire ora causera' errori! Vuoi continuare?"
	string4 = 'Attenzione'

else:
	string = 'Downloading new version...'
	string2 = 'Installing new version...'
	string3 = 'The update is running, exit now will cause error! Do you want continue?'
	string4 = 'Warning'

class Gui(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.start()

	def callback(self):
		self.message = messagebox.askyesno(string4, string3)
		if self.message:
			sys.exit(0)

	def run(self):
		self.download_window = Tk()
		self.download_window.protocol("WM_DELETE_WINDOW", self.callback)

		self.download_window.title('Lite Mails Updater')
		self.download_window.geometry('430x100')
		self.download_window.resizable(False, False)
		self.download_window.iconbitmap('update.ico')

		self.download_window.style = Style()
		self.download_window.style.theme_use('vista')	

		self.pb = Progressbar(self.download_window, mode='determinate')
		self.pb.grid(ipadx=150, padx=15, pady=15, sticky='n')

		self.lb = Label(self.download_window, text=string)
		self.lb.grid(padx=15, sticky='s')

		self.lb2 = Label(self.download_window)
		self.lb2.grid(padx=25, sticky='s')

		self.download_window.mainloop()

def update():

	if os.path.isfile('bin/version.txt'):
		with open('bin/version.txt', 'r') as f:
			current_version = f.read()
			f.close()
	else:
		print('Version file not found! Cannot run updater!')
		sys.exit()

	r = requests.get('http://alex3025.github.io/litemails.html')

	new_version = h2t.html2text(r.text).strip()

	if current_version < new_version:

		gui = Gui()

		try:
			print('Downloading new version...')

			if not os.path.isdir("update"):
				os.makedirs("update")

			def reporthook(count, data_size, total_data):
				global start_time

				if count == 0:
					gui.pb.configure(maximum=total_data)
					start_time = time.time()
					return
				else:
					gui.pb.step(data_size)

				duration = time.time() - start_time
				progress_size = int(count * data_size)
				speed = int(progress_size / (1024 * duration))
				percent = int(count * data_size * 100 / total_data)

				gui.lb2['text'] = "{0}% - {1} MB - {2} KB/s".format(percent, round(progress_size / (1024 * 1024), 1), speed)

			source = 'https://github.com/alex3025/litemails/releases/download/{0}/LiteMails.zip'.format(new_version)
			urllib.request.urlretrieve(source, 'update/LiteMails.zip', reporthook)

			print('Installing new version...')

			gui.lb['text'] = string2
			gui.pb['mode'] = 'indeterminate'
			gui.pb.configure(maximum=100)
			gui.pb.start(30)
			gui.lb2['text'] = ' '

			# Creating init folders

			if not os.path.isdir('bin'):
				os.makedirs('bin')

			if not os.path.isdir('backup'):
				os.makedirs('backup/emails')

			# Backup files

			if os.path.isfile('bin/config.db'):
				shutil.copy('bin/config.db', 'backup')

			if os.path.isdir('bin/emails'):
				for item in os.listdir('bin/emails'):
					shutil.copy('bin/emails/' + item, 'backup/emails')

			# Delete folders

			shutil.rmtree('bin')

			# Install version

			unzipper = zipfile.ZipFile('update/LiteMails.zip', 'r')

			if not os.path.isdir('bin'):
				os.makedirs('bin/emails')

			unzipper.extractall('bin')
			unzipper.close()

			# Move files

			if os.path.isfile('backup/config.db'):
				shutil.copy('backup/config.db', 'bin')

			if os.path.isdir('backup/emails'):
				for item in os.listdir('backup/emails'):
					shutil.copy('backup/emails/' + item, 'bin/emails')

			# Remove dirs

			shutil.rmtree('update')
			shutil.rmtree('backup')

			# Finish

			print('Installed!')

			gui.download_window.destroy()
		except Exception as e:
			print('Error when installing new version!')
			print(e)
	else:
		print('No updates found!')
		gui.download_window.destroy()

update()