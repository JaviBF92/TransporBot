# encoding :utf-8
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
from datetime import date, datetime
import cPickle as pickle
from subprocess import call
import telebot, requests
from estaciones import get_stations
from tidylib import tidy_document
from token import token


def get_schedule(html):
	soup = BeautifulSoup(html, 'html.parser')
	table = soup.body.table
	#Comprueba si es trasbordo
	if "Origen" in str(table.tbody.contents[3].contents[3]):
		horarios = [i.string.strip() for i in table.findAll('td', { "class" : "color2" })[::3] if i.string != None]
	else:
		horarios = [i.string.strip() for i in table.findAll('td', { "class" : "color1" })[::2] if i.string != None]
	return horarios

def new_empty_file():
	call(["touch", "horarios"])
	fichero = open('horarios', 'w')
	pickle.dump({}, fichero)
	fichero.close()

def save_schedule(dic, org_dst, fecha, horarios):
	dic[org_dst] = (fecha, horarios)
	fichero = open('horarios', 'w')
	pickle.dump(dic, fichero)
	fichero.close()

def get_html(org, dst):
	r = requests.post('http://horarios.renfe.com/cer/hjcer310.jsp',
	                    data = {'nucleo':'30', 'i':'s', 'cp':'NO',
	                            'o':org, 'd':dst, 'df':'20160617',
	                            'ho':'00', 'hd':'26', 'TXTInfo':''}).text
	document, errors = tidy_document(r)
	return document

def return_schedule(orig, dest):
	hoy = date.today().strftime("%d-%m-%Y")
	while True:
		try:
			fichero = open("horarios", "r")
			dic = pickle.load(fichero)
			fichero.close()
		except IOError:
			print "IOError"
			new_empty_file()
		else:
			org_dst = orig + "_" + dest
			print org_dst
			horas = []
			if not org_dst in dic or dic[org_dst][0] != hoy:
				html = get_html(orig, dest)
				horas = get_schedule(html)
				save_schedule(dic, org_dst, hoy, horas)
			else:
				horas = dic[org_dst][1]
			horas = [i for i in horas if datetime.strptime(i, "%H.%M").time() > datetime.now().time()]
			if not horas:
				return "Vaya, parece que ya no hay mas trenes hoy"
			else:
				return "\n".join(horas)

def main():

	bot = telebot.TeleBot(token, skip_pending=True)

	stations = get_stations()

	@bot.message_handler(commands=['start'])
	def send_welcome(message):
		bot.reply_to(message, "Bot para conocer los horarios de Renfe Cercanias.\nPara conocer los comandos, escribe /help.")

	@bot.message_handler(commands=['help'])
	def send_help(message):
	        bot.reply_to(message, "Comandos:\n /estaciones Manera correcta de escribir las estaciones\n/[provincia] [origen] [destino] Horarios desde la hora actual\n/[ciudad] [origen] [destino] [hora] Horarios desde la hora especificada")

	@bot.message_handler(commands=['estaciones'])
	def send_stations(message):
	        reply = ""
	        for e in sorted(stations.keys()):
	                reply = reply + e + "\n"
	        bot.reply_to(message, reply)

	@bot.message_handler(commands=['sevilla'])
	def send_schedule(message):
		texto = message.text.lower()
		listacomando = texto.split(' ')
		if len(listacomando) in range(3):
			bot.reply_to(message, "No has introducido bien el comando")
		else:
			if not listacomando[1] in stations:
				bot.reply_to(message, "La estacion de origen no existe")
			elif not listacomando[2] in stations:
				bot.reply_to(message, "La estacion de destino no existe")
			elif listacomando[1] == listacomando[2]:
				bot.reply_to(message, "No creo que quieras saber eso")
			else:
				if len(listacomando) == 3:
					res = return_schedule(stations[listacomando[1]], stations[listacomando[2]])
					bot.reply_to(message, res)
				if len(listacomando) == 4:
					origen = str(listacomando[1])
					destino = str(listacomando[2])
					hora = str(listacomando[3])
				if len(listacomando) > 4:
					bot.reply_to(message, "No has introducido bien el comando")

	bot.polling()


if __name__ == "__main__":
	main()
