import os
import sqlite3
import shutil
import requests
from threading import Thread
from tkinter import *
from tkinter.ttk import *
import urllib.request
import zipfile
import html2text as h2t

try:
	window = Tk()

	window.title('Lite Mails Updater')
	window.geometry('430x100')
	window.iconbitmap('update.ico')
	window.resizable(False, False)

	window.style = Style()
	window.style.theme_use('vista')

	pb = Progressbar(window)
	pb.grid(column=0, row=0, ipadx=100, pady=15, padx=60, sticky='wn')

	def update():

			r = requests.get('http://alex3025.github.io/litemails.html')

			version_to_install = h2t.html2text(r.text).strip()

			try:
				db = sqlite3.connect("bin/config.db")
				c = db.cursor()
				c.execute("SELECT version, language FROM settings")
				global settings
				settings = list(c.fetchall())

				if 'en' in settings[0][1]:
					string = 'Downloading new version...'
				elif 'it' in settings[0][1]:
					string = 'Download della nuova versione...'
				else:
					string = 'Downloading new version...'
			except FileNotFoundError:
				print('Start first the main application!')
				return
			except:
				return

			lb = Label(window, text=string)
			lb.grid(column=0, row=0, pady=50, sticky='s')

			if settings[0][0] < version_to_install:

				db.close()

				try:

					print('Downloading new version...')

					if not os.path.isdir("update"):
						os.makedirs("update")

					def reporthook(count, data_size, total_data):
						if count == 0:
							pb.configure(maximum=total_data)
						else:
							pb.step(data_size)

						global percent
						percent = int(count * data_size * 100 / total_data)

					source = 'https://github.com/alex3025/litemails/releases/download/{0}/LiteMails.zip'.format(version_to_install)
					urllib.request.urlretrieve(source, 'update/LiteMails.zip', reporthook)

					print('Installing new version...')

					if not os.path.isdir("bin"):
						os.makedirs("bin")

					if not os.path.isdir("backup"):
						os.makedirs("backup")

					if not os.path.isdir("backup/emails"):
						os.makedirs("backup/emails")

					try:
						for file in os.listdir("bin/emails"):
							os.rename("bin/emails/" + file, "backup/emails/" + file)
							shutil.move("bin/emails/" + file, "backup/emails/" + file)

						if os.path.isfile("bin/config.db"):
							os.rename("bin/config.db", "backup/config.db")
							shutil.move("bin/config.db", "backup/config.db")
					except:
						pass

					unzipper = zipfile.ZipFile('update/LiteMails.zip', 'r')

					for the_file in os.listdir('bin'):
						path = os.path.join('bin', the_file)

						if os.path.isfile(path):
							os.unlink(path)

					unzipper.extractall('bin')
					unzipper.close()

					if not os.path.isdir("bin/emails"):
						os.makedirs("bin/emails")

					try:
						for file in os.listdir("backup/emails"):
							os.rename("backup/emails/" + file, "bin/emails/" + file)
							shutil.move("backup/emails/" + file, "bin/emails/" + file)

						if os.path.isfile("backup/config.db"):
							os.rename("backup/config.db", "bin/config.db")
							shutil.move("backup/config.db", "bin/config.db")
					except:
						pass

					for the_file in os.listdir('update'):
						path = os.path.join('update', the_file)

						if os.path.isfile(path):
							os.unlink(path)

					for the_file in os.listdir('backup/emails'):
						path = os.path.join('backup', the_file)

						if os.path.isfile(path):
							os.unlink(path)

					for the_file in os.listdir('backup'):
						path = os.path.join('backup', the_file)

						if os.path.isfile(path):
							os.unlink(path)

					shutil.rmtree('update/')
					shutil.rmtree('backup/')

					print('Installed!')

				except Exception as e:
					print('Error when installing new version!')
					print('\n' + e)
			else:
				print('No updates found!')
				window.destroy()

	Thread(target=update).start()

	window.mainloop()

except:
	os.exit(1)