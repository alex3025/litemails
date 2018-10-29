import os
import time
import tkinter
import sqlite3
import json
import smtplib
import locale
import requests
import threading
import html2text as h2t
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

version = "v1.4" # DO NOT CHANGE

print('Starting Lite Mails {} \n'.format(version))

file = None
toopen = None

# Inizializzazione database
db = sqlite3.connect("config.db")
c = db.cursor()

# Inizializzazione finestra
window = Tk()

window.title('Lite Mails {}'.format(version)) # Titolo finestra
window.geometry('460x425') # Dimensione finestra
window.resizable(False, False) # Blocco ridimensionamento

window.style = Style()
window.style.theme_use('vista')

langsel = IntVar()

datesel = IntVar()
timesel = IntVar()

destination = StringVar()
subject = StringVar()

email = StringVar()
password = StringVar()

try:
	c.execute("SELECT email, password FROM account")
	credentials = list(c.fetchall())

	c.execute("SELECT language FROM settings")
	language = list(c.fetchall())

	c.execute("SELECT date_format, time_format FROM settings")
	datetime_format = list(c.fetchall())

	print('Database loaded succeful!')

except sqlite3.OperationalError:
	# Creazione delle nuove tables
	print('A table or the database are missing: creating new one...')
	try:
		c.execute("CREATE TABLE account(email TEXT, password TEXT, id INTEGER)")
		db.commit()
	except sqlite3.OperationalError:
		print('Table account already exist, skipping...')
	try:
		c.execute("CREATE TABLE settings(language TEXT, date_format INTEGER, time_format INTEGER, id INTEGER)")
		db.commit()
	except sqlite3.OperationalError:
		print('Table settings already exist, skipping...')
	c.execute("INSERT INTO settings(language, date_format, time_format, id) VALUES(?,?,?,?)", (str(locale.getdefaultlocale()), 1, 1, 0))
	db.commit()
	c.execute("INSERT INTO account(email, password, id) VALUES(?,?,?)", (None, None, 0))
	db.commit()

	if not os.path.isfile('version.txt'):
		print('Created version file.')
		with open('version.txt', 'w') as f:
			f.write(version)
			f.close()

c.execute("SELECT email, password FROM account")
credentials = list(c.fetchall())

c.execute("SELECT language FROM settings")
language = list(c.fetchall())

if 'en' in language[0][0]:
	with open("languages/en-EN.json", "r") as read_file:
		string = json.load(read_file)
		langsel.set(1)
elif 'it' in language[0][0]:
	with open("languages/it-IT.json", "r") as read_file:
		string = json.load(read_file)
		langsel.set(2)
else:
	with open("languages/en-EN.json", "r") as read_file:
		string = json.load(read_file)
		langsel.set(1)

c.execute("SELECT date_format, time_format FROM settings")
datetime_format = list(c.fetchall())

datesel.set(datetime_format[0][0])
timesel.set(datetime_format[0][1])

class message_handler: # Gestione messaggi

	def auth_error_type2():
		messagebox.showerror(string['error'], string['auth-error-type2'])

	def auth_error_type1():
		messagebox.showerror(string['error'], string['auth-error-type1'])

	def mail_sent():
		messagebox.showinfo(string['info'], string['mail-sent'])

	def compile_error():
		messagebox.showerror(string['error'], string['send-error'])

	def apply_language():
		messagebox.showinfo(string['info'], string['apply-language'])

	def no_conn():
		messagebox.showerror(string['error'], string['no-connection'])

def save_email(): # Salvataggio email
	if not os.path.isdir("emails"):
		os.makedirs("emails")

	tosave = filedialog.asksaveasfile(defaultextension="*.litemail", initialdir="emails", title=string['save-email'], filetypes=[('E-Mail', "*.litemail")])

	if tosave is None:
		return

	template = ("""{0}
{1}
{2}
-""").format(destination.get(), subject.get(), msg_input.get('1.0', 'end-1c'))

	tosave.write(str(template))
	tosave.close()

	print('Email saved!')

def open_email(): # Apertura emails
	global toopen
	toopen = filedialog.askopenfilename(initialdir="emails", title=string['open-email'], filetypes=[("E-Mail", "*.litemail")])
	if toopen == '':
		return
	with open(toopen, 'r') as openedfile:
		def clear():
			dest_input.delete(0, 'end')
			sub_input.delete(0, 'end')
			msg_input.delete('1.0', 'end')
			dest_input.insert(0, openedfile.readline().strip())
			sub_input.insert(0, openedfile.readline(62).strip())
			lines = openedfile.readlines()
			msg_input.insert('1.0', (''.join(lines[0:-1])).strip())
		if msg_input.get('1.0', 'end-1c') or destination.get() or subject.get():
			quitquestion = messagebox.askyesnocancel(string['open-email'], string['quit-message'])
			if quitquestion is True:
				save_email()
				clear()
			elif quitquestion is False:
				clear()
			elif quitquestion is None:
				pass
		elif msg_input.get('1.0', 'end-1c') and destination.get() and subject.get() in open(toopen, 'r').read():
			clear()
		else:
			clear()

