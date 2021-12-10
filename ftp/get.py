# -*- coding: cp1251 -*-
from ftplib import FTP
import sys

PATH = '\\'.join(sys.argv[0].split('\\')[:-1])

ftp = FTP()
HOST = '192.168.0.1'
PORT = 21

ftp.connect(HOST, PORT)

print(ftp.login(user='login', passwd='password'))

ftp.cwd('path/to/the/file')

for i in ['file1', 'file2']:
  with open(i, 'wb') as f:
      ftp.retrbinary('RETR ' + i, f.write)

