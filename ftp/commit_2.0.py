# -*- coding: cp1251 -*-
from ftplib import FTP
import sys
fl = []
if len(sys.argv) > 1:
  for i in range(1, len(sys.argv)):
    print(sys.argv[i])
    fl.append(sys.argv[i])
else:
  fl.append('path/test.py')


for j in range(len(fl)):
  print(fl[j])

  ftp = FTP()
  HOSTS = ['192.168.0.1']
  PORT = 21
  for i in range(len(HOSTS)):
    ftp.connect(HOSTS[i], PORT)
    print(ftp.login(user='login', passwd='password'))

    ftp.cwd('output/path')

    with open(fl[j], 'rb') as f:
        ftp.storbinary('STOR ' + fl[j].split('\\')[-1], f, 1024)

    print('Done!')