def close_program(): # Funzione per chiudere il programma
	if toopen:
		if msg_input.get('1.0', 'end-1c') and destination.get() and subject.get() in open(toopen, 'r').read():
			window.destroy()
			os._exit(0)
		else:
			quitquestion = messagebox.askyesnocancel(string['quit'], string['quit-message'])
			if quitquestion is True:
				save_email()
			elif quitquestion is False:
				window.destroy()
				os._exit(0)
			elif quitquestion is None:
				pass
	elif msg_input.get('1.0', 'end-1c') or destination.get() or subject.get():
		quitquestion = messagebox.askyesnocancel(string['quit'], string['quit-message'])
		if quitquestion is True:
			save_email()
		elif quitquestion is False:
			window.destroy()
			os._exit(0)
		elif quitquestion is None:
			pass
	else:
		window.destroy()
		os._exit(0)

def account(): # Impostazioni account

	c.execute("SELECT email, password FROM account")
	credentials = list(c.fetchall())

	accountwin = Toplevel(window) # Creazione nuova finestra

	accountwin.title(string['account-settings']) # Titolo finestra
	accountwin.geometry('450x155') # Dimensione finestra
	accountwin.resizable(False, False) # Blocco ridimensionamento

	accountwin.iconbitmap('litemails.ico')

	# Elementi finestra

	user_label = Label(accountwin, text=string['email'], font=('Segoe UI', 13)).grid(row=0, pady=15, padx=5, sticky='w')
	user_input = Entry(accountwin, textvariable=email, font=('Segoe UI', 10), width=45)
	user_input.grid(row=0, column=1, pady=15, padx=5, sticky='w')

	psw_label = Label(accountwin, text=string['password'], font=('Segoe UI', 13)).grid(row=1, pady=15, padx=5, sticky='w')
	psw_input = Entry(accountwin, textvariable=password, font=('Segoe UI', 10), width=45, show='*')
	psw_input.grid(row=1, column=1, pady=15, padx=5, sticky='w')

	try:
		user_input.delete(0, 'end')
		psw_input.delete(0, 'end')
		user_input.insert(0, credentials[0][0])
		psw_input.insert(0, credentials[0][1])
	except tkinter.TclError:
		pass

	def close_and_save():

		print('Saving account data...')
		c.execute("UPDATE account SET email = ? WHERE id = ? ", (email.get(), 0))
		db.commit()
		c.execute("UPDATE account SET password = ? WHERE id = ? ", (password.get(), 0))
		db.commit()

		accountwin.destroy()

	ok_button = Button(accountwin, text=string['done'], width=10, command=lambda: close_and_save())
	ok_button.grid(row=2, column=1, padx=25, sticky='se')

def language(lang): # Gestione lingua

	global settings
	c.execute("SELECT language FROM settings")
	language = list(c.fetchall())

	c.execute("UPDATE settings SET language = ? WHERE id = ? ", (lang, 0))
	db.commit()

	user_choice = messagebox.askokcancel(string['info'], string['apply-language'])
	if user_choice:
		window.destroy()
		os._exit(0)

def check_for_updates(fromwhat=None): # Gestione aggiornamenti
	
	try:
		global r
		r = requests.get('http://alex3025.github.io/litemails.html')

		version_to_install = h2t.html2text(r.text).strip()
	except:
		version_to_install = None
		pass

	class RunUpdaterScript(threading.Thread):
		def __init__(self):
			Thread.__init__(self)
			self.start()
			window.destroy()
			self._stop_event = threading.Event()
		def stop(self):
			self._stop_event.set()
		def run(self):
			os.chdir('..')
			os.system('python Updater.py')

	def start_updating():
		db.commit()
		db.close()
		thread = RunUpdaterScript()
		thread.stop()
		os._exit(0)

	if version_to_install:
		if version < version_to_install:
			uf = messagebox.askyesno(string['info'], string['update-found'])
			if uf:
				if toopen:
					if msg_input.get('1.0', 'end-1c') and destination.get() and subject.get() in open(toopen, 'r').read():
						start_updating()
					else:
						quitquestion = messagebox.askyesnocancel(string['quit'], string['quit-message'])
						if quitquestion is True:
							save_email()
						elif quitquestion is False:
							start_updating()
						elif quitquestion is None:
							pass
				elif msg_input.get('1.0', 'end-1c') or destination.get() or subject.get():
					quitquestion = messagebox.askyesnocancel(string['quit'], string['quit-message'])
					if quitquestion is True:
						save_email()
					elif quitquestion is False:
						start_updating()
					elif quitquestion is None:
						pass
				else:
					start_updating()
		elif fromwhat == 'menu':
			messagebox.showinfo(string['info'], string['no-update'])
	elif fromwhat == 'menu':
		message_handler.no_conn()
	else:
		print('No updates found!')

