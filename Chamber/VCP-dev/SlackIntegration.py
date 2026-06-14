# import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import datetime as dt
from threading import Thread, Condition

class SlackBridge():
    def __init__(self):
        self.SLACK_BOT_TOKEN = "xoxb-1362981002915-7756260254116-B7gh38nBTTe07jdbnV2dKrGi"
        self.userID = "D021UANU6M6"
        self.jonasID = "U0214GG961Y"
        self.nathanID = "U01B2SJHQSV"
        self.julesID = "U09MYE1KS8M"
        self.ianID = "U072215J06P"
        self.plasmaChamberID = "C01ANV06ASF"
        self.msgTimeStamp = "1726767751.216949"
        self.client = WebClient(token=self.SLACK_BOT_TOKEN)
        self.cv = Condition()
        
    def doUpdateStatus(self, connectData, data):
        self.cv.acquire(1)
        newText = self.createMessageFromData(connectData, data)
        try:
            self.response = self.client.chat_update(
                channel=self.plasmaChamberID,
                ts=self.msgTimeStamp,
                text=newText
                )
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["error"]  
        self.cv.release()
        # print(self.response)    
    
    def updateStatus(self, connectData, data):
        self.thUpdateStatus = Thread( target = self.doUpdateStatus, name = '-Update-Slack', daemon = True, args=(connectData, data,) )
        self.thUpdateStatus.start()
        return True
    
    def createMessageFromData(self, connectData, data):
        try:
            time = dt.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            newText = "Chamber Status\n"
            try:
                # print("We have to be able to get this far")
                if connectData['l392'] == 1:
                    # print("l392 is connected, apparently")
                    p = '{:.2e}'.format(data['Pressure'])
                    p_set = '{:.2e}'.format(data['PCS setpoint'])
                    # print("P, p_set is ", p, ',', p_set)
                    newText = newText + '\n   Pressure: {:s} Torr (Setpoint: {:s} Torr)'.format( p[0:-2]+p[-1], p_set[0:-2]+p_set[-1] )
                else:
                    # print("yeehaw")
                    newText = newText + "\n   Pressure: disconnected"
                
                if connectData['mc'] == 1:
                    newText = newText + '\n   Motor Position (z,t): ({:.0f}cm, {:.1f}°)'.format(data['Motor Z'], data['Motor T'])
                else:
                    newText = newText + '\n   Motor position: disconnected'
                    
                if connectData['heat1'] == 1:
                    newText = newText + '\n   Heat 1: {:.1f}V, {:.2f}A. ≈{:.0f} K'.format(data['Heat1, V'], data['Heat1, A'], data['Heat1, T'])
                else:
                    newText = newText + '\n   Heat1: disconnected'
                
                if connectData['heat2'] == 1:
                    newText = newText + '\n   Heat 2: {:.1f}V, {:.2f}A. ≈{:.0f} K'.format(data['Heat2, V'], data['Heat2, A'], data['Heat2, T'])
                else:
                    newText = newText + '\n   Heat2: disconnected'
                    
                if connectData['bias'] == 1:
                    newText = newText + '\n   Bias: {:.1f}V, {:.2f}A'.format(data['Bias, V'], data['Bias, A'])
                else:
                    newText = newText + '\n   Bias: disconnected'
                
                newText = newText + '\n\nLast updated: {:s}'.format(time)
                
            except TypeError:
                print("Something was the wrong type for ")
            except:
                print("Error setting newText. Text so far is ", newText)
                return 'Error getting update from chamber.\n\nLast updated: {:s}'.format(time)
            return newText
        
        except:
            print("Big errors somewhere in Slack Integrator")
            return 'Error'
    
    def sendMessageToJonas(self, newText):
        #self.thMessageJR = Thread( target = self.doSendMessageToJonas, name = 'Jonas-Update', daemon = True, args=(newText,) )
        #self.thMessageJR.start()
        self.thMessageNG = Thread( target = self.doSendMessageToJonas, name = 'Nathan-Update', daemon = True, args=(newText,self.nathanID) )
        self.thMessageNG.start()
        self.thMessageJV = Thread( target = self.doSendMessageToJonas, name = 'Jules-Update', daemon = True, args=(newText,self.julesID) )
        self.thMessageJV.start()
        self.thMessageIH = Thread( target = self.doSendMessageToJonas, name = 'Ian-Update', daemon = True, args=(newText,self.ianID) )
        self.thMessageIH.start()
        return True
    
    def doSendMessageToJonas(self, newText,userID):
        try:
            self.msgJonas = self.client.chat_postMessage(
                channel=userID,
                text=newText
            )
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["error"]  
            
    
            
# c = SlackBridge()