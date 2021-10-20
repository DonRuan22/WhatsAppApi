# -*- coding: utf-8 -*-
import os
from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from deep_translator import GoogleTranslator
import logging


app = Flask(__name__)
client = Client(os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))

def respond(id,message):
    receivedMessage = GoogleTranslator(source='auto', target='en').translate(text=message)
    payload = {'sender': id,'message': receivedMessage}
    #payload_json = json.loads(payload)
    logging.warning(str(payload))
    response_rasa = requests.post('https://don-mvp-vc5xcezzwa-uc.a.run.app/webhooks/rest/webhook', json = payload, timeout=None)
    logging.warning('response') 
    logging.warning(response_rasa.json()) 
    response_data=[]
    if(len(response_rasa.json())>0):
        response_data = response_rasa.json()[0]
        #response_port = GoogleTranslator(source='auto', target='pt').translate(text=response_rasa.json()[0]["text"] )
    else:
        response_data = {}
        response_data['text'] = 'Sorry error server'
    if('custom' in response_data):
        if('title' in response_data['custom'][0]):
            data_custom = response_data['custom']
            response_text = 'Esses são os produtos mais recomendados para vc:\n'
            for each in data_custom:
                elem={}
                elem['title'] = each['title']
                elem['image_url'] = each['image']
                elem['subtitle'] = each['short_desc']
                response_text = response_text + elem['image_url']+'\n'
                
                #response_info.append(elem)
            
        elif('text' in response_data):
            logging.warning(response_data) 
            response = {"text": response_data['text'] }
    elif('text' in response_data):
            logging.warning(response_data) 
            response_text = response_data['text']
    response = MessagingResponse()
    response.message(response_text)
    return str(response)

@app.route('/message', methods=['POST'])
def reply():
    message = request.form.get('Body').lower()
    id = request.form.get('From').lower()
    if message:
        return respond(id,message)

if __name__ == '__main__':
    app.run()