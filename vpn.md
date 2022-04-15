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
```

Client
```

```
