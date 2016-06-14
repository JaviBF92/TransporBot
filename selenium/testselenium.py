# encoding :utf-8
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

display = Display(visible=0, size=(800,600))
display.start()

driver = webdriver.Firefox()
driver.get("http://horarios.renfe.com/cer/hjcer300.jsp?NUCLEO=30&CP=NO&I=s#")
elem = driver.find_element_by_name('o')
elem.click()
for i in range(36):
	elem.send_keys(Keys.ARROW_DOWN)

elem = driver.find_element_by_name('d')
for i in range(12):
	elem.send_keys(Keys.ARROW_DOWN)

elem = driver.find_element_by_tag_name('a')
elem.click()
page =  driver.page_source
driver.close()

htmlfile = open('html_virgendelrocio_doshermanas.html', 'w')
htmlfile.write(page.encode('utf-8'))
htmlfile.close()
display.stop()
