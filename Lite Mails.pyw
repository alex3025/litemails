import os
import tkinter
import sqlite3
import json
import smtplib
import locale
import requests
import html2text as h2t
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

version = "v1.2" # DO NOT CHANGE

global file
file = None

global toopen
toopen = None

# Inizializzazione database
db = sqlite3.connect("config.db")
c = db.cursor()

# Inizializzazione finestra
window = Tk()

window.title('Lite Mails {}'.format(version)) # Titolo finestra
window.geometry('460x435') # Dimensione finestra
window.resizable(False, False) # Blocco ridimensionamento

window.style = Style()
window.style.theme_use('vista')

langsel = IntVar()

destination = StringVar()
subject = StringVar()

try:
	# Controllo del database
	c.execute("SELECT email, password FROM account")
	c.execute("SELECT language FROM settings")
	print('Database loaded succeful!')
except sqlite3.OperationalError:
	# Creazione di un nuovo table
	# in caso di mancato file
	print('Database not found: creating a new one...')
	c.execute("CREATE TABLE account(email TEXT, password TEXT, id INTEGER)")
	db.commit()
	c.execute("CREATE TABLE settings(language TEXT, version TEXT, id INTEGER)")
	db.commit()
	c.execute("INSERT INTO settings(language, version, id) VALUES(?,?,?)", (str(locale.getdefaultlocale()), version, 0))
	db.commit()
	c.execute("INSERT INTO account(email, password, id) VALUES(?,?,?)", (None, None, 0))
	db.commit()
	c.execute("SELECT email, password FROM account")
	global credentials
	credentials = list(c.fetchall())
	c.execute("SELECT language FROM settings")
	global settings
	settings = list(c.fetchall())

c.execute("SELECT language FROM settings")
settings = list(c.fetchall())

if 'en' in settings[0][0]:
	with open("languages/en-EN.json", "r") as read_file:
		string = json.load(read_file)
		langsel.set(1)
elif 'it' in settings[0][0]:
	with open("languages/it-IT.json", "r") as read_file:
		string = json.load(read_file)
		langsel.set(2)
else:
	with open("languages/en-EN.json", "r") as read_file:
		string = json.load(read_file)
		langsel.set(1)

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
		else:
			quitquestion = messagebox.askyesnocancel(string['quit'], string['quit-message'])
			if quitquestion is True:
				save_email()
			elif quitquestion is False:
				window.destroy()
			elif quitquestion is None:
				pass
	elif msg_input.get('1.0', 'end-1c') or destination.get() or subject.get():
		quitquestion = messagebox.askyesnocancel(string['quit'], string['quit-message'])
		if quitquestion is True:
			save_email()
		elif quitquestion is False:
			window.destroy()
		elif quitquestion is None:
			pass
	else:
		window.destroy()

def check_for_updates(fromwhat=None): # Gestione aggiornamenti
	
	r = requests.get('http://alex3025.github.io/litemails.html')

	version_to_install = h2t.html2text(r.text).strip()

	if version < version_to_install:

		uf = messagebox.askyesno(string['info'], string['update-found'])
		if uf:
			if toopen:
				if msg_input.get('1.0', 'end-1c') and destination.get() and subject.get() in open(toopen, 'r').read():
					os.system('cd "%ProgramFiles%\Lite Mails\"')
					os.system('StartUpdate.exe')
				else:
					quitquestion = messagebox.askyesnocancel(string['quit'], string['quit-message'])
					if quitquestion is True:
						save_email()
					elif quitquestion is False:
						os.system('cd "%ProgramFiles%\Lite Mails\"')
						os.system('StartUpdate.exe')
					elif quitquestion is None:
						pass
			elif msg_input.get('1.0', 'end-1c') or destination.get() or subject.get():
				quitquestion = messagebox.askyesnocancel(string['quit'], string['quit-message'])
				if quitquestion is True:
					save_email()
				elif quitquestion is False:
					os.system('cd "%ProgramFiles%\Lite Mails\"')
					os.system('StartUpdate.exe')
				elif quitquestion is None:
					pass
	elif fromwhat == 'menu':
		messagebox.showinfo(string['info'], string['no-update'])

