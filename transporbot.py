# encoding :utf-8
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from datetime import date
import cPickle as pickle
from subprocess import call
import telebot
import os.path

estacionesDict = {
	"alcoleadelrio" : 1,
	"arenilla" : 2,
	"bellavista" : 3,
	"benacazon" : 4,
	"brenes" : 5,
	"camas" : 6,
	"cantaelgallo" : 7,
	"cantillana" : 8,
	"cartuja" : 9,
	"cazalla-constantina" : 10,
	"donrodrigo" : 11,
	"doshermanas" : 12,
	"elcanamo" : 13,
	"estadioolimpico" : 14,
	"fabricadepedroso" : 15,
	"guadajoz" : 16,
	"jardinesdehercules" : 17,
	"larinconada" : 18,
	"lascabezasdesanjuan" : 19,
	"lebrija" : 20,
	"loradelrio" : 21,
	"losrosales" : 22,
	"padrepiopalmete" : 23,
	"palaciodecongresos" : 24,
	"pedroso" : 25,
	"salteras" : 26,
	"sanbernardo" : 27,
	"sanjeronimo" : 28,
	"sanlucarlamayor" : 29,
	"santajusta" : 30,
	"tocina" : 31,
	"utrera" : 32,
	"valenciana-santiponce" : 33,
	"villanuevaariscalolivares" : 34,
	"villanuevariominas" : 35,
	"virgendelrocio" : 36
}
estacionesList = sorted(estacionesDict.keys())

def coge_horarios(orig, dest):
	arrowOr = estacionesDict.get(orig)
	arrowDe = estacionesDict.get(dest)
	if arrowOr != None and arrowDe != None:
		return return_schedule(orig, dest)

def selenium_horarios(orig, dest):
	#selenium
	display = Display(visible=0, size=(800,600))
	display.start()

	firefox_capabilities = DesiredCapabilities.FIREFOX
	firefox_capabilities['marionette'] = True
	firefox_capabilities['binary'] = '/usr/bin/firefox'
	driver = webdriver.Firefox(capabilities=firefox_capabilities)
	driver.get("http://horarios.renfe.com/cer/hjcer300.jsp?NUCLEO=30&CP=NO&I=s#")
	elem = driver.find_element_by_name('o')
	elem.click()
	for i in range(orig):
		elem.send_keys(Keys.ARROW_DOWN)
	
	elem = driver.find_element_by_name('d')
	for i in range(dest):
		elem.send_keys(Keys.ARROW_DOWN)
	
	elem = driver.find_element_by_tag_name('a')
	elem.click()
	page =  driver.page_source
	driver.close()

	return page

def get_schedule(html):
	soup = BeautifulSoup(html, 'html.parser')
	horarios = [i.string for i in soup.body.table.findAll('td', { "class" : "color1" })[::2]]
	return horarios

def new_empty_file():
	call(["touch", "horarios"])
	pickle.dump({}, open('horarios', 'wb'))

def save_schedule(dic, org_dst, fecha, horarios):
	dic[org_dst] = (fecha, horarios)
	pickle.dump(dic, open('horarios', 'wb'))

def return_schedule(orig, dest):
	hoy = date.today().strftime("%d-%m-%Y")
	while True:
		try:
			dic = pickle.load(open("horarios", "rb"))
		except IOError:
			new_empty_file()
		else:
			org_dst = orig + "_" + dest
			print org_dst
			if not org_dst in dic or dic[org_dst][0] != hoy:
				print estacionesDict.get(orig), estacionesDict.get(dest)
				html = selenium_horarios(estacionesDict.get(orig), estacionesDict.get(dest))
				print html
				fechas = get_schedule(html)
				save_schedule(dic, org_dst, hoy, fechas)
				return fechas
			else:
				return dic[org_dst][1]

bot = telebot.TeleBot("220215593:AAGp_I8ILGz5SjBu7sucjvTzzB6aalCZEuc")

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Bot para conocer los horarios de Renfe Cercanias.\nPara conocer los comandos, escribe /help.")

@bot.message_handler(commands=['help'])
def send_welcome(message):
        bot.reply_to(message, "Comandos:\n/[provincia] [origen] [destino] Horarios desde la hora actual\n/[ciudad] [origen] [destino] [hora] Horarios desde la hora especificada")

@bot.message_handler(commands=['estaciones'])
def send_welcome(message):
        reply = ""
        for e in estacionesList:
                reply = reply + e + "\n"
        bot.reply_to(message, reply)

@bot.message_handler(commands=['sevilla'])
def send_welcome(message):
        texto = message.text
	listacomando = texto.split(' ')
	if len(listacomando) == 3:
		res = coge_horarios(str(listacomando[1]), str(listacomando[2]))
		bot.reply_to(message, res)
	
	if len(listacomando) == 4:
		origen = str(listacomando[1])
                destino = str(listacomando[2])
		hora = str(listacomando[3])

bot.polling()

