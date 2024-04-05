# web_check
web check informer for Telegram, Discord, Gotify as linux service

*** [Gotify - a simple server for sending and receiving messages (in real time per WebSocket). ](https://github.com/gotify/server)

```
pip install -r requirements.txt
```

**config.json**
```
{
	"TELEGRAM": {
		"ON": true,
		"TOKEN": "your_token",
		"CHAT_ID": "your_chat_id"
	},
	"DISCORD": {
		"ON": true,
		"WEB": "web_your_channel"
	},
	"GOTIFY": {
		"ON": true,
		"TOKEN": "your_token",
		"WEB": "server_url"
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
ExecStart=/usr/bin/python3 /opt/web_check/web_check.py

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