def add_attachment(): # Funzione per l'aggiunta dell'allegato

	global file
	file = filedialog.askopenfilename(title=string['add-attachment'])

	if file:
		send_button.configure(text=string['send-with-attachment'])
		remove_attch_button.configure(state='active')
	else:
		send_button.configure(text=string['send'])
		remove_attch_button.configure(state='disabled')

def remove_attch(): # Rimozione allegato

	global file
	if file:
		send_button.configure(text=string['send'])
		remove_attch_button.configure(state='disabled')
		file = None

def add_date_time(date_or_time, format_=None): # Aggiunge la data corrente alla mail

	global datetime_format
	c.execute("SELECT date_format, time_format FROM settings")
	datetime_format = list(c.fetchall())

	if format_:
		if format_ == string['date-format-type1']:
			c.execute("UPDATE settings SET date_format = ? WHERE id = ? ", (1, 0))
			db.commit()
		elif format_ == string['date-format-type2']:
			c.execute("UPDATE settings SET date_format = ? WHERE id = ? ", (2, 0))
			db.commit()
		elif format_ == string['time-format-type1']:
			c.execute("UPDATE settings SET time_format = ? WHERE id = ? ", (1, 0))
			db.commit()
		elif format_ == string['time-format-type2']:
			c.execute("UPDATE settings SET time_format = ? WHERE id = ? ", (2, 0))
			db.commit()
	else:
		c.execute("SELECT date_format, time_format FROM settings")
		datetime_format = list(c.fetchall())

		if date_or_time:
			if date_or_time == 'date':
				if datetime_format[0][0] == 1:
					msg_input.insert('insert', time.strftime("%d/%m/%Y"))
				elif datetime_format[0][0] == 2:
					msg_input.insert('insert', time.strftime("%d-%m-%Y"))
			if date_or_time == 'time':
				if datetime_format[0][1] == 1:
					msg_input.insert('insert', time.strftime("%H:%M:%S"))
				elif datetime_format[0][1] == 2:
					msg_input.insert('insert', time.strftime("%H:%M"))

	c.execute("SELECT date_format, time_format FROM settings")
	datetime_format = list(c.fetchall())

def send_email(): # Funzione per inviare la mail

	c.execute("SELECT email, password FROM account")
	credentials = list(c.fetchall())
	
	if r:
		try:
			msg = MIMEMultipart()

			msg['From'] = str(credentials[0][0])
			msg['To'] = str(destination.get())
			msg['Subject'] = str(subject.get())

			msg.attach(MIMEText(msg_input.get('1.0', 'end-1c'), 'plain'))

			if file:

				attachment = open(file, "rb")

				part = MIMEBase('application', 'octet-stream')
				part.set_payload((attachment).read())
				encoders.encode_base64(part)
				part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(file))

				msg.attach(part)

			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.login(str(credentials[0][0]), str(credentials[0][1]))
			text = msg.as_string()
			server.sendmail(str(credentials[0][0]), str(destination.get()), text)
			server.quit()
			print('Mail sent.')
			message_handler.mail_sent()
		except smtplib.SMTPAuthenticationError:

			if email.get() or password.get() == None:
				message_handler.auth_error_type2()
			else:
				message_handler.auth_error_type1()

		except smtplib.SMTPRecipientsRefused:
			message_handler.compile_error()
	else:
		message_handler.no_conn()

# Oggetti
main_frame = Frame(window)
main_frame.grid(row=0, column=0, pady=15, sticky='wn')

dest_label = Label(main_frame, text=string['to'], font=('Segoe UI', 13)).grid(row=0, padx=5, sticky='w')
dest_input = Entry(main_frame, textvariable=destination, font=('Segoe UI', 10), width=45)
dest_input.grid(row=0, column=1, padx=5, sticky='w')

