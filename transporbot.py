# encoding :utf-8
from bs4 import BeautifulSoup
from datetime import date, datetime
import cPickle as pickle
import telebot, os.path
from peticiones import get_stations, get_html
from tidylib import tidy_document
from difflib import *
from telegram_token import token


def get_schedule(html):
	soup = BeautifulSoup(html, 'html.parser')
	body = soup.body
	table = body.table

	if table == None:
		if any(["No Existen Servicios" in i.text for i in soup.body.div.find_all("h4")]):
			return ("", [], [])
		else:
			return (None, None, None)
	else:
		#Comprueba si es trasbordo
		if any(["Transbordo en" in i.text for i in table.findAll('td', { "class" : "cabe" })]):
			transbordo = table.tbody.contents[5].td.string.strip()
			horarios = [i.string.strip() for i in table.findAll('td', { "class" : "color2" })[::3] if i.string != None]
			horarios_t = [i.string.strip() for i in table.findAll('td', { "class" : "color3" })[::2] if i.string != None]
		else:
			transbordo = None
			horarios = [i.string.strip() for i in table.findAll('td', { "class" : "color1" })[::2] if i.string != None]
			horarios_t = []

	return (transbordo, horarios, horarios_t)

def new_empty_file():
	fichero = open('horarios', 'w+')
	pickle.dump({}, fichero)
	fichero.close()

def save_schedule(dic, org_dst, fecha, transbordo, horarios, horarios_t):
	dic[org_dst] = (fecha, transbordo, horarios, horarios_t)
	fichero = open('horarios', 'w')
	pickle.dump(dic, fichero)
	fichero.close()


def return_schedule(entries):
	today = date.today().strftime("%Y%m%d")

	fichero = open("horarios", "r")
	dic = pickle.load(fichero)
	fichero.close()
	orig = entries[0]
	dest = entries[1]
	org_dst = orig + "_" + dest
	print(org_dst)
	horas = []

	if not org_dst in dic or dic[org_dst][0] != today:
		html = get_html(orig, dest, today)
		transbordo, horas, horas_t = get_schedule(html)
		if horas == None:
			return "Parece que la web de Renfe no funciona ahora mismo.\nIntentalo mas tarde"
		save_schedule(dic, org_dst, today, transbordo, horas, horas_t)
	else:
		transbordo, horas, horas_t =  dic[org_dst][1:]

	#Si al comando se le ha incluido una hora se devuelven las horas a partir de esta
	#Si no se devuelven las horas a partir de la actual
	if len(entries) == 3:
		filtro_hora = entries[2]
	else:
		filtro_hora = datetime.now().time()
	horas = [i for i in horas if datetime.strptime(i, "%H.%M").time() > filtro_hora]
	horas_t = horas_t[(len(horas_t) - len(horas)):]

	if not horas:
		return "Vaya! Parece que no hay trenes disponibles"
	else:
		if transbordo == None:
			return "\n".join(horas)
		else:
			return "Transbordo en: " + transbordo + "\n" + "\n".join([horas[i] + "-" + horas_t[i] for i in range(len(horas))])

def get_closest(entries, word):
	    closest = [i for i in entries if word in i]
	    res = ""

	    if len(closest) == 1:
	        res = closest[0]

	    elif len(closest) > 1:
	        close_matches = get_close_matches(word, entries, cutoff=0.8)
	        closest = set(closest).intersection(close_matches)
	        if len(closest) == 1:
	            res = closest[0]

	    else:
	        close_matches = get_close_matches(word, entries, cutoff=0.8)
	        if len(close_matches) == 1:
	            res = close_matches[0]

	    return res

def main():

	bot = telebot.TeleBot(token, skip_pending=True)

	if not os.path.isfile("horarios"):
		new_empty_file()

	stations = get_stations()

	if stations == None:
		return "No ha sido posible establecer la conexion con la Pagina de Renfe"

	@bot.message_handler(commands=['start'])
	def send_welcome(message):
		bot.reply_to(message, "Bot para conocer los horarios de Renfe Cercanias.\nPara conocer los comandos, escribe /help.")

	@bot.message_handler(commands=['help'])
	def send_help(message):
	        bot.reply_to(message, "Comandos:\n /estaciones Estaciones de la zona\n/[provincia] [origen] [destino] Horarios desde la hora actual\n/[provincia] [origen] [destino] [hora] Horarios desde la hora especificada\n El formato de los horarios es HH.MM")

	@bot.message_handler(commands=['estaciones'])
	def send_stations(message):
	        bot.reply_to(message, "\n".join(sorted(stations.keys())))

	@bot.message_handler(commands=['sev', 'Sev'])
	def send_schedule(message):
		texto = message.text.lower()
		listacomando = texto.split(' ')

		if len(listacomando) not in [3, 4]:
			bot.reply_to(message, "No has introducido bien el comando")
		else:
			commands = listacomando[1:3]
			if not commands[0] in stations: #complementar con nueva funcion
				commands[0] = get_closest(stations, commands[0])

			if not commands[1] in stations: #complementar con nueva funcion
				commands[1] = get_closest(stations, commands[1])

			if commands[0] == "":
				bot.reply_to(message, "No se ha encontrado la estacion de origen")
			elif commands[1] == "":
				bot.reply_to(message, "No se ha encontrado la estacion de destino")
			elif commands[0] == commands[1]:
				bot.reply_to(message, "No creo que quieras saber eso")
			else:
				entries = [stations[i] for i in commands]
				try:
					if len(listacomando) == 4:
						time = datetime.strptime(listacomando[3], "%H.%M").time()
						entries.append(time)
				except ValueError:
					bot.reply_to(message, "Formato de fecha incorrecto")
				else:
					res = return_schedule(entries)
					bot.reply_to(message, "Horarios de\n"+ commands[0]+"-"+commands[1]+"\n"+res)

	while(True):
		try:
			bot.polling(none_stop=True)
			break
		except AttributeError:
			print("AttributeError exception")
		except Exception as e:
			print(e)

if __name__ == "__main__":
	main()
