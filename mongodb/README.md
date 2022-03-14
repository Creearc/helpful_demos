Установка mongodb
- Ubuntu
```
sudo apt install -y mongodb
```
Для настройки нужно открыть файл /etc/mongodb.conf
```
sudo nano /etc/mongodb.conf
```
И поменять IP адрес, чтобы базу данных видели другие устройства
```
bind_ip = 0.0.0.0
```
Затем, нужно перезагрузить mongodb
```
sudo systemctl restart mongodb
```
Для работы программы нужно установить билиотеку
```
sudo python3 -m pip install pymongo==3.4.0
```

- Windows

Скачать и установить MongoDB
https://www.mongodb.com/try/download/community?tck=docs_server&_ga=2.80979607.1045525337.1647236219-1212526624.1647236219

Скачать и установить mongoshell
https://www.mongodb.com/try/download/community?tck=docs_server&_ga=2.80979607.1045525337.1647236219-1212526624.1647236219

Для настройки нужно открыть файл mongodb.conf и поменять IP адрес, чтобы базу данных видели другие устройства
```
bind_ip = 0.0.0.0
```

Запуск сервера с MongoDB (где drying папка где будет храниться база данных)
```
"C:\Program Files\MongoDB\Server\4.4\bin\mongod.exe" --dbpath="D:\MongoDB\drying"
```

Запустить mongoshell и проверить работоспособность
```
mongosh "mongodb://0.0.0.0:27017"
```

Установить pymongo
```
pip install pymongo==3.4.0
```