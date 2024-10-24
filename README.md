## Web Host Monitoring Script
<div align="center">  
    <img src="https://github.com/2boom-ua/web_check/blob/main/web_check.jpg?raw=true" alt="" width="260" height="177">
</div>
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

### Edit config.json:
A **config.json** file in the same directory as the script, and include your API tokens and configuration settings.
```
{
    "TELEGRAM": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "CHAT_IDS": [
            "first chat_id",
            "second chat_id",
            "...."
        ]
    },
    "DISCORD": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "SLACK": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "GOTIFY": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "CHAT_URLS": [
            "first server_url",
            "second server_url",
            "...."
        ]
    },
    "NTFY": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "PUSHBULLET": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
    "PUSHOVER": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "USER_KEYS": [
            "first user_key",
            "second user_key",
            "...."
        ]
    },
    "MATRIX": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "SERVER_URLS": [
            "first server_url",
            "second server_url",
            "...."
        ],
        "ROOM_IDS": [
            "!first room_id",
            "!second room_id",
            "...."
        ]
    },
    "MATTERMOST": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "ROCKET": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
		"USER_IDS": [
            "first user_id",
            "second user_id",
            "...."
        ],
        "SERVER_URLS": [
           "first server_url",
            "second server_url",
            "...."
        ],
		"CHANNEL_IDS": [
            "#first channel",
            "#second channel",
            "...."
        ]
    },
    "FLOCK": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "PUMBLE": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "ZULIP": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "APPRISE": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ],
        "FORMATS": [
            "markdown"
        ]
    },
    "CUSTOM": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
        "CONTENT_NAMES": [
            "text",
            "body",
        "...."
        ],
        "FORMATS": [
            "asterisk",
            "markdown"
        ]
    },
    "DEFAULT_DOT_STYLE": true,
    "MIN_REPEAT": 1
}
```
| Item | Required | Description |
|------------|------------|------------|
| **TELEGRAM** | | |
| ENABLED | true/false | Enable or disable Telegram notifications |
| TOKENS | String | The token of your Telegram bot |
| CHAT_IDS | String | The ID of the Telegram chat where notifications will be sent |
||||
| **DISCORD** | | |
| ENABLED | true/false | Enable or disable Discord notifications |
| WEBHOOK_URLS | url | The URL of your Discord webhook |
||||
| **SLACK** | | |
| ENABLED | true/false | Enable or disable Slack notifications |
| WEBHOOK_URLS | url | The URL of your Slack webhook |
||||
| **GOTIFY** | | |
| ENABLED | true/false | Enable or disable Gotify notifications |
| SERVER_URLS | url | The URL of your Gotify server |
| TOKENS | String | The token for your Gotify application |
||||
| **NTFY** | | |
| ENABLED | true/false | Enable or disable Ntfy notifications |
| WEBHOOK_URLS | url | The URL of your self-hosted Ntfy server (or use https://ntfy.sh) |
||||
| **PUSHBULLET** | | |
| ENABLED | true/false | Enable or disable Pushbullet notifications |
| TOKENS | String | The token for your Pushbullet application |
||||
| **PUSHOVER** | | |
| ENABLED | true/false | Enable or disable Pushover notifications |
| TOKENS | String | The token for your Pushover application |
| USER_KEYS | String | The user key for your Pushover application |
||||
| **MATRIX** | | |
| ENABLED | true/false | Enable or disable Matrix notifications |
| TOKENS | String | The token for your Matrix application |
| SERVER_URLS | url | The URL of your Matrix server  (or use https://matrix.org) |
||||
| **MATTERMOST** | | |
| ENABLED | true/false | Enable or disable Mattermost notifications |
| WEBHOOK_URLS | url | The URL of your Mattermost webhook |
||||
| **ROCKET** | | |
| ENABLED | true/false | Enable or disable Rocket.Chat notifications |
| SERVER_URLS | url | The URL of your Rocket.Chat server |
| TOKENS | String | The token for your Rocket.Chat application |
| CHANNEL_IDS | String | The ID of the Rocket.Chat channel where notifications will be sent |
||||
| **PUMBLE** | | |
| ENABLED | true/false | Enable or disable Pumble notifications |
| WEBHOOK_URLS | url | The URL of your Pumble webhook |
||||
| **ZULIP** | | |
| ENABLED | true/false | Enable or disable Zulip notifications |
| WEBHOOK_URLS | url | The URL of your Zulip webhook |
||||
| **FLOCK** | | |
| ENABLED | true/false | Enable or disable Flock notifications |
| WEBHOOK_URLS | url | The URL of your Flock webhook |
||||
| **APPRISE** | | |
| ENABLED | true/false | Enable or disable Apprise notifications |
| WEBHOOK_URLS | url | The URL of your Apprise webhook |
| FORMATS | markdown,<br>html,<br>text,<br>asterisk | The format(s) to be used for the notification (e.g., markdown/html/text/asterisk) |
||||
| **CUSTOM** | | |
| ENABLED | true/false | Enable or disable Custom notifications |
| WEBHOOK_URLS | url | The URL of your Custom webhook |
| FORMATS | markdown,<br>html,<br>text,<br>asterisk | The format(s) to be used for the notification (e.g., markdown/html/text/asterisk) |
| CONTENT_NAMES | text,<br>body,<br>content,<br>message | json = {"text/body/content/message": out_message} |

- **markdown** - a simple text-based format with lightweight syntax for basic styling (Pumble, Mattermost, Discord, Ntfy, Gotify),
- **html** - a web-based format using tags for advanced text styling,
- **text** - raw text without any styling or formatting.
- **asterisk** - non-standard Markdown (Telegram, Zulip, Flock, Slack, RocketChat).


| Item   | Required   | Description   |
|------------|------------|------------|
| DEFAULT_DOT_STYLE | true/false | Round/Square dots. |
| MIN_REPEAT | 1 | Set the poll period in minutes. Minimum is 1 minute. | 

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
## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) for details.

## Author

- **2boom** - [GitHub](https://github.com/2boom-ua)


