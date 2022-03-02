import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from eugo.models import *

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        #TODO! change 'global123' to channel user requests
        self.room_group_name = 'global123'
        #add user to a new channel to 'global123'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, #chatroom
            self.channel_name #users personal pathway to channel
        )
        self.accept()

    def receive(self, text_data):
        print("socket recieveing")
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'username':username
            }
        )

    def chat_message(self, event):
        message = event['message']
        channel_id = 'global123'
        username = event['username']
        channel_id_k = ChatChannel.objects.filter(channel_id  = channel_id)[0]
        new_message = ChatMessage(channel_id = channel_id_k , user = username, content=message)
        new_message.save()
        date = new_message.date
        print("message : " + message)

        self.send(text_data=json.dumps({
            'type':'chat',
            'message':message,
            'username':username,
            'date': str(date)[10:16],
        }))