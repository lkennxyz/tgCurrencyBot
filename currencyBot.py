#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
import requests
import time
import re

file = open(".token.txt","r")
TG_TOKEN = file.readline().rstrip()
TG_URL = "https://api.telegram.org/bot{}/".format(TG_TOKEN)

ER_TOKEN = file.readline().rstrip()
ER_URL = "https://v3.exchangerate-api.com/pair/{}/".format(ER_TOKEN)
file.close()

def get_url(url):
	response = requests.get(url)
	content = response.content.decode("utf8")
	return content

def get_json_from_url(url):
	content = get_url(url)
	js = json.loads(content)
	return js

def tg_get_updates():
	url = TG_URL + "getUpdates?timeout=100"
	js = get_json_from_url(url)
	return js

def tg_last_chat_id_and_text(updates):
	num_updates = len(updates["result"])
	last_update = num_updates - 1
	text = updates["result"][last_update]["message"]["text"]
	chat_id = updates["result"][last_update]["message"]["chat"]["id"]
	return (text, chat_id)

def tg_send_message(text, chat_id):
	url = TG_URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
	get_url(url)

def er_get_rate(cur):
	url = ER_URL + "{}/GBP".format(cur)
	js = get_json_from_url(url)
	rate = js["rate"]
	return rate

def convert(text):
	cur = ""
	if u"$" in text:
		cur = "USD"
	elif u"€" in text:
		cur = "EUR"
	rate = er_get_rate(cur)
	num = re.findall('\d+', text)
	converted = int(num[0]) * rate
	pounds = round(converted, 2)
	ret = "£" + str(pounds)
	return ret

def main():
	last_textchat = (None, None)
	STARTED = False
	while True:	
		text, chat = tg_last_chat_id_and_text(tg_get_updates())
		if (text, chat) != last_textchat:
			if STARTED is False:
				if text == "/start":
					tg_send_message("service started", chat)
					STARTED = True
			elif STARTED is True:
				ret = ""
				if u"$" in text or u"€" in text:
					ret = convert(text)
				elif text == "/help":
					ret = "send /$xxxx or /€xxxx to convert to £"
				elif text == "/stop":
					ret = "service stopped"
					STARTED = False
				else:
					ret = "No currency"
				tg_send_message(ret, chat)
			last_textchat = (text, chat)
		time.sleep(0.5)

if __name__ == '__main__':
	main()
