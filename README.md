# web_check
web check notifier

**config.json**
```
{
	"TELEGRAM": {
		"TOKEN": "your_token",
		"CHAT_ID": "your_chat_id"
	},
	"MIN_REPEAT": 1
}
```
**make as service**
```
nano /etc/systemd/system/web_check.service
```
```
[Unit]
Description=check active hosts
After=multi-user.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /root/web_check/web_check.py

[Install]
WantedBy=multi-user.target
```
```
systemctl daemon-reload
```
```
systemctl enable web_check.service
```
```
systemctl start web_check.service
```
