#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

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
from requests.exceptions import RequestException


def getHostname():
	hostname = ""
	if os.path.exists('/proc/sys/kernel/hostname'):
		with open('/proc/sys/kernel/hostname', "r") as file:
			hostname = file.read().strip('\n')
	return hostname
	
def get_modification_time(file_path):
	modification_time = os.path.getmtime(file_path)
	return datetime.datetime.fromtimestamp(modification_time)


def SendMessage(message : str):
	message = message.replace("\t", "")
	if telegram_on:
		try:
			response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if discord_on:
		try:
			response = requests.post(discord_web, json={"content": message.replace("*", "**")})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if slack_on:
		try:
			response = requests.post(slack_web, json = {"text": message})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	message = message.replace("*", "")
	header = message[:message.index("\n")].rstrip("\n")
	message = message[message.index("\n"):].strip("\n")
	if gotify_on:
		try:
			response = requests.post(f"{gotify_web}/message?token={gotify_token}",\
			json={'title': header, 'message': message, 'priority': 0})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if ntfy_on:
		try:
			response = requests.post(f"{ntfy_web}/{ntfy_sub}", data=message.encode(encoding='utf-8'), headers={"Title": header})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if pushbullet_on:
		try:
			response = requests.post('https://api.pushbullet.com/v2/pushes',\
			json={'type': 'note', 'title': header, 'body': message},\
			headers={'Access-Token': pushbullet_api, 'Content-Type': 'application/json'})
		except requests.exceptions.RequestException as e:
			print("error:", e)


if __name__ == "__main__":	
	current_path =  os.path.dirname(os.path.realpath(__file__))
	hostname = getHostname()
	old_status = ""
	web_list = []
	ssl._create_default_https_context = ssl._create_unverified_context
	telegram_on = discord_on = gotify_on = ntfy_on = slack_on = pushbullet_on = config_files = False
	token = chat_id = discord_web = gotify_web = gotify_token = ntfy_web = ntfy_sub = pushbullet_api = slack_web = messaging_service = ""
	if os.path.exists(f"{current_path}/config.json") and os.path.exists(f"{current_path}/url_list.json"):
		config_files = True
		with open(f"{current_path}/url_list.json", "r") as file:
			parsed_json = json.loads(file.read())
		url_list_date = get_modification_time(f"{current_path}/url_list.json")
		web_list = parsed_json["list"]
		with open(f"{current_path}/config.json", "r") as file:
			parsed_json = json.loads(file.read())
		telegram_on = parsed_json["TELEGRAM"]["ON"]
		discord_on = parsed_json["DISCORD"]["ON"]
		gotify_on = parsed_json["GOTIFY"]["ON"]
		ntfy_on = parsed_json["NTFY"]["ON"]
		pushbullet_on = parsed_json["PUSHBULLET"]["ON"]
		slack_on = parsed_json["SLACK"]["ON"]
		if telegram_on:
			token = parsed_json["TELEGRAM"]["TOKEN"]
			chat_id = parsed_json["TELEGRAM"]["CHAT_ID"]
			messaging_service += "- messenging: Telegram,\n"
		if discord_on:
			discord_web = parsed_json["DISCORD"]["WEB"]
			messaging_service += "- messenging: Discord,\n"
		if gotify_on:
			gotify_web = parsed_json["GOTIFY"]["WEB"]
			gotify_token = parsed_json["GOTIFY"]["TOKEN"]
			messaging_service += "- messenging: Gotify,\n"
		if ntfy_on:
			ntfy_web = parsed_json["NTFY"]["WEB"]
			ntfy_sub = parsed_json["NTFY"]["SUB"]
			messaging_service += "- messenging: Ntfy,\n"
		if pushbullet_on:
			pushbullet_api = parsed_json["PUSHBULLET"]["API"]
			messaging_service += "- messenging: Pushbullet,\n"
		if slack_on:
			slack_web = parsed_json["SLACK"]["WEB"]
			messaging_service += "- messenging: Slack,\n"
		min_repeat = int(parsed_json["MIN_REPEAT"])
		SendMessage(f"*{hostname}* (hosts)\nhosts monitor:\n{messaging_service}- polling period: {min_repeat} minute(s).")
	else:
		print("url_list.json or/and config.json not nound")


@repeat(every(min_repeat).minutes)
def web_check():
	current_status = []
	count_hosts = 0
	red_dot, green_dot  = "\U0001F534", "\U0001F7E2"
	status_message = new_status = ""
	global old_status
	global web_list
	global url_list_date
	if config_files:
		current_url_list_date = get_modification_time(f"{current_path}/url_list.json")
		if url_list_date != current_url_list_date:
			with open(f"{current_path}/url_list.json", "r") as file:
				parsed_json = json.loads(file.read())
			web_list = parsed_json["list"]
			url_list_date = current_url_list_date
		total_hosts = len(web_list)
		if len(old_status) == 0: old_status = "0" * total_hosts
		current_status = list(old_status)
		for i in range(total_hosts):
			#req = Request(web_list[i][0], headers={'User-Agent': 'Mozilla/5.0'})
			req = Request(web_list[i][0], headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'})
			try:
				response = urlopen(req)#timeout
			except HTTPError as e:
				current_status[i] = "1"
				#status_message += f"{red_dot} *{web_list[i][1]}*, error: {e.code}\n"
				status_message += f"{red_dot} *{web_list[i][1]}:* {e.code}\n"
			except URLError as e:
				current_status[i] = "1"
				#status_message += f"{red_dot} *{web_list[i][1]}*, reason: {e.reason}\n"
				status_message += f"{red_dot} *{web_list[i][1]}:* {e.reason}\n"				
			else:
				current_status[i] = "0"
				count_hosts += 1
		new_status = "".join(current_status)
		bad_hosts = total_hosts - count_hosts
		if count_hosts == total_hosts:
			status_message = f"{green_dot} monitoring host(s):\n|ALL| - {total_hosts}, |OK| - {count_hosts}, |BAD| - {bad_hosts}"
		else:
			status_message = f"monitoring host(s):\n|ALL| - {total_hosts}, |OK| - {count_hosts}, |BAD| - {bad_hosts}\n{status_message}"
		if old_status != new_status:
			old_status = new_status
			SendMessage(f"*{hostname}* (hosts)\n{status_message}")
	else:
		print("url_list.json or/and config.json not nound")


while True:
	run_pending()
	time.sleep(1)