def account(): # Impostazioni account

	global credentials
	c.execute("SELECT email, password FROM account")
	credentials = list(c.fetchall())

	accountwin = Toplevel(window) # Creazione nuova finestra

	accountwin.title(string['account-settings']) # Titolo finestra
	accountwin.geometry('450x155') # Dimensione finestra
	accountwin.resizable(False, False) # Blocco ridimensionamento

	accountwin.iconbitmap('icons/icon.ico')

	# Elementi finestra

	global email
	global password

	email = StringVar()
	password = StringVar()

	user_label = Label(accountwin, text=string['email'], font=('Segoe UI', 13)).grid(row=0, pady=15, padx=5, sticky='w')
	user_input = Entry(accountwin, textvariable=email, font=('Segoe UI', 10), width=45)
	user_input.grid(row=0, column=1, pady=15, padx=5, sticky='w')

	psw_label = Label(accountwin, text=string['password'], font=('Segoe UI', 13)).grid(row=1, pady=15, padx=5, sticky='w')
	psw_input = Entry(accountwin, textvariable=password, font=('Segoe UI', 10), width=45, show='*')
	psw_input.grid(row=1, column=1, pady=15, padx=5, sticky='w')

	try:
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
		c.execute("SELECT email, password FROM account")
		global credentials
		credentials = list(c.fetchall())

		accountwin.destroy()

	ok_button = Button(accountwin, text=string['done'], width=10, command=lambda: close_and_save())
	ok_button.grid(row=2, column=1, padx=25, sticky='se')

def language(lang): # Gestione lingua

	global settings
	c.execute("SELECT language FROM settings")
	settings = list(c.fetchall())

	c.execute("UPDATE settings SET language = ? WHERE id = ? ", (lang, 0))
	db.commit()

	c.execute("SELECT language FROM settings")
	settings = list(c.fetchall())

	user_choice = messagebox.askokcancel(string['info'], string['apply-language'])
	if user_choice:
		window.destroy()

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

def send_email(): # Funzione per inviare la mail

	c.execute("SELECT email, password FROM account")
	global credentials
	credentials = list(c.fetchall())

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

# Oggetti

dest_label = Label(window, text=string['to'], font=('Segoe UI', 13)).grid(row=0, pady=15, padx=5, sticky='w')
dest_input = Entry(window, textvariable=destination, font=('Segoe UI', 10), width=45)
dest_input.grid(row=0, column=1, pady=15, padx=5, sticky='w')

sub_label = Label(window, text=string['subject'], font=('Segoe UI', 13)).grid(row=1, pady=5, padx=5, sticky='w')
sub_input = Entry(window, textvariable=subject, font=('Segoe UI', 10), width=45)
sub_input.grid(row=1, column=1, pady=5, padx=5, sticky='w')

msg_label = Label(window, text=string['message'], font=('Segoe UI', 13)).grid(row=2, pady=15, padx=5, sticky='wn')
msg_input = Text(window, font=('Segoe UI', 10), width=45, height=15)
msg_input.grid(row=2, column=1, pady=20, padx=5, sticky='w')
scroll = Scrollbar(window, command=msg_input.yview, orient='vertical')
scroll.config(command=msg_input.yview)
msg_input.configure(yscrollcommand=scroll.set)
scroll.grid(row=2, column=2, ipady=105, sticky='e')

send_button = Button(window, text=string['send'], width=20, command=lambda: send_email())
send_button.grid(row=3, column=1, padx=25, sticky='se')

remove_attch_button = Button(window, text=string['remove-attachment'], state='disabled', width=20, command=lambda: remove_attch())
remove_attch_button.grid(row=3, column=1, padx=25, sticky='sw')

# Barre menu

menu_bar = Menu(window)

# Menu mail
menu_mail = Menu(menu_bar, tearoff=0)

menu_bar.add_cascade(label=string['mail'], menu=menu_mail)

menu_mail.add_command(label=string['save-email'], command=lambda: save_email())
menu_mail.add_command(label=string['open-email'], command=lambda: open_email())
menu_mail.add_separator()
menu_mail.add_command(label=string['add-attachment'], command=lambda: add_attachment())

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
menu_options.add_command(label=string['close'], command=lambda: close_program())

window.config(menu=menu_bar) # Aggiunge la barra dei menu

window.iconbitmap('icons/icon.ico') # Icona programma

window.protocol("WM_DELETE_WINDOW", close_program) # Attiva funzione in caso di chiusura

check_for_updates() # Controlla gli aggiornamenti

window.mainloop() # Genera l'interfaccia graficaz