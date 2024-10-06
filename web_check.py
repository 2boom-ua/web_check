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


def getHostName():
	"""Get system hostname"""
	hostname = ""
	hostname_path = '/proc/sys/kernel/hostname'
	if os.path.exists(hostname_path):
		with open(hostname_path, "r") as file:
			hostname = file.read().strip()
	return hostname
	
def GetModificationTime(file_path):
	"""Get file modification time"""
	modification_time = os.path.getmtime(file_path)
	return datetime.datetime.fromtimestamp(modification_time)


def SendMessage(message: str):
	"""Send notifications to various messaging services (Telegram, Discord, Slack, Gotify, Ntfy, Pushbullet, Pushover, Matrix, Mattermost, Rocket.chat)."""
	def SendRequest(url, json_data=None, data=None, headers=None):
		"""Send an HTTP POST request and handle exceptions."""
		try:
			response = requests.post(url, json=json_data, data=data, headers=headers)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending message: {e}")
	
	if telegram_on:
		for token, chat_id in zip(telegram_tokens, telegram_chat_ids):
			url = f"https://api.telegram.org/bot{token}/sendMessage"
			json_data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
			SendRequest(url, json_data)
	if discord_on:
		for url in discord_webhook_urls:
			json_data = {"content": message.replace("*", "**")}
			SendRequest(url, json_data)
	if mattermost_on:
		for url in mattermost_webhook_urls:
			json_data = {'text': message.replace("*", "**")}
			SendRequest(url, json_data)
	if slack_on:
		for url in slack_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if matrix_on:
		for token, server_url, room_id in zip(matrix_tokens, matrix_server_urls, matrix_room_ids):
			url = f"{server_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message?access_token={token}"
			tmp_message = "<br>".join(string.replace('*', '<b>', 1).replace('*', '</b>', 1) for string in message.split("\n"))
			json_data = {"msgtype": "m.text", "body": tmp_message, "format": "org.matrix.custom.html", "formatted_body": tmp_message}
			SendRequest(url, json_data)
	if rocket_on:
		for token, server_url, user_id, channel in zip(rocket_tokens, rocket_server_urls,rocket_user_ids, rocket_channel_ids):
			url = f"{server_url}/api/v1/chat.postMessage"
			headers_data = {"X-Auth-Token": token, "X-User-Id": user_id, "Content-Type": "application/json"}
			json_data = {"channel": channel, "text": message}
			SendRequest(url, json_data, None, headers_data)
	
	header, message = message.replace("*", "").split("\n", 1)
	message = message.strip()
	
	if gotify_on:
		for token, server_url in zip(gotify_tokens, gotify_server_urls):
			url = f"{server_url}/message?token={token}"
			json_data = {'title': header, 'message': message, 'priority': 0}
			SendRequest(url, json_data)
	if ntfy_on:
		for url in ntfy_webhook_urls:
			encoded_message = message.encode(encoding = 'utf-8')
			headers_data = {"title": header}
			SendRequest(url, None, encoded_message, headers_data)
	if pushbullet_on:
		for token in pushbullet_tokens:
			url = "https://api.pushbullet.com/v2/pushes"
			json_data = {'type': 'note', 'title': header, 'body': message}
			headers_data = {'Access-Token': token, 'Content-Type': 'application/json'}
			SendRequest(url, json_data, None, headers_data)
	if pushover_on:
		for token, user_key in zip(pushover_tokens, pushover_user_keys):
			url = "https://api.pushover.net/1/messages.json"
			json_data = {"token": token, "user": user_key, "message": message, "title": header}
			SendRequest(url, json_data)

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
			parsed_json = json.loads(file.read())
		url_list_date = GetModificationTime(f"{current_path}/url_list.json")
		web_list = parsed_json["list"]
		with open(f"{current_path}/config.json", "r") as file:
			parsed_json = json.loads(file.read())
		default_dot_style = parsed_json["DEFAULT_DOT_STYLE"]
		if not default_dot_style:
			dots = square_dot
		green_dot, red_dot = dots["green"], dots["red"]
		messaging_platforms = ["TELEGRAM", "DISCORD", "GOTIFY", "NTFY", "PUSHBULLET", "PUSHOVER", "SLACK", "MATRIX", "MATTERMOST", "ROCKET"]
		telegram_on, discord_on, gotify_on, ntfy_on, pushbullet_on, pushover_on, slack_on, matrix_on, mattermost_on, rocket_on = (parsed_json[key]["ON"] for key in messaging_platforms)
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
			"ROCKET": ["TOKENS", "SERVER_URLS", "USER_IDS", "CHANNEL_IDS"]
		}	
		for service, keys in services.items():
			if parsed_json[service]["ON"]:
				globals().update({f"{service.lower()}_{key.lower()}": parsed_json[service][key] for key in keys})
				monitoring_mg += f"- messaging: {service.capitalize()},\n"
		min_repeat = int(parsed_json["MIN_REPEAT"])
		SendMessage(f"{header}hosts monitor:\n{monitoring_mg}- polling period: {min_repeat} minute(s).")
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
				parsed_json = json.loads(file.read())
			web_list = parsed_json["list"]
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
			message = f"monitoring host(s):\n|ALL| - {total_hosts}, |OK| - {count_hosts}, |BAD| - {bad_hosts}\n{message}"
		if old_status != new_status:
			old_status = new_status
			SendMessage(f"{header}{message}")
	else:
		print("url_list.json or/and config.json not nound")

while True:
	run_pending()
	time.sleep(1)
