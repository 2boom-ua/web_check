#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Copyright (c) 2024 2boom.

import json
import socket, errno
import os
import ssl
import time
import datetime
import requests
from schedule import every, repeat, run_pending
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def getHostName() -> str:
	"""Get system hostname"""
	hostname = ""
	hostname_path = '/proc/sys/kernel/hostname'
	if os.path.exists(hostname_path):
		with open(hostname_path, "r") as file:
			hostname = file.read().strip()
	return hostname
	
def GetModificationTime(file_path):
	"""Returns the modification time of a file as a datetime object."""
	modification_time = os.path.getmtime(file_path)
	return datetime.datetime.fromtimestamp(modification_time)


def SendMessage(message: str):
	"""Send notifications to various messaging services (Telegram, Discord, Gotify, Ntfy, Pushbullet, Pushover, Matrix, Zulip, Flock, Slack, RocketChat, Pumble, Mattermost, CUSTOM)."""
	"""CUSTOM - single_asterisks - Zulip, Flock, Slack, RocketChat, Flock, double_asterisks - Pumble, Mattermost """
	def SendRequest(url, json_data=None, data=None, headers=None):
		"""Send an HTTP POST request and handle exceptions."""
		try:
			response = requests.post(url, json=json_data, data=data, headers=headers)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending message: {e}")
			
	def toHTMLformat(message: str) -> str:
		"""Format the message with bold text and HTML line breaks."""
		formatted_message = ""
		for i, string in enumerate(message.split('*')):
			formatted_message += f"<b>{string}</b>" if i % 2 else string
		formatted_message = formatted_message.replace("\n", "<br>")
		return formatted_message

	if telegram_on:
		for token, chat_id in zip(telegram_tokens, telegram_chat_ids):
			url = f"https://api.telegram.org/bot{token}/sendMessage"
			json_data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
			SendRequest(url, json_data)
	if slack_on:
		for url in slack_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if rocket_on:
		for url in rocket_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if zulip_on:
		for url in zulip_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if flock_on:
		for url in flock_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if matrix_on:
		for token, server_url, room_id in zip(matrix_tokens, matrix_server_urls, matrix_room_ids):
			url = f"{server_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message?access_token={token}"
			formatted_message = toHTMLformat(message)
			json_data = {"msgtype": "m.text", "body": formatted_message, "format": "org.matrix.custom.html", "formatted_body": formatted_message}
			SendRequest(url, json_data)
	if discord_on:
		for url in discord_webhook_urls:
			formatted_message = message.replace("*", "**")
			json_data = {"content": formatted_message}
			SendRequest(url, json_data)
	if mattermost_on:
		for url in mattermost_webhook_urls:
			formatted_message = message.replace("*", "**")
			json_data = {'text': formatted_message}
			SendRequest(url, json_data)
	if pumble_on:
		for url in pumble_webhook_urls:
			formatted_message = message.replace("*", "**")
			json_data = {"text": formatted_message}
			SendRequest(url, json_data)
	if apprise_on:
		for url, mformat in zip(apprise_webhook_urls, apprise_formats):
			"""apprise_formats - markdown/html/text."""
			headers_data = {"Content-Type": "application/json"}
			formatters = {
				"markdown": lambda msg: msg.replace("*", "**"),
				"html": toHTMLformat,
				"text": lambda msg: msg.replace("*", ""),
			}
			formatted_message = formatters.get(mformat, lambda msg: msg)(message)
			json_data = {"body": formatted_message, "type": "info", "format": mformat}
			SendRequest(url, json_data, None, headers_data)
	if custom_on:
		for url, content_name, mformat in zip(custom_webhook_urls, custom_content_names, custom_formats):
			"""custom_name - text/body/content/message/..., custom_format - markdown/html/text/asterisk(non standard markdown - default)."""
			formatters = {
				"markdown": lambda msg: msg.replace("*", "**"),
				"html": toHTMLformat,
				"text": lambda msg: msg.replace("*", ""),
			}
			formatted_message = formatters.get(mformat, lambda msg: msg)(message)
			json_data[content_name] = formatted_message
			SendRequest(url, json_data)
	if ntfy_on:
		for url in ntfy_webhook_urls:
			headers_data = {"Markdown": "yes"}
			formatted_message = message.replace("*", "**").encode(encoding = "utf-8")
			SendRequest(url, None, formatted_message, headers_data)
	
	header, message = message.split("\n", 1)

	if gotify_on:
		for token, server_url in zip(gotify_tokens, gotify_server_urls):
			url = f"{server_url}/message?token={token}"
			formatted_message = message.replace("*", "**").replace("\n", "\n\n")
			formatted_header = header.replace("*", "")
			json_data = {'title': formatted_header, "message": formatted_message, "priority": 0, "extras": {"client::display": {"contentType": "text/markdown"}}}
			SendRequest(url, json_data)
	if pushover_on:
		for token, user_key in zip(pushover_tokens, pushover_user_keys):
			url = "https://api.pushover.net/1/messages.json"
			formatted_message = toHTMLformat(message)
			formatted_header = header.replace("*", "")
			json_data = {"token": token, "user": user_key, "message": formatted_message, "title": formatted_header, "html": "1"}
			SendRequest(url, json_data)
	if pushbullet_on:
		for token in pushbullet_tokens:
			url = "https://api.pushbullet.com/v2/pushes"
			formatted_header = header.replace("*", "")
			formatted_message = message.replace("*", "")
			json_data = {'type': 'note', 'title': formatted_header, 'body': formatted_message}
			headers_data = {'Access-Token': token, 'Content-Type': 'application/json'}
			SendRequest(url, json_data, None, headers_data)


