import locale
import datetime

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

myDate = datetime.date.today()
myMonth = myDate.strftime('%B')

print(myMonth)