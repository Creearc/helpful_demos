Server
```
wget https://git.io/vpn -O openvpn-install.sh
sudo apt-get install openvpn easy-rsa
sudo cp -R /usr/share/easy-rsa /etc/openvpn/

sudo bash openvpn-install.sh

service openvpn start
service openvpn status

service openvpn restart

sudo cat /root/test.ovpn
>>> copy to client
```

Client
```
sudo apt-get install openvpn easy-rsa
sudo cp -R /usr/share/easy-rsa /etc/openvpn/

sudo nano /etc/openvpn/client/test.conf

>>> insert data from server

sudo systemctl start openvpn-client@test
sudo systemctl status openvpn-client@test
sudo systemctl enable openvpn-client@test
```
