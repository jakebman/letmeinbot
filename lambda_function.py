import json
from botocore.vendored import requests
from os import environ
from pprint import pprint

#BOT_ID = "Y2lzY29zcGFyazovL3VzL0FQUExJQ0FUSU9OL2NkZWFjMzY2LWU2MzQtNDVmNS05NmRiLWJiMGJiNTMxZTE0Yg"
MYSELF = 'Y2lzY29zcGFyazovL3VzL1BFT1BMRS9jZGVhYzM2Ni1lNjM0LTQ1ZjUtOTZkYi1iYjBiYjUzMWUxNGI'
HEADERS = dict()
debug_settings = {'method': print}


def debug_to_me(msg):
    # TODO: consider a letmein bot debug room
    send(
        "Y2lzY29zcGFyazovL3VzL1BFT1BMRS83NDk5YTMzOC02YzM4LTQzMDctYjVkMi1jYjVjYTg2OGM2ODY",
        msg
    )
    print(msg)


def debug(*msgs, **kmsg):
    msgs = list(msgs)
    for key in kmsg:
        debug_msg = """```
{0}:
{1}""".format(key, json.dumps(kmsg[key], indent=3))
        msgs.append(debug_msg)

    for msg in msgs:
        debug_settings['method'](msg)


def respond(context_msg, markdown, personal=False):
    room = None

    personId = context_msg['personId']
    if context_msg['roomType'] != 'direct':
        room = context_msg['roomId']

    send(personId, markdown, room, personal)


def send(personId, markdown, room=None, personal=False):
    payload = dict()
    if room:
        payload["roomId"] = room
        if personal and personId:
            markdown = "<@personId:{}>: {}".format(personId, markdown)
    else:
        payload["toPersonId"] = personId

    payload["markdown"] = markdown
    print("sending create request!")
    pprint(payload)
    resp = requests.post('https://api.ciscospark.com/v1/messages', headers=HEADERS, json=payload)
    if not resp or not resp.ok:
        print(resp)
        pprint(resp.json())


def roomList():
    req = requests.get('https://api.ciscospark.com/v1/rooms?type=group', headers=HEADERS)
    js = req.json()
    return js['items']


def list_rooms(personId):
    rooms = roomList()
    names = [room['title'] for room in rooms]

    # TODO: format into prompt
    prompt = json.dumps(names)

    bullet_list = "\n".join("* " + n for n in names)
    markdown = "Here are the rooms that LetMeInBot can let you in to:\n" \
               "{}\n\n" \
               "Use 'join \<room name\>' to join a room.".format(bullet_list)

    send(personId, markdown)


def create_membership(personId, roomId):
    payload = {'personId': personId, 'roomId': roomId}
    r = requests.post('https://api.ciscospark.com/v1/memberships', headers=HEADERS, json=payload)
    debug(creation=r.json(), headers=dict(r.headers))


def join_room(personId, roomTitle):
    debug("joining room '{}'".format(roomTitle))
    rooms = roomList()
    ids = [room['id'] for room in rooms if roomTitle in room['title']]
    for id in ids:
        create_membership(personId, id)


def show_help(context_msg):
    respond(context_msg, """
Hi, I'm `LetMeInBot(beta)`, I'm new here!  
Webex Teams doesn't let you re-enter rooms you leave.  
I do.  
If you invite me to a room, I will let you (or anyone!) into that room if they ask!  
I respond to the following commands:
* list - I will tell you which rooms I can let you in to
* join \\<name\\> - I will you into any rooms with that name
* help - I print this message again

I don't have a good trust model yet, so I let absolutely anyone into your room!  
Please don't add me to sensitive rooms :(""")


def lambda_handler(event, context):
    debug_settings['method'] = print
    if 'data' not in event:
        debug(event=event)
    if 'id' not in event['data']:
        debug(**{"event['data']": event['data']})
    message_id = event['data']['id']

    HEADERS['Authorization'] = environ['Authorization']
    print(HEADERS)
    message = requests.get('https://api.ciscospark.com/v1/messages/{}'.format(message_id), headers=HEADERS)

    body = message.json()  # ['id']

    if body['personId'] == MYSELF:
        debug(simple="Received notification that we posted a message")
        return {
            'statusCode': 200,
            'body': body
        }

    text = body['text']
    if "debug" in text or 'debug' in event:  # string contains, or key exists
        print("found debug flag")
        debug_settings['method'] = debug_to_me

    debug(event=event, message_itself=body)

    if 'help' in text:
        show_help(body)
    elif 'join ' in text:
        needle = 'join '
        pos = text.find(needle)
        join_room(body['personId'], text[pos + len(needle):])
    elif 'list' in text:
        list_rooms(body['personId'])

    return {
        'statusCode': 200,
        'body': body
    }
