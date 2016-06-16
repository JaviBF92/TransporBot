from bs4 import BeautifulSoup
import cPickle as pickle
from subprocess import call
from datetime import date

html = "renfe.html"
org_dst = "virgendelrocio_doshermanas"

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




hoy = date.today().strftime("%d-%m-%Y")
while True:
    try:
        dic = pickle.load(open("horarios", "rb"))
    except IOError:
        new_empty_file()
    else:
        if not org_dst in dic or dic[org_dst][0] != hoy:
            #open(html, 'r') -> lo que devuelva selenium
            #org_dst -> el texto de telegram
            fechas = get_schedule(open(html, "rb"))
            save_schedule(dic, org_dst, hoy, fechas)
            print "no exihte",fechas
            break
        else:
            print "exihte", dic[org_dst][1]
            break


"""buscar y guardar el horario para tenerlo al dia
"""
"""
if __name__ == "__main__":
    obtener_horario_BS("renfe.html")
"""
