```
sudo nano /etc/systemd/system/my-service.service
```

```
[Unit]
Description=My custom startup script
Before=motd-news.service

[Service]
User=alexandr
Type=oneshot
ExecStart=/home/alexandr/reboot_project/start.sh start
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target

```

```
systemctl enable --now my-service
systemctl start my-service
systemctl restart my-service
systemctl stop my-service
systemctl status my-service
```
