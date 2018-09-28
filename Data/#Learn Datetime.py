#Learn Datetime.py
#Importing datetime
from datetime import datetime

#prints the time now
now = datetime.now()
#year,month,day
year = now.year
month = now.month
day = now.day
#Converter
#months
if month == 1:
	month = "January"
if month == 2:
	month = "Febuary"
if month == 3:
	month = "March"
if month == 4:
	month = "April"
if month == 5:
	month = "May"
if month == 6:
	month = "June"
if month == 7:
	month = "July"
if month == 8:
	month = "August"
if month == 9:
	month = "September"
if month == 10:
	month = "October"
if month == 11:
	month = "November"
if month == 12:
	month = "December"

#Date Printer
print(f"{month} {day}, {year}")

#Time
hour = now.hour
minute = now.minute
second = now.second
#Converter for hour
if hour > 12:
	hour = hour - 12
	ap = "pm"
else:
	ap = "am"
time = '%02d:%02d:%02d ' % (hour,minute,second) + ap

print(time)


