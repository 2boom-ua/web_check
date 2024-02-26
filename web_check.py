#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

import json
import telebot
import socket, errno
import os
import time
from schedule import every, repeat, run_pending
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl

def telegram_message(message : str):
	try:
		tb.send_message(CHAT_ID, message, parse_mode='markdown')
	except Exception as e:
		print(f"error: {e}")

if __name__ == "__main__":	
	CURRENT_PATH = "/root/web_check"
	HOSTNAME = open('/proc/sys/kernel/hostname', 'r').read().strip('\n')
	ssl._create_default_https_context = ssl._create_unverified_context
	if os.path.exists(f"{CURRENT_PATH}/config.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/config.json", "r").read())
		TOKEN = parsed_json["TOKEN"]
		CHAT_ID = parsed_json["CHAT_ID"]
		MIN_REPEAT = int(parsed_json["MIN_REPEAT"])
		tb = telebot.TeleBot(TOKEN)
		telegram_message(f"*{HOSTNAME}* (hosts)\nhosts monitor started: check period {MIN_REPEAT} minute(s)")
	else:
		print("config.json not nound")

@repeat(every(MIN_REPEAT).minutes)
def web_check():
	TMP_FILE = "/tmp/status_web.tmp"
	web_list = []
	count_hosts = 0
	RED_DOT, GREEN_DOT  = "\U0001F534", "\U0001F7E2"
	status_message = old_status_str = new_status_str = ""
	if os.path.exists(f"{CURRENT_PATH}/url_list.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/url_list.json", "r").read())
		web_list = parsed_json["list"]
		total_hosts = len(web_list)
		if not os.path.exists(TMP_FILE) or total_hosts != os.path.getsize(TMP_FILE):
			with open(TMP_FILE, "w") as file:
				old_status_str += "0" * total_hosts
				file.write(old_status_str)
			file.close()
		else:
			with open(TMP_FILE, "r") as file:
				old_status_str = file.read()
				li = list(old_status_str)
			file.close()
		for i in range(total_hosts):
			req = Request(web_list[i][0], headers={'User-Agent': 'Mozilla/5.0'})
			try:
				response = urlopen(req)#timeout
			except HTTPError as e:
				li[i] = "1"
				status_message += f"{RED_DOT} - *{web_list[i][1]}*, error: _{e.code}_\n"
			except URLError as e:
				li[i] = "1"
				status_message += f"{RED_DOT} - *{web_list[i][1]}*, reason: _{e.reason}_\n"		
			else:
				li[i] = "0"
				count_hosts += 1
		new_status_str = "".join(li)
		bad_hosts = total_hosts - count_hosts
		if count_hosts == total_hosts:
			status_message = f"{GREEN_DOT} - controlled host(s):\n|ALL| - {total_hosts}, |OK| - {count_hosts}, |BAD| - {bad_hosts}"
		else:
			status_message = f"controlled host(s):\n|ALL| - {total_hosts}, |OK| - {count_hosts}, |BAD| - {bad_hosts}\n{status_message}"
		if old_status_str != new_status_str:
			with open(TMP_FILE, "w") as file:
				file.write(new_status_str)
			file.close()
			telegram_message(f"*{HOSTNAME}* (hosts)\n{status_message}")
	else:
		print("url_list.json not nound")
	
while True:
    run_pending()
    time.sleep(1)
