Установка ftp
```
sudo apt-get install vsftpd
```
Затем, нужно открыть файл /etc/vsftpd.conf
```
sudo nano /etc/vsftpd.conf
```
 и раскомментировать следующие строки:
```
write_enable=YES
```
```
ascii_upload_enable=YES
ascii_download_enable=YES
```
В конце необходимо перезапустить ftp и все готово.
```
sudo service vsftpd restart
```