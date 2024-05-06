from flask import Flask, request, jsonify
import requests
from temp  import send_webex_message, Get_Attachment_Action_Details,get_message, bot_report_bad_command,list_rooms,last_message,get_last_msg,send_meeting_card,book_meeting
import json, os
webhook = ''
# token = os.environ.get('TOKEN')

app = Flask(__name__)
accessToken = None  

def save_access_token(token):
    global accessToken
    accessToken = token
    print("Access Token:", accessToken)

@app.route('/', methods=['POST'])
def webhook():
    
    global accessToken, father_Id   

    data = request.json
   
    for key, value in data.items():
        # Determine if the Bot was at mentioned or Submit button hit on the card.
        if key == "name" and value == "@bot":  # When @ mentioned the Bot.
            msg = get_message(data['data']['id'])
            # Verify if the good command entered.
            if msg['text'].endswith("help"):   
                print("\n\n Received message:\n\n", msg['text'])  # Print the value of msg['text'] to the terminal
                send_webex_message(data['data']['roomId'])  # Sends card into this Room.
                return msg['text']  # Return msg['text'] as the response
            else:
                bot_report_bad_command(data['data']['roomId'], msg['text'].split()[-1])
                error_message = {"error": "Bad command"}
                print("Failed to fetch message:", error_message)  # Print the error message to the terminal
                return jsonify(error_message), 500  # Return the error message along with status code

        # Dictates card action by user and corresponding response.
        # Webhook 2 triggered.
        if key == "name" and value == "get_messages":  # When Submit button pressed on the Bot.
            print(data, "\n\n\n USER PERFORMED CARD ACTIONS\n\n\n")
            parent_id = data['data']['messageId'] # Do not change.
             # Initialize messageId only if it's not already set
            # if messageId is None and 'data' in data and 'messageId' in data['data']:
            #     messageId = data['data']['messageId']
            msg = get_message(parent_id)
            usr_input = Get_Attachment_Action_Details(data['data']['id'])
            print("\n\n\n Message extraction for the Submit Action \n\n\n", usr_input)

            try:
                
                if msg['attachments'][0]['content']['body'][4]['type'] == 'Input.ChoiceSet':
                    if 'inputs' in usr_input and 'userInput' in usr_input['inputs'] and usr_input['inputs']['userInput']:
                        save_access_token(usr_input['inputs']['userInput'])
                        father_Id = usr_input['messageId']

                    if accessToken:
                        if usr_input['inputs']['option'] == "List Rooms":
                            list_rooms(accessToken, data['data']['roomId'], data['data']['messageId'])

                        if usr_input['inputs']['option'] == "last Message":
                            print(usr_input['inputs'], "?????")
                            last_message(data['data']['roomId'], data['data']['messageId'])

                        if usr_input['inputs']['option'] == "book a Meeting":
                            print("Book a meetings....")
                            send_meeting_card(data['data']['roomId'], data['data']['messageId'])
                    else:
                        print("Access token not available")

            except IndexError:
                print("IndexError: list index out of range")
                try:
                    if 'inputs' in usr_input and 'textInput' in usr_input['inputs']:
                        # 'textInput' is present
                        room_name = usr_input['inputs']['textInput']
                        
                        get_last_msg(accessToken, data['data']['roomId'],  room_name, father_Id)
                        print("Room Name:", room_name)
                    else:
                        # 'textInput' is not present
                        print("Room name not found")
                except Exception as e:
                    # Handle the exception from the second try block
                    print("Error in the second try block:", e)

            try:
                if 'inputs' in usr_input and 'start_time' in usr_input['inputs']:
                # 'textInput' is present
                    start_date = usr_input['inputs']['start_date']
                    end_date = usr_input['inputs']['end_date']
                    end_time = usr_input['inputs']['end_time']
                    start_time = usr_input['inputs']['start_time']
                    title = usr_input['inputs']['title']
                    book_meeting(accessToken, start_date, end_date, start_time, end_time, title, data['data']['roomId'], father_Id)
                else:
                    # 'textInput' is not present
                    print("textInput is not present")
            except Exception as e:
                # Handle the exception from the second try block
                print("Error in the third try block:", e)

    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