if __name__ == "__main__":
	"""Load configuration and initialize monitoring"""
	current_path =  os.path.dirname(os.path.realpath(__file__))
	hostname = getHostName()
	header = f"*{hostname}* (hosts)\n"
	old_status = ""
	web_list = []
	ssl._create_default_https_context = ssl._create_unverified_context
	config_files = False
	monitoring_mg = ""
	dots = {"green": "\U0001F7E2", "red": "\U0001F534"}
	square_dot = {"green": "\U0001F7E9", "red": "\U0001F7E5"}
	if os.path.exists(f"{current_path}/config.json") and os.path.exists(f"{current_path}/url_list.json"):
		config_files = True
		with open(f"{current_path}/url_list.json", "r") as file:
			config_json = json.loads(file.read())
		url_list_date = GetModificationTime(f"{current_path}/url_list.json")
		web_list = config_json["list"]
		with open(f"{current_path}/config.json", "r") as file:
			config_json = json.loads(file.read())
		default_dot_style = config_json["DEFAULT_DOT_STYLE"]
		if not default_dot_style:
			dots = square_dot
		green_dot, red_dot = dots["green"], dots["red"]
		messaging_platforms = ["TELEGRAM", "DISCORD", "GOTIFY", "NTFY", "PUSHBULLET", "PUSHOVER", "SLACK", "MATRIX", "MATTERMOST", "PUMBLE", "ROCKET", "ZULIP", "FLOCK", "APPRISE", "CUSTOM"]
		telegram_on, discord_on, gotify_on, ntfy_on, pushbullet_on, pushover_on, slack_on, matrix_on, mattermost_on, pumble_on, rocket_on, zulip_on, flock_on, apprise_on, custom_on = (config_json[key]["ENABLED"] for key in messaging_platforms)
		services = {
			"TELEGRAM": ["TOKENS", "CHAT_IDS"],
			"DISCORD": ["WEBHOOK_URLS"],
			"SLACK": ["WEBHOOK_URLS"],
			"GOTIFY": ["TOKENS", "SERVER_URLS"],
			"NTFY": ["WEBHOOK_URLS"],
			"PUSHBULLET": ["TOKENS"],
			"PUSHOVER": ["TOKENS", "USER_KEYS"],
			"MATRIX": ["TOKENS", "SERVER_URLS", "ROOM_IDS"],
			"MATTERMOST": ["WEBHOOK_URLS"],
			"PUMBLE": ["WEBHOOK_URLS"],
			"ROCKET": ["WEBHOOK_URLS"],
			"ZULIP": ["WEBHOOK_URLS"],
			"FLOCK": ["WEBHOOK_URLS"],
			"APPRISE": ["WEBHOOK_URLS", "FORMATS"],
			"CUSTOM": ["WEBHOOK_URLS", "CONTENT_NAMES", "FORMATS"]
		}
		for service, keys in services.items():
			if config_json[service]["ENABLED"]:
				globals().update({f"{service.lower()}_{key.lower()}": config_json[service][key] for key in keys})
				monitoring_mg += f"- messaging: {service.capitalize()},\n"
		min_repeat = max(int(config_json.get("MIN_REPEAT", 1)), 1)
		monitoring_mg += (
			f"- default dot style: {default_dot_style}.\n"
			f"- polling period: {min_repeat} minute(s)."
		)
		SendMessage(f"{header}hosts monitor:\n{monitoring_mg}")
	else:
		print("url_list.json or/and config.json not nound")


@repeat(every(min_repeat).minutes)
def WebCheck():
	"""Periodically check webhosts"""
	current_status = []
	count_hosts = 0
	message = new_status = ""
	global old_status
	global web_list
	global url_list_date
	if config_files:
		current_url_list_date = GetModificationTime(f"{current_path}/url_list.json")
		if url_list_date != current_url_list_date:
			with open(f"{current_path}/url_list.json", "r") as file:
				config_json = json.loads(file.read())
			web_list = config_json["list"]
			url_list_date = current_url_list_date
		total_hosts = len(web_list)
		if not old_status or total_hosts != len(old_status): old_status = "0" * total_hosts
		current_status = list(old_status)
		for i, weblist in enumerate(web_list):
			req = Request(weblist[0], headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'})
			try:
				response = urlopen(req)#timeout
			except HTTPError as e:
				current_status[i] = "1"
				message += f"{red_dot} *{weblist[1]}:* {e.code}\n"
			except URLError as e:
				current_status[i] = "1"
				message += f"{red_dot} *{weblist[1]}:* {e.reason}\n"
			except Exception as e:
				current_status[i] = "1"
				message += f"{red_dot} *{weblist[1]}:* {e}\n"
			else:
				current_status[i] = "0"
				count_hosts += 1
		new_status = "".join(current_status)
		bad_hosts = total_hosts - count_hosts
		if count_hosts == total_hosts:
			message = f"{green_dot} monitoring host(s):\n|ALL| - {total_hosts}, |OK| - {count_hosts}, |BAD| - {bad_hosts}"
		else:
			message = f"monitoring host(s):\n{message}|ALL| - {total_hosts}, |OK| - {count_hosts}, |BAD| - {bad_hosts}"
		if old_status != new_status:
			old_status = new_status
			SendMessage(f"{header}{message}")
	else:
		print("url_list.json or/and config.json not nound")

while True:
	run_pending()
	time.sleep(1)
