from datetime import datetime, date

t = datetime.now()
print(t)
dt1 = datetime.strptime(str(t), '%Y-%m-%d %H:%M:%S.%f')
print(type(dt1))
