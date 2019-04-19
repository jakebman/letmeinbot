import json
from botocore.vendored import requests
from os import environ

def debug(**msgs) :
    index = 0
    for key in msgs:
        debug_msg = """
```
{0}:
{1}         """.format(key, json.dumps(msgs[key], indent=3))

        send(
            "Y2lzY29zcGFyazovL3VzL1BFT1BMRS83NDk5YTMzOC02YzM4LTQzMDctYjVkMi1jYjVjYTg2OGM2ODY", #TODO: consider a letmein bot debug room
            debug_msg)
        

def send(personId, markdown):
    payload = {
            "toPersonId": personId,
            "markdown": markdown,
        }
    requests.post('https://api.ciscospark.com/v1/messages', headers={"Authorization": TOKEN}, json=payload)

def roomList():
    return requests.get('https://api.ciscospark.com/v1/rooms?type=group', headers={"Authorization": TOKEN}).json()['items']

def list_rooms(personId):
    rooms = roomList()
    names = [room['title'] for room in rooms]

    # TODO: format into prompt
    prompt = json.dumps(names)

    send(personId, prompt)
    
    
def create_membership(personId, roomId):
    payload = {'personId':personId, 'roomId': roomId}
    TOKEN = "Bearer {}".format()
    r = requests.post('https://api.ciscospark.com/v1/memberships', headers={"Authorization": TOKEN}, json=payload)
    debug(creation=r.json(), headers=dict(r.headers))
    

def join_room(personId, roomTitle):
    rooms = roomList()
    ids = [room['id']for room in rooms if roomTitle in room['title']]
    for id in ids:
        create_membership(personId, id)
    
    

def lambda_handler(event, context):
    message_id = event['data']['id']
    message = requests.get('https://api.ciscospark.com/v1/messages/{}'.format(message_id), headers={"Authorization": environ['Authorization']})
    
    body = message.json()#['id']
    
    text = body['text']
    
    if "debug" in text or 'debug' in event: # string contains, or key exists
        debug(event=event, message_itself=body)
    
    if 'list' in text:
        list_rooms(body['personId'])
    
    if 'join' in text:
        join_room(body['personId'], text.lstrip("join "))
    
    return {
        'statusCode': 200,
        'body': body
    }
