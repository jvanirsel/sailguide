# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 09:53:36 2024

@author: ROWANJ2
"""

# import logging
# logging.basicConfig(level=logging.DEBUG)

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# client = WebClient()
# api_response = client.api_test()

# slack_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token='xoxb-1362981002915-7756260254116-B7gh38nBTTe07jdbnV2dKrGi')

# try:
#     response = client.chat_postMessage(
#         channel="C01ANV06ASF",
#         text="This is where chamber info will go"
#     )
# except SlackApiError as e:
#     # You will get a SlackApiError if "ok" is False
#     assert e.response["error"]  
    
def update_canvas(channel_id, view_id, blocks):
    try:
        client.views_update(
            view_id=view_id,
            view={
                "type": "home",
                "blocks": blocks
            }
        )
    except SlackApiError as e:
        print(f"Error updating canvas: {e}")
        
# block = []
# update_canvas("C01ANV06ASF" ,"C01ANV06ASF", block)

def create_canvas(channel_id, title):
    try:
        response = client.views_publish(
            user_id=channel_id,
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": title
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Loading data..."
                        }
                    }
                ]
            }
        )
        return response["view"]["id"]
    except SlackApiError as e:
        print(f"Error creating canvas: {e}")
        
        
# ID = create_canvas("U0214GG961Y", "Chamber Status 2")

# response = client.chat_update(
#     channel="D07N5NLK6NN",
#     ts="1726759750.458769",
#     text="Updating this field, again, again"
#     )


class SlackBridge():
    def __init__(self):
        self.SLACK_BOT_TOKEN = "xoxb-1362981002915-7756260254116-B7gh38nBTTe07jdbnV2dKrGi"
        self.userID = "D021UANU6M6"
        self.plasmaChamberID = "C01ANV06ASF"
        self.msgTimeStamp = "1726767751.216949"
        self.client = WebClient(token='xoxb-1362981002915-7756260254116-B7gh38nBTTe07jdbnV2dKrGi')
        
    def updateStatus(self, newText):
        self.response = self.client.chat_update(
            channel=self.plasmaChamberID,
            ts=self.msgTimeStamp,
            text=newText
            )
        # print(self.response)    
        
    def createMessageFromData(self, data):
        pass
    
c = SlackBridge()
c.updateStatus("This is where chamber info will go\n\nTesting update...")