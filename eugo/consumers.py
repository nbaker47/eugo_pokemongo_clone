""" ---------------------------- IMPORTS -------------------------------------------------------------- """
""" EUGO IMPORTS ------------- """
from eugo.models import *                                   # all of the models to access the database

""" OTHER IMPORTS ------------ """
from channels.generic.websocket import WebsocketConsumer    # this is the specific users that can use
                                                            # the chat
from asgiref.sync import async_to_sync
import json                                                 # json for processing data in json format


""" ---------------------------- CONSUMERS ------------------------------------------------------------ """
""" CHAT CONSUMERS ----------- """
""" This class handles all of the chat communication """
class ChatConsumer(WebsocketConsumer):
    """ CONNECT -------------- """
    """ This method connects the user to the chat """
    def connect(self):
        # select the chat room
        #TODO! change 'global123' to channel user requests
        self.room_group_name = 'global123'
        # add user to a new channel to 'global123'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,   # chatroom
            self.channel_name       # users personal pathway to channel
        )
        self.accept()


    """ RECIEVE -------------- """
    """ This method handles the receiving of chat messages (sent from other users) """
    def receive(self, text_data):
        # let the server debug know that a user is recieving a message
        print("socket recieveing")
        # load the data
        text_data_json = json.loads(text_data)
        # get the message and the username from the chat data
        message = text_data_json['message']
        username = text_data_json['username']

        # send the message to the corresponding channel
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'username':username
            }
        )


    """ CHAT MESSAGE --------- """
    """ This method handles the creation of chat messages """
    def chat_message(self, event):
        # set the event type to message
        message = event['message']
        # set the channel ID
        channel_id = 'global123'
        # set the username 
        username = event['username']
        channel_id_k = ChatChannel.objects.filter(channel_id  = channel_id)[0]
        # create a new message (in the ChatMessage table)
        new_message = ChatMessage(channel_id = channel_id_k , user = username, content=message)
        # save the new message
        new_message.save()
        # get the date of the new message
        date = new_message.date
        # print message to console
        print("message : " + message)

        # finally, send the message in json format
        self.send(text_data=json.dumps({
            'type':'chat',
            'message':message,
            'username':username,
            'date': str(date)[10:16],
        }))