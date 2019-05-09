#!/usr/bin/python3

''' 
ATMOCOM UDP listener captures any data on UDP broadcast 
and will try to parse and store it to SQLite databases.
Logic is virtually identical to acpwu.php companion script 
with communication over UDP protocol instead of HTTP.

License GNU-GPL V3, see repo for details.

(c)2019 Astrogenic Systems
'''

import argparse
import os
from urllib.parse import parse_qsl
from datetime import datetime, timedelta
import sqlite3
import socket

#Default settings are globals, can be modified when starting via commandline
PASSKEY = 'mypasskey'
DATAFOLDER = 'wxdb'
USE_METRIC = True

#Parse weather data and store it in SQLite database
class WXParser:
	def __init__(self):
		global wxdata

		#Initialize dictionary with all supported parameters to avoid potential key errors in SQL exec later
		wxdata = { 'stationID':'unknownID', 'baro':0, 'absbaro':0, 'temp':0, 'dewpoint':0, 'intemp':0, 'wctemp':0, 'rhum':0, 'inrhum':0, 'wdir':0, 'wgustdir':0, 'wspeed':0,
			'wgustspeed':0, 'precip':0, 'precip_day':0, 'precip_week':0, 'precip_month':0, 'precip_year':0, 'UV':0, 'solar':0, 'soiltemp':0, 'soilmoisture':0, 'leafwetness':0, 
			'weather':0, 'clouds':0, 'visibility':0, 'firmware_rev':'0x000000' }

	def store_data(self, qdic):
		#Check for legit access. If passkey check is not important then comment out entire 'if' clause
		if 'passkey' not in qdic or PASSKEY not in qdic['passkey']:
			print ('*** Access error ***')
			return

		uc = UnitConverter()
		if 'updateweatherstation.php' in qdic['data']: #Parse Weather Underground protocol
			print ('-  WU data format detected')

			try:
				wxdata.update({ 'stationID': qdic['data'].split('=')[1] })
			except KeyError:
				wxdata.update({ 'stationID': 'unknownID' })

			#Get air pressure
			if 'baromin' in qdic: wxdata.update({ 'baro': uc.inHg_hPa(qdic['baromin']) })
			if 'absbaromin' in qdic: wxdata.update({ 'absbaro': uc.inHg_hPa(qdic['absbaromin']) })
			
			#Get/convert temperatures
			if 'tempf' in qdic: wxdata.update({ 'temp': uc.f_c(qdic['tempf']) })
			if 'dewptf' in qdic: wxdata.update({ 'dewpoint': uc.f_c(qdic['dewptf']) })
			if 'indoortempf' in qdic: wxdata.update({ 'intemp': uc.f_c(qdic['indoortempf']) })
			if 'windchillf' in qdic: wxdata.update({ 'wctemp': uc.f_c(qdic['windchillf']) })

			#Get/convert humidity
			if 'humidity' in qdic: wxdata.update({ 'rhum': float(qdic['humidity']) })
			if 'indoorhumidity' in qdic: wxdata.update({ 'inrhum': float(qdic['indoorhumidity']) })

			#Get/convert wind and windspeed -- set wind gust dir to prevailing wind dir in case the first is not reported by PWS
			if 'winddir' in qdic: 
				wxdata.update({ 'wdir': float(qdic['winddir']) })
				wxdata.update({ 'wgustdir': float(qdic['winddir']) }) 
			if 'windgustdir' in qdic: wxdata.update({ 'wgustdir': float(qdic['windgustdir']) })
			if 'windspeedmph' in qdic: wxdata.update({ 'wspeed': uc.mph_kt(qdic['windspeedmph']) })
			if 'windgustmph' in qdic: wxdata.update({ 'wgustspeed': uc.mph_kt(qdic['windgustmph']) })

			#Get/convert precipitation
			if 'rainin' in qdic: wxdata.update({ 'precip': uc.in_mm(qdic['rainin']) })
			if 'weeklyrainin' in qdic: wxdata.update({ 'precip_week': uc.in_mm(qdic['weeklyrainin']) })
			if 'dailyrainin' in qdic: wxdata.update({ 'precip_day': uc.in_mm(qdic['dailyrainin']) })
			if 'monthlyrainin' in qdic: wxdata.update({ 'precip_month': uc.in_mm(qdic['monthlyrainin']) })
			if 'yearlyrainin' in qdic: wxdata.update({ 'precip_year': uc.in_mm(qdic['yearlyrainin']) })

			#Get UV and solar radiation
			if 'UV' in qdic: wxdata.update({ 'UV': float(qdic['UV']) })
			if 'solarradiation' in qdic: wxdata.update({ 'solar': float(qdic['solarradiation']) })

			#Other data
			if 'soiltempf' in qdic: wxdata.update({ 'soiltemp': uc.f_c(qdic['soiltempf']) })
			if 'soilmoisture' in qdic: wxdata.update({ 'soilmoisture': float(qdic['soilmoisture']) })
			if 'leafwetness' in qdic: wxdata.update({ 'leafwetness': float(qdic['leafwetness']) })
			if 'weather' in qdic: wxdata.update({ 'weather': float(qdic['weather']) })
			if 'clouds' in qdic: wxdata.update({ 'clouds': float(qdic['clouds']) })
			if 'visibility' in qdic: wxdata.update({ 'visibility': float(qdic['visibility']) })

			#ATMOCOM firmware revision
			if 'rev' in qdic: wxdata.update({ 'firmware_rev': qdic['rev'] })

			db = DBStorage()
			db.db_store(wxdata)

			#print(wxdata)
		elif 'automaticreading' in qdic['data']: #TODO Parse MetOffice protocol 
			print ('-  MetOffice WOW data format detected')
			#TODO
			pass

		return

class DBStorage:
	def db_store(self, wxdict):
		now = datetime.now()
		dbname = os.path.join(DATAFOLDER, 'wx' + now.strftime('%Y%m') + '.db')

		date_str = now.strftime('%Y-%m-%d')
		time_str = now.strftime('%H:%M:%S')
		zOffset = round((now-datetime.utcnow()).total_seconds()/60.0, 1)

		#Check if DB already exists and if not create it		
		self.db_create(dbname)

		try:
			dbconn = sqlite3.connect(dbname)
			c = dbconn.cursor()
			c.execute("INSERT INTO wxdata VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
				( wxdict['stationID'], date_str, time_str, zOffset, wxdict['temp'], wxdict['dewpoint'], wxdict['rhum'], wxdict['baro'],
					wxdict['wdir'], wxdict['wspeed'], wxdict['wgustdir'], wxdict['wgustspeed'],
					wxdict['precip'], wxdict['precip_day'], wxdict['UV'], wxdict['solar'],
					wxdict['intemp'], wxdict['inrhum'], wxdict['soiltemp'], wxdict['soilmoisture'],
					wxdict['leafwetness'], wxdict['weather'], wxdict['clouds'], wxdict['visibility'],
					wxdict['precip_week'], wxdict['precip_month'], wxdict['precip_year'], wxdict['absbaro'], wxdict['firmware_rev'] ) )

			dbconn.commit()
		except sqlite3.Error as e:
			print(e)
		finally:
			dbconn.close()

	#Creates DB and table if not exists
	#If DB file exists table is implicit so no action
	def db_create(self, dbname):
		if os.path.isfile(dbname): 
			#Database file exists, table is implicit. All OK so just return
			return
		else: #We have to create new DB file and table. Also make directory if this is the first run
			db_fullpath = os.path.join(os.getcwd(), DATAFOLDER)
			print ('Database not found, creating directory ' + db_fullpath)
			if not os.path.exists(db_fullpath): os.makedirs(db_fullpath)
		
		try:
			conn = sqlite3.connect(dbname)
			print('SQLite3 version ' + sqlite3.version)

			if conn is not None:
				c = conn.cursor()
				c.execute( "CREATE TABLE IF NOT EXISTS wxdata (ID integer primary key, STATIONID text, DATE text, TIME text, UTC real, \
				TEMP real, DEWPT real, RHUM real, BARO real, WINDDIR real, WINDVEL real, WGUSTDIR real, WGUSTVEL real, PRECIP real, PRECIPDAY real, \
				UVIDX real, SOLAR real, INTEMP real, INRHUM real, SOILTEMP real, SOILMOIST real, LEAFWET real, WEATHER text, CLOUDS text, VISNM real, \
				PRECIPWEEK real, PRECIPMON real, PRECIPYEAR real, ABSBARO real, FIRMWARE_REV text);")
				
				#return conn
			else:
				print('Failed to create database or table')

		except sqlite3.Error as e:
			print(e)
		finally:
			conn.close()
		
		return


class UnitConverter:
	def f_c(self, v):
		temp=float(v)
		if not USE_METRIC: return temp
		return round((temp - 32) * 0.555556, 2)

	def in_mm(self, v):
		p_in = float(v)
		if not USE_METRIC: return p_in
		return round(p_in * 25.4, 2)

	def mph_kt(self, v):
		ws_mph = float(v)
		if not USE_METRIC: return ws_mph
		return round(ws_mph * 0.868976, 2)
	
	def inHg_hPa(self, v):
		inHg = float(v)
		if not USE_METRIC: return inHg
		return round(inHg * 33.8638816, 2)


def main():
	global PASSKEY, DATAFOLDER, USE_METRIC

	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--passkey", type=str, help="Set accesssecurity passkey. Default: "+PASSKEY)
	parser.add_argument("-d", "--directory", type=str, help="Database directory. Default: "+DATAFOLDER)
	parser.add_argument("-i", "--imperial", action="store_true", help="Store data in Imperial units. Default: Metric")


	args = parser.parse_args()
	
	if args.passkey:
		PASSKEY = args.passkey
	
	if args.directory:
		DATAFOLDER = args.directory

	if args.imperial:
		USE_METRIC = False


	print("* ATMOCOM UDP Weather Data Logger v0.4b *")
	print("-Passkey            : " + PASSKEY)
	print("-Database directory : " + DATAFOLDER)
	print("-Using metric system: " + str(USE_METRIC))
	print("")

	try:
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind(('', 12000))
		pWU = WXParser()
		while True:
			message, address = server_socket.recvfrom(1024)
			print(address, message)
			
			#Get command line arguments
			s=dict(parse_qsl(message.decode("utf-8"))) 

			#send off data for parsing and storing
			pWU.store_data(s)

	except KeyboardInterrupt:
		print ("Shutting down UDP server")
	except Exception as e:
		print (e)

if __name__ == "__main__": main()
