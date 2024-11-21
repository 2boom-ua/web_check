#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Copyright (c) 2024 2boom.

import json
import socket, errno
import os
import sys
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
	"""Internal function to send HTTP POST requests with error handling"""
	def SendRequest(url, json_data=None, data=None, headers=None):
		try:
			response = requests.post(url, json=json_data, data=data, headers=headers)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending message: {e}")
	
	"""Converts the message to HTML format by replacing Markdown-like syntax"""
	def toHTMLFormat(message: str) -> str:
		formatted_message = ""
		for i, string in enumerate(message.split('*')):
			formatted_message += f"<b>{string}</b>" if i % 2 else string
		formatted_message = formatted_message.replace("\n", "<br>")
		return formatted_message

	"""Converts the message to the specified format (HTML, Markdown, or plain text)"""
	def toMarkdownFormat(message: str, m_format: str) -> str:
		if m_format == "html":
			return toHTMLFormat(message)
		elif m_format == "markdown":
			return message.replace("*", "**")
		elif m_format == "text":
			return message.replace("*", "")
		return message

	"""Iterate through multiple platform configurations"""
	for url, header, pyload, format_message in zip(platform_webhook_url, platform_header, platform_pyload, platform_format_message):
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
			pyload[key] = formated_message if key in ["text", "content", "message", "body", "formatted_body", "data"] else pyload[key]
		pyload_json = None if ntfy else pyload
		data = formated_message.encode("utf-8") if ntfy else None
		"""Send the request with the appropriate payload and headers"""
		SendRequest(url, pyload_json, data, header_json)


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
		for platform in messaging_platforms:
			if config_json[platform].get("ENABLED", False):
				for key, value in config_json[platform].items():
					platform_key = f"platform_{key.lower()}"
					if platform_key in globals():
						globals()[platform_key] = (globals()[platform_key] if isinstance(globals()[platform_key], list) else [globals()[platform_key]])
						globals()[platform_key].extend(value if isinstance(value, list) else [value])
					else:
						globals()[platform_key] = value if isinstance(value, list) else [value]
				monitoring_message += f"- messaging: {platform.lower().capitalize()},\n"
		monitoring_message = "\n".join([*sorted(monitoring_message.splitlines()), ""])
		monitoring_message += (
			f"- default dot style: {default_dot_style},\n"
			f"- polling period: {min_repeat} minute(s)."
		)
		if all(value in globals() for value in ["platform_webhook_url", "platform_header", "platform_pyload", "platform_format_message"]):
			SendMessage(f"{header}hosts monitor:\n{monitoring_message}")
		else:
			print("config.json is wrong")
			sys.exit(1)
	else:
		print("url_list.json or/and config.json not nound")
		sys.exit(1)


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
