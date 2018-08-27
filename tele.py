from chatbot_rest import *
import json
import requests
import time

vocab, matrix= gen_matrix()


token= "YOUR BOT TOKEN"
URL= "https://api.telegram.org/bot{}/".format(token)

def get_url(url):
    '''
        This function returns the response to the GEt request to the url
    '''
    response = requests.get(url)
    content = response.content.decode("utf-8")
    return content


def get_json_from_url(url):
    '''
        This function returns the JSON response to the bot's url
    '''
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates():
    url = URL + "getUpdates"
    js = get_json_from_url(url)
    return js



def get_last_chat_id_and_text(updates):
    '''
    This function returns the message id and user id of the last message/query to the bot.
    '''
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    (text, chat_id,chat_name)= (None,None,None)
    if last_update>=0 :
    	text = updates["result"][last_update]["message"]["text"]
    	chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    	chat_name = updates["result"][last_update]["message"]["from"]["first_name"]
    return (text, chat_id,chat_name)



def send_message(text, chat_id,name):
    '''
        Sends a message to the designated user with the help of Telegram's API.
    '''
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    print("Sending message to "+ name)
    get_url(url)


def main():
    '''
        This checks if the bot has received a message by periodically checking the last message and the corresponding user id. This uses long polling, which should be only used for testing purposes'''
    last_textchat = get_last_chat_id_and_text(get_updates())
    while True:
        text, chat,name = get_last_chat_id_and_text(get_updates())
        if (text, chat,name) != last_textchat:
        	print("Message received from "+name+": "+text)
        	answer= bot_response(text.encode('utf-8'),matrix)
	        send_message(answer, chat, name)
	        last_textchat = (text, chat,name)
		time.sleep(0.25)


if __name__ == '__main__':
    main()