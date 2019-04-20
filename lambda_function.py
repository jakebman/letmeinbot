import json
from botocore.vendored import requests
from os import environ
from pprint import pprint
HEADERS = dict()
debug_settings = {'method':print}
def debug_to_me(msg):
    send(
        "Y2lzY29zcGFyazovL3VzL1BFT1BMRS83NDk5YTMzOC02YzM4LTQzMDctYjVkMi1jYjVjYTg2OGM2ODY", #TODO: consider a letmein bot debug room
        msg
        )
    print(msg)
    
def debug(**msgs) :
    index = 0
    for key in msgs:
        debug_msg = """
```
{0}:
{1}         """.format(key, json.dumps(msgs[key], indent=3))

        debug_settings['method'](debug_msg)
        

def send(personId, markdown):
    payload = {
            "toPersonId": personId,
            "markdown": markdown,
        }
    requests.post('https://api.ciscospark.com/v1/messages',  headers=HEADERS, json=payload)

def roomList():
     req = requests.get('https://api.ciscospark.com/v1/rooms?type=group', headers=HEADERS)
     js = req.json()
     return js['items']

def list_rooms(personId):
    rooms = roomList()
    names = [room['title'] for room in rooms]

    # TODO: format into prompt
    prompt = json.dumps(names)

    send(personId, prompt)
    
    
def create_membership(personId, roomId):
    payload = {'personId':personId, 'roomId': roomId}
    r = requests.post('https://api.ciscospark.com/v1/memberships',  headers=HEADERS, json=payload)
    debug(creation=r.json(), headers=dict(r.headers))
    

def join_room(personId, roomTitle):
    rooms = roomList()
    ids = [room['id']for room in rooms if roomTitle in room['title']]
    for id in ids:
        create_membership(personId, id)
    
    

def lambda_handler(event, context):
    if 'data' not in event:
        pprint(event)
    if 'id' not in event['data']:
        pprint(event['data'])
    message_id = event['data']['id']
    
    HEADERS['Authorization'] = environ['Authorization']
    print (HEADERS)
    message = requests.get('https://api.ciscospark.com/v1/messages/{}'.format(message_id), headers=HEADERS)
    
    body = message.json()#['id']
    
    text = body['text']
    if "debug" in text or 'debug' in event: # string contains, or key exists
        debug_settings['method'] = debug_to_me

    debug(event=event, message_itself=body)
    
    if 'list' in text:
        list_rooms(body['personId'])
    
    if 'join' in text:
        join_room(body['personId'], text.lstrip("join "))
    
    return {
        'statusCode': 200,
        'body': body
    }
