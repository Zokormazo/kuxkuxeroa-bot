import sys
import time
import os
import telepot
import telepot.helper
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from pymongo import MongoClient

token = os.environ.get("KUXKUXEROA_TELEGRAM_API_TOKEN", None)
if token == None:
    print("token is mandatory")
    sys.exit(1)

mongodb_uri = os.environ.get("KUXKUXEROA_MONGODB_URI", None)
if mongodb_uri == None:
    print("mongodb uri is mandatory")
    sys.exit(1)

client = MongoClient(mongodb_uri)
db = client.get_default_database()

messages = db.messages

class MessageLogger(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageLogger, self).__init__(*args, **kwargs)

    def on_chat_message(self, msg):
        if 'edit_date' in msg:
            key = { 'message_id': msg['message_id'], 'chat.id': msg['chat']['id']}
            data = { '$set': { 'edit_date': msg['edit_date'], 'text': msg['text']}}
            messages.update(key, data)
        else:
            messages.insert_one(msg)

bot = telepot.DelegatorBot(token, [
    pave_event_space()(
        per_chat_id(types=['supergroup', 'group', 'channel']), create_open, MessageLogger, timeout=3)
])

MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)
