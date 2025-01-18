## Web Host Monitoring Script
<div align="center">  
    <img src="https://github.com/2boom-ua/web_check/blob/main/web_check.jpg?raw=true" alt="" width="260" height="177">
</div>


*The idea for this software was inspired by* [louislam/uptime-kuma](https://github.com/louislam/uptime-kuma)

### Overview

This Python script monitors the availability of specified web hosts. It checks the status of URLs and sends notifications through various messaging services if any host is unreachable or returns an error.

### Features

- **Web Host Monitoring:** Regularly checks if specified URLs are accessible.
- **Real-time notifications with support for multiple accounts** via:
  - Telegram
  - Discord
  - Slack
  - Gotify
  - Ntfy
  - Pushbullet
  - Pushover
  - Rocket.chat
  - Matrix
  - Mattermost
  - Pumble
  - Flock
  - Zulip
  - Apprise
  - Webntfy
  - Custom webhook
- **Dynamic Configuration:** Load URLs and settings from JSON files.
- **Polling Period:** Adjustable interval for checking host availability.
### Requirements

- Python 3.x
- Docker installed and running
- Dependencies: `requests`, `schedule`

### Clone the repository:
```
git clone https://github.com/2boom-ua/web_check.git
cd web_check
```
### Install required Python packages:

```
pip install -r requirements.txt
```
### Edit url_list.json:
```
{
	"list": [
		["http://url", "name_of_url"],
		["http://url", "name_of_url"],
		["http://url", "name_of_url"]
	]
}
```
| Item | Required | Description |
|------------|------------|------------|
| list | url | Name host |

### Edit config.json:
You can use any name and any number of records for each messaging platform configuration, and you can also mix platforms as needed. The number of message platform configurations is unlimited.

[Configuration examples for Telegram, Matrix, Apprise, Pumble, Mattermost, Discord, Ntfy, Gotify, Zulip, Flock, Slack, Rocket.Chat, Pushover, Pushbullet](docs/json_message_config.md)
```
    "CUSTOM_NAME": {
        "ENABLED": false,
        "WEBHOOK_URL": [
            "first url",
            "second url",
            "...."
        ],
        "HEADER": [
            {first JSON structure},
            {second JSON structure},
            {....}
        ],
        "PYLOAD": [
            {first JSON structure},
            {second JSON structure},
            {....}
        ],
        "FORMAT_MESSAGE": [
            "markdown",
            "html",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Custom notifications |
| WEBHOOK_URL | url | The URL of your Custom webhook |
| HEADER | JSON structure | HTTP headers for each webhook request. This varies per service and may include fields like {"Content-Type": "application/json"}. |
| PAYLOAD | JSON structure | The JSON payload structure for each service, which usually includes message content and format. Like as  {"body": "message", "type": "info", "format": "markdown"}|
| FORMAT_MESSAGE | markdown,<br>html,<br>text,<br>simplified | Specifies the message format used by each service, such as markdown, html, or other text formatting.|

- **markdown** - a text-based format with lightweight syntax for basic styling (Pumble, Mattermost, Discord, Ntfy, Gotify),
- **simplified** - simplified standard Markdown (Telegram, Zulip, Flock, Slack, RocketChat).
- **html** - a web-based format using tags for advanced text styling,
- **text** - raw text without any styling or formatting.
```
"HOST_NAME": "MyHostName",
"STARTUP_MESSAGE": true,
"REQUEST_TIMEOUT": 10,
"DEFAULT_DOT_STYLE": true,
"MIN_REPEAT": 1
```

| Item   | Required   | Description   |
|------------|------------|------------|
| "HOST_NAME" | string | Host or config name.|
| STARTUP_MESSAGE | true/false | On/Off startup message. |
| REQUEST_TIMEOUT | 10 | Request timeout in seconds. Default is 10 sec.|
| DEFAULT_DOT_STYLE | true/false | Round/Square dots. |
| MIN_REPEAT | 1 | Set the poll period in minutes. Minimum is 1 minute. | 


## Docker
### docker-cli
```bash
docker build -t web_check:latest .
```
```bash
docker run -d \
  --name web_check \
  -v $(pwd)/config.json:/web_check/config.json \
  -v $(pwd)/url_list.json:/web_check/url_list.json \
  --restart always \
  web_check:latest
```
### docker-compose
```
version: "3.8"
services:
  web_check:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: web_check
    image: web_check:latest
    volumes:
      - ./config.json:/web_check/config.json
      - ./url_list.json:/web_check/url_list.json
    environment:
      - TZ=UTC
    restart: always
    healthcheck:
      test: ["CMD", "pgrep", "-fl", "web_check"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

```bash
docker-compose up -d
```
---

## Running as a Linux Service
You can set this script to run as a Linux service for continuous monitoring.

Create a systemd service file:
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
### License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) for details.

### Author

- **2boom** - [GitHub](https://github.com/2boom-ua)


