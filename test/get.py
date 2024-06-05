# -*- coding: cp1251 -*-
from ftplib import FTP
import sys

PATH = '\\'.join(sys.argv[0].split('\\')[:-1])

ftp = FTP()
HOST = '192.168.137.106'
PORT = 21

ftp.connect(HOST, PORT)

print(ftp.login(user='pi', passwd='9'))

ftp.cwd('picam')

for i in ['Sat May 14 04_22_12 2022.avi']:
  with open(i, 'wb') as f:
      ftp.retrbinary('RETR ' + i, f.write)

