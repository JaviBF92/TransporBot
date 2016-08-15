# encoding :utf-8
from bs4 import BeautifulSoup
from datetime import date, datetime
import cPickle as pickle
from subprocess import call
import telebot, os.path
from peticiones import get_stations, get_html
from tidylib import tidy_document
from token import token


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
	call(["touch", "horarios"])
	fichero = open('horarios', 'w')
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
	print org_dst
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
	        bot.reply_to(message, "Comandos:\n /estaciones Manera correcta de escribir las estaciones\n/[provincia] [origen] [destino] Horarios desde la hora actual\n/[ciudad] [origen] [destino] [hora] Horarios desde la hora especificada\n El formato de los horarios es HH.MM")

	@bot.message_handler(commands=['estaciones'])
	def send_stations(message):
	        bot.reply_to(message, "\n".join(sorted(stations.keys())))

	@bot.message_handler(commands=['sevilla'])
	def send_schedule(message):
		texto = message.text.lower()
		listacomando = texto.split(' ')
		if len(listacomando) in range(3) or len(listacomando) > 4:
			bot.reply_to(message, "No has introducido bien el comando")
		else:
			if not listacomando[1] in stations:
				bot.reply_to(message, "La estacion de origen no existe")
			elif not listacomando[2] in stations:
				bot.reply_to(message, "La estacion de destino no existe")
			elif listacomando[1] == listacomando[2]:
				bot.reply_to(message, "No creo que quieras saber eso")
			else:
				try:
					entries = [stations[i] for i in listacomando[1:3]]
					if len(listacomando) == 4:
						time = datetime.strptime(listacomando[3], "%H.%M").time()
						entries.append(time)
				except ValueError:
					bot.reply_to(message, "El formato para la hora que has introducido no es el correcto")
				else:
					res = return_schedule(entries)
					bot.reply_to(message, res)

	bot.polling(none_stop=True)

if __name__ == "__main__":
	main()
