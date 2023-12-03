#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023

import json
import telebot
import socket, errno
import os.path
import os
import time
from schedule import every, repeat, run_pending
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl

def get_host_name():
	if os.path.exists("/proc/sys/kernel/hostname"):
		return open("/proc/sys/kernel/hostname").read().strip("\n")
	else:
		return ""
		
def hbold(item):
	return telebot.formatting.hbold(item)

current_path = "/root/web_check"
hostname = hbold(get_host_name())
ssl._create_default_https_context = ssl._create_unverified_context
if os.path.exists(f"{current_path}/config.json"):
	parsed_json = json.loads(open(f"{current_path}/config.json", "r").read())
	min_repeat = int(parsed_json["minutes"])
else:
	min_repeat = 3
RED_DOT, GREEN_DOT  = "\U0001F534", "\U0001F7E2"

if os.path.exists(f"{current_path}/telegram_bot.json"):			
	parsed_json = json.loads(open(f"{current_path}/telegram_bot.json", "r").read())
	TOKEN = parsed_json["TOKEN"]
	CHAT_ID = parsed_json["CHAT_ID"]
	tb = telebot.TeleBot(TOKEN)
	try:
		tb.send_message(CHAT_ID, f"{hostname} (hosts)\nhosts monitor started: check period {min_repeat} minute(s)", parse_mode='html')
	except Exception as e:
		print(f"error: {e}")
else:
	print("telegram_bot.json not nound")
	
@repeat(every(min_repeat).minutes)
def web_check():
	tmp_file = "/tmp/status_web.tmp"
	web_list = []
	count_hosts = 0
	status_message = old_status_str = new_status_str = ""
	if os.path.exists(f"{current_path}/url_list.json"):
		parsed_json = json.loads(open(f"{current_path}/url_list.json", "r").read())
		web_list = parsed_json["list"]
		total_hosts = len(web_list)
		if not os.path.exists(tmp_file) or total_hosts != os.path.getsize(tmp_file):
			with open(tmp_file, "w") as status_file:
				for i in range(total_hosts):
					old_status_str += "0"
				status_file.write(old_status_str)
			status_file.close()
		with open(tmp_file, "r") as status_file:
			old_status_str = status_file.read()
			li = list(old_status_str)
			status_file.close()
			
		for i in range(total_hosts):
			req = Request(web_list[i][0], headers={'User-Agent': 'Mozilla/5.0'})
			try:
				response = urlopen(req)#timeout
			except HTTPError as e:
				li[i] = "1"
				status_message += f"{RED_DOT} - {hbold(web_list[i][1])}, error: {e.code}\n"
			except URLError as e:
				li[i] = "1"
				status_message += f"{RED_DOT} - {hbold(web_list[i][1])}, reason: {e.reason}\n"
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
			with open(tmp_file, "w") as status_file:
				status_file.write(new_status_str)
				status_file.close()
			try:
				tb.send_message(CHAT_ID, f"{hostname} (hosts)\n{status_message}", parse_mode='html')
			except Exception as e:
				print(f"error: {e}")
			print(f"{hostname} (hosts)\n{status_message}")
	else:
		print("url_list.json not nound")
	
while True:
    run_pending()
    time.sleep(1)
