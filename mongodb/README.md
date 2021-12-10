Установка mongodb
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