import sqlite3
import time
import datetime
import random

conn = sqlite3.connect("database.db")
c = conn.cursor()

def create_table():
	c.execute("CREATE TABLE IF NOT EXISTS bank(User_ID BIGINT NOT NULL UNIQUE, Balance float)")

def data_entry():
	c.execute("INSERT INTO bank VALUES(462351034384252938,0)")
	conn.commit()

def dynamic_data_entry():
	unix = time.time()
	date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
	keyword = 'Python'
	value = random.randrange(0,10)
	c.execute("INSERT INTO bank (unix, datestamp, keyword, value) VALUES(?, ?, ?, ?)",
			  (unix, date, keyword, value))
	conn.commit()

def read_from_db():
	c.execute("SELECT * FROM bank")
	#data = c.fetchall()
	#print(data)
	for row in c.fetchall():
		print(row)

def del_and_update():
	c.execute('UPDATE bank SET value = 99 WHERE value=8')

	conn.commit()

	c.execute('SELECT * FROM bank')
	[print(row) for row in c.fetchall()]



create_table()
data_entry()
#for i in range(10):
#	dynamic_data_entry()
#	time.sleep(1)
read_from_db()
#del_and_update()
