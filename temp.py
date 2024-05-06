import requests
import json,os
from flask import request, jsonify
WEBEX_TOKEN = os.environ.get('bot_token')

#WEBEX_TOKEN = Bot Access Token
#user_access_token = user access token

def get_message(id):   
    url = f"https://webexapis.com/v1/messages/{id}"  
    headers = {
        "Authorization": f"Bearer {WEBEX_TOKEN}"
    }
    response = requests.get(url, headers=headers)    
    if response.status_code == 200:
        return response.json()
    else:
        return None

def send_webex_message(roomId):
    
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WEBEX_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
  "roomId": roomId,
  "markdown": "Card with a button!",
  "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "version": "1.0",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "Interactive Bot",
                        "weight": "Bolder",
                        "size": "Large",
                        "horizontalAlignment": "Center"
                    },
                    {
                        "type": "TextBlock",
                        "text": "Enter your text below:",
                        "wrap": True
                    },
                    {
                        "type": "Input.Text",
                        "id": "userInput",
                        "placeholder": "Type here..."
                    },
                    {
                        "type": "TextBlock",
                        "text": " ",
                        "spacing": "Large"
                    },
                    {
                        "type": "Input.ChoiceSet",
                        "id": "option",
                        "style": "expanded",
                        "choices": [
                            {
                                "title": "List Rooms",
                                "value": "List Rooms"
                            },
                            {
                                "title": "Last Message",
                                "value": "last Message"
                            },
                            {
                                "title": "Book a meeting",
                                "value": "book a Meeting"
                            }
                        ]
                    }
                ],
                "actions": [
                    {
                        "type": "Action.Submit",
                        "title": "Submit"
                    }
                ]
            }
        }
    ]
}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  
    return response.json()

def Get_Attachment_Action_Details(id):
    url = f"https://webexapis.com/v1/attachment/actions/{id}"
    headers = {
    "Authorization": f"Bearer {WEBEX_TOKEN}"
    }
    response = requests.get(url, headers=headers)    
    if response.status_code == 200:
        return response.json()
    else:
        return None
 
def bot_report_bad_command(roomId, command):
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WEBEX_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "roomId": roomId,
        "text": f"The command '{command}' is not recognized."
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()   
    return response.json()

def list_rooms(user_access_token, roomId, parent_id): 
    rooms_endpoint = "https://api.ciscospark.com/v1/rooms"

    params = {
        "type": "group",  
        "max": 10,   
        "sortBy": "lastactivity",   
        "sortOrder": "desc"   
    }

    headers = {
        "Authorization": f"Bearer {user_access_token}"
    }
    response = requests.get(rooms_endpoint, params=params, headers=headers)

    if response.status_code == 200:
        rooms_data = response.json()
        
        rooms = [(room["title"], room["id"]) for room in rooms_data["items"]]
        
        message = "List of 10 rooms where the user is a member (last active first):\n"
        for room_name, _ in rooms:
            message += f"- {room_name}\n"
        
        messages_endpoint = "https://api.ciscospark.com/v1/messages"
        
        payload = {
            "roomId": roomId,
            "text": message,
            "parentId": parent_id
        }

        headers2 = {
        "Authorization": f"Bearer {WEBEX_TOKEN}"
        }
        
        response = requests.post(messages_endpoint, json=payload, headers=headers2)
        if response.status_code == 200:
            print("List of rooms sent successfully.")
        else:
            print(f"Failed to send the list of rooms. Status code: {response.status_code}")
    else:
        print(f"Error: Failed to retrieve rooms (Status code: {response.status_code})")