sub_label = Label(main_frame, text=string['subject'], font=('Segoe UI', 13)).grid(row=1, pady=5, padx=5, sticky='w')
sub_input = Entry(main_frame, textvariable=subject, font=('Segoe UI', 10), width=45)
sub_input.grid(row=1, column=1, pady=5, padx=5, sticky='w')

msg_label = Label(main_frame, text=string['message'], font=('Segoe UI', 13)).grid(row=2, pady=15, padx=5, sticky='wn')
msg_input = Text(main_frame, font=('Segoe UI', 10), width=45, height=15)
msg_input.grid(row=2, column=1, pady=20, padx=5, sticky='w')
scroll = Scrollbar(main_frame, command=msg_input.yview, orient='vertical')
scroll.config(command=msg_input.yview)
msg_input.configure(yscrollcommand=scroll.set)
scroll.grid(row=2, column=2, ipady=105, sticky='e')

send_button = Button(main_frame, text=string['send'], width=20, command=lambda: send_email())
send_button.grid(row=3, column=1, padx=25, sticky='se')

remove_attch_button = Button(main_frame, text=string['remove-attachment'], state='disabled', width=20, command=lambda: remove_attch())
remove_attch_button.grid(row=3, column=1, padx=25, sticky='sw')

# Barre menu
menu_bar = Menu(window)

# Menu mail
menu_mail = Menu(menu_bar, tearoff=0)

menu_bar.add_cascade(label=string['mail'], menu=menu_mail)

menu_mail.add_command(label=string['save-email'], command=lambda: save_email())
menu_mail.add_command(label=string['open-email'], command=lambda: open_email())

# Menu formato datetime

menu_datetime_format = Menu(menu_bar, tearoff=0)

menu_datetime_format.add_radiobutton(label=string['date'].title() + ': ' + string['date-format-type1'], command=lambda: add_date_time(None, string['date-format-type1']), variable=datesel, value=1)
menu_datetime_format.add_radiobutton(label=string['date'].title() + ': ' + string['date-format-type2'], command=lambda: add_date_time(None, string['date-format-type2']), variable=datesel, value=2)
menu_datetime_format.add_radiobutton(label=string['time'].title() + ': ' + string['time-format-type1'], command=lambda: add_date_time(None, string['time-format-type1']), variable=timesel, value=1)
menu_datetime_format.add_radiobutton(label=string['time'].title() + ': ' + string['time-format-type2'], command=lambda: add_date_time(None, string['time-format-type2']), variable=timesel, value=2)

# Sottomenu datetime
menu_datetime_settings = Menu(menu_bar, tearoff=0)

menu_datetime_settings.add_command(label=string['insert'] + ' ' + string['date'], command=lambda: add_date_time('date'))
menu_datetime_settings.add_command(label=string['insert'] + ' ' + string['time'], command=lambda: add_date_time('time'))
menu_datetime_settings.add_cascade(label=string['date-time-settings'], menu=menu_datetime_format)

# Menu inserisci
menu_insert = Menu(menu_bar, tearoff=0)

menu_insert.add_cascade(label=string['date-time'], menu=menu_datetime_settings)
menu_insert.add_command(label=string['add-attachment'], command=lambda: add_attachment())

# Menu strumenti
menu_utility = Menu(menu_bar, tearoff=0)

menu_bar.add_cascade(label=string['utility'], menu=menu_utility)

menu_utility.add_cascade(label=string['insert'], menu=menu_insert)

# Menu lingue
menu_languages = Menu(menu_bar, tearoff=0)

menu_languages.add_radiobutton(label='English', command=lambda: language('en-EN'), variable=langsel, value=1)
menu_languages.add_radiobutton(label='Italiano', command=lambda: language('it-IT'), variable=langsel, value=2)

# Menu opzioni
menu_options = Menu(menu_bar, tearoff=0)

menu_bar.add_cascade(label=string['options'], menu=menu_options)

menu_options.add_command(label=string['account-settings'], command=lambda: account())
menu_options.add_cascade(label=string['language'], menu=menu_languages)
menu_options.add_command(label=string['check-updates'], command=lambda: check_for_updates('menu'))
menu_options.add_separator()
menu_options.add_command(label=string['close'] + ' Lite Mails', command=lambda: close_program())

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

window.config(menu=menu_bar) # Aggiunge la barra dei menu

window.iconbitmap('litemails.ico') # Icona programma

window.protocol("WM_DELETE_WINDOW", close_program) # Attiva funzione in caso di chiusura

check_for_updates() # Controlla gli aggiornamenti

window.mainloop() # Genera l'interfaccia grafica