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
	"""Send notifications to various messaging services (Telegram, Discord, Gotify, Ntfy, Pushbullet, Pushover, Matrix, Zulip, Flock, Slack, RocketChat, Pumble, Mattermost, custom)."""
	def SendRequest(url, json_data=None, data=None, headers=None):
		"""Send an HTTP POST request and handle exceptions."""
		try:
			response = requests.post(url, json=json_data, data=data, headers=headers)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending message: {e}")
			
	def toHTMLFormat(message: str) -> str:
		"""Format the message with bold text and HTML line breaks."""
		formatted_message = ""
		for i, string in enumerate(message.split('*')):
			formatted_message += f"<b>{string}</b>" if i % 2 else string
		formatted_message = formatted_message.replace("\n", "<br>")
		return formatted_message
		
	def toMarkdownFormat(message: str, m_format: str) -> str:
		"""Converts a message into a specified format (either Markdown, HTML, or plain text)"""
		formatters = {
			"markdown": lambda msg: msg.replace("*", "**"),
			"html": toHTMLFormat,
			"text": lambda msg: msg.replace("*", ""),
			}
		return formatters.get(m_format, lambda msg: msg)(message)

	if telegram_on:
		for token, chat_id in zip(telegram_tokens, telegram_chat_ids):
			url = f"https://api.telegram.org/bot{token}/sendMessage"
			json_data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
			SendRequest(url, json_data)
	if asterisk_on:
		"""For platforms using asterisk formatting: Slack, Rocket.chat, Zulip, Flock"""
		for url in asterisk_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if markdown_on:
		"""For platforms using markdown formatting: Mattermost, Pumble"""
		for url in markdown_webhook_urls:
			json_data = {"text": message.replace("*", "**")}
			SendRequest(url, json_data)
	if matrix_on:
		for token, server_url, room_id in zip(matrix_tokens, matrix_server_urls, matrix_room_ids):
			url = f"{server_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message?access_token={token}"
			formatted_message = toHTMLFormat(message)
			json_data = {"msgtype": "m.text", "body": formatted_message, "format": "org.matrix.custom.html", "formatted_body": formatted_message}
			SendRequest(url, json_data)
	if discord_on:
		for url in discord_webhook_urls:
			formatted_message = message.replace("*", "**")
			json_data = {"content": formatted_message}
			SendRequest(url, json_data)
	if apprise_on:
		"""apprise_formats - markdown/html/text."""
		for url, format_message in zip(apprise_webhook_urls, apprise_format_messages):
			formatted_message = toMarkdownFormat(message, format_message)
			json_data = {"body": formatted_message, "type": "info", "format": format_message}
			SendRequest(url, json_data)
	if custom_on:
		message_str_format = ["text", "content", "message", "body", "formatted_body", "data"]
		for url, header, pyload, format_message in zip(custom_webhook_urls, custom_headers, custom_pyloads, custom_format_messages):
			data, ntfy = None, False
			formated_message = toMarkdownFormat(message, format_message)
			header_json = header if header else None
			for key in list(pyload.keys()):
				if key == "title":
					delimiter = "<br>" if format_message == "html" else "\n"
					header, formated_message = formated_message.split(delimiter, 1)
					pyload[key] = header.replace("*", "")
				elif key == "extras":
					formated_message = formated_message.replace("\n", "\n\n")
					pyload["message"] = formated_message
				elif key == "data":
					ntfy = True
				pyload[key] = formated_message if key in message_str_format else pyload[key]
			pyload_json = None if ntfy else pyload
			data = formated_message.encode("utf-8") if ntfy else None
			SendRequest(url, pyload_json, data, header_json)
	if ntfy_on:
		for url in ntfy_webhook_urls:
			headers_data = {"Content-Type": "application/json", "Markdown": "yes"}
			formatted_message = message.replace("*", "**").encode(encoding = "utf-8")
			SendRequest(url, None, formatted_message, headers_data)
	
	header, message = message.split("\n", 1)

	if gotify_on:
		for token, server_url in zip(gotify_tokens, gotify_server_urls):
			url = f"{server_url}/message?token={token}"
			formatted_message = message.replace("*", "**").replace("\n", "\n\n")
			formatted_header = header.replace("*", "")
			json_data = {"title": formatted_header, "message": formatted_message, "priority": 0, "extras": {"client::display": {"contentType": "text/markdown"}}}
			SendRequest(url, json_data)
	if pushover_on:
		for token, user_key in zip(pushover_tokens, pushover_user_keys):
			url = "https://api.pushover.net/1/messages.json"
			formatted_message = toHTMLFormat(message)
			formatted_header = header.replace("*", "")
			json_data = {"token": token, "user": user_key, "title": formatted_header, "message": formatted_message, "html": "1"}
			SendRequest(url, json_data)
	if pushbullet_on:
		for token in pushbullet_tokens:
			url = "https://api.pushbullet.com/v2/pushes"
			formatted_header = header.replace("*", "")
			formatted_message = message.replace("*", "")
			json_data = {"type": "note", "title": formatted_header, "body": formatted_message}
			headers_data = {"Access-Token": token, "Content-Type": "application/json"}
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
	monitoring_message = ""
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
		try:
			default_dot_style = config_json.get("DEFAULT_DOT_STYLE", True)
			min_repeat = max(int(config_json.get("MIN_REPEAT", 1)), 1)
		except (json.JSONDecodeError, ValueError, TypeError, KeyError):
			default_dot_style = True
			min_repeat = 1
		if not default_dot_style:
			dots = square_dot
		green_dot, red_dot = dots["green"], dots["red"]
		no_messaging_keys = ["DEFAULT_DOT_STYLE", "MIN_REPEAT"]
		messaging_platforms = list(set(config_json) - set(no_messaging_keys))
		default_planform = [
			"telegram_on", "discord_on", "gotify_on", "ntfy_on", "pushbullet_on", 
			"pushover_on", "slack_on", "matrix_on", "mattermost_on", "pumble_on", 
			"rocket_on", "zulip_on", "flock_on", "apprise_on"]
		for platform_on in default_planform:
			globals()[platform_on] = False
		asterisk_on = markdown_on = custom_on = False
		globals().update({f"{key.lower()}_on": config_json[key]["ENABLED"] for key in messaging_platforms})
		for platform in messaging_platforms:
			if config_json[platform].get("ENABLED", False):
				for key, value in config_json[platform].items():
					platform_on_key = f"{platform.lower()}_on"
					if platform_on_key in default_planform:
						if platform_on_key in ["rocket_on", "zulip_on", "flock_on", "slack_on"]:
							storage_key = f"asterisk_{key.lower()}"
							asterisk_on = True
						elif platform_on_key in ["mattermost_on", "pumble_on"]:
							storage_key = f"markdown_{key.lower()}"
							markdown_on = True
						else:
							storage_key = f"{platform.lower()}_{key.lower()}"
						if storage_key in globals():
							globals()[storage_key] = (globals()[storage_key] if isinstance(globals()[storage_key], list) else [globals()[storage_key]])
							globals()[storage_key].extend(value if isinstance(value, list) else [value])
						else:
							globals()[storage_key] = value if isinstance(value, list) else [value]
					else:
						custom_key = f"custom_{key.lower()}"
						custom_on = True
						if custom_key in globals():
							globals()[custom_key] = (globals()[custom_key] if isinstance(globals()[custom_key], list) else [globals()[custom_key]])
							globals()[custom_key].extend(value if isinstance(value, list) else [value])
						else:
							globals()[custom_key] = value if isinstance(value, list) else [value]
				monitoring_message += f"- messaging: {platform.lower().capitalize()},\n"
		monitoring_message = "\n".join([*sorted(monitoring_message.splitlines()), ""])
		monitoring_message += (
			f"- default dot style: {default_dot_style},\n"
			f"- polling period: {min_repeat} minute(s)."
		)
		SendMessage(f"{header}hosts monitor:\n{monitoring_message}")
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
				response = urlopen(req)  # timeout
				current_status[i] = "0"
				count_hosts += 1
			except (HTTPError, URLError, Exception) as e:
				current_status[i] = "1"
				reason = e.code if isinstance(e, HTTPError) else e.reason if isinstance(e, URLError) else str(e)
				message += f"{red_dot} *{weblist[1]}:* {reason}\n"
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