def last_message(roomId, messageId):
    url = "https://webexapis.com/v1/messages"

    payload = {
        "parentId": messageId,
        "roomId": roomId,
        "markdown": "Card with a button!",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.1",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "Room Name"
                        },
                        {
                            "type": "Input.Text",
                            "id": "textInput",
                            "placeholder": "Enter the room name"
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.Submit",
                            "title": "Submit"
                        }
                    ]
                    
                }

            }
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {WEBEX_TOKEN}"
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# room name recived, last message is sent by Bot.
def get_last_msg(user_access_token, parent_room_id, room_name, parentId):    
    room_name = room_name
    url = "https://webexapis.com/v1/rooms"
    headers = {
        "Authorization": f"Bearer {user_access_token}"
    }
    response = requests.get(url, headers=headers)
    
    # Find Room ID from the given Room Name
    room_id = None
    if response.status_code == 200:
        for room in response.json()['items']:
            if room['title'] == room_name:
                room_id = room['id']
                print("Room ID:", room_id)
                break
        else:
            print("Room not found:", room_name)
    else:
        print("Error:", response.status_code, response.text)


    url = f"https://webexapis.com/v1/messages?roomId={room_id}&max=5"

    headers = {
        "Authorization": f"Bearer {user_access_token}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        last_message = response.json()['items'][0]['text']
        messages_endpoint = "https://webexapis.com/v1/messages"
       
        payload = {
            "roomId": parent_room_id,
            "text": last_message,
            "parentId": parentId
        }
        headers3 = {
        "Authorization": f"Bearer {WEBEX_TOKEN}"
        }
        response2 = requests.post(messages_endpoint, json=payload, headers=headers3)
        if response2.status_code == 200:
            return response2.json()
        else:
            return None

# Bot sends it to allow users fill in the meetings details.       
def send_meeting_card(roomId, parent_messageId):

    url = "https://webexapis.com/v1/messages"

    payload = {
        "parentId": parent_messageId,
        "roomId": roomId,
        "markdown": "Card with a button!",
    "attachments": [
        {
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.1",
            "body": [
            {
                "type": "Input.Text",
                "id": "title",
                "placeholder": "Enter title",
                "label": "Title"
            },
            {
                "type": "Input.Date",
                "id": "start_date",
                "placeholder": "Select start date",
                "label": "Start Date"
            },
            {
                "type": "Input.Time",
                "id": "start_time",
                "placeholder": "Select start time",
                "label": "Start Time"
            },
            {
                "type": "Input.Date",
                "id": "end_date",
                "placeholder": "Select end date",
                "label": "End Date"
            },
            {
                "type": "Input.Time",
                "id": "end_time",
                "placeholder": "Select end time",
                "label": "End Time"
            },
            {
                "type": "Input.ChoiceSet",
                "id": "timezone",
                "label": "Timezone",
                "choices": [
                {
                    "title": "America/Los_Angeles",
                    "value": "America/Los_Angeles"
                },
                {
                    "title": "Asia/Kolkata",
                    "value": "Asia/Kolkata"
                },
                {
                    "title": "Europe/Dublin",
                    "value": "Europe/Dublin"
                }
                ]
            }
            ],
            "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit"
            }
            ]
        }
        }
    ]    
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {WEBEX_TOKEN}"
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def book_meeting(user_access_token, start_date,end_date,start_time, end_time,title, roomId, parent_messageId):


    url = "https://webexapis.com/v1/meetings"

    start_datetime = f"{start_date}T{start_time}"
    end_datetime = f"{end_date}T{end_time}"

    payload = {
        'title': title,
        'start': start_datetime,
        'end': end_datetime
    }

    headers = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {user_access_token}"
    }
     
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        # Parse the JSON string
        data = response.json()
        # Define the endpoint for sending messages
        reply_2_bot_url = "https://api.ciscospark.com/v1/messages"
            # Define the payload for the message
        payload = {
            "roomId": roomId,
            "text": f"Meeting Details:\n"
                    f"Meeting Number: {data.get('meetingNumber')}\n"
                    f"Title: {data.get('title')}\n"
                    f"Start: {data.get('start')}\n"
                    f"End: {data.get('end')}\n"
                    f"Host Display Name: {data.get('hostDisplayName')}\n"
                    f"Host Email: {data.get('hostEmail')}",
            "parentId": parent_messageId
        }

        # HTTP headers with the access token
        headers2 = {
        "Authorization": f"Bearer {WEBEX_TOKEN}"
        }

            # Make the request to send the message
        requests.post(reply_2_bot_url, json=payload, headers=headers2)
    else:
        print("Error!")




    
