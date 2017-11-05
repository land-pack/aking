# aking


Prepare
========


    ./ready.sh
    pip install -r requirements.txt
    python manager.py


Test
======

Open your websocket client , like (chrome extends)
put the url (127.0.0.1:9777/ws?uid=1002925)
And then send a message to the server:

    {
        "msg_type": "user_join",
        "msg_id": "123",
        "data":{
           "uid":1002925
        }
    }

And if join successful 

    {
        "msg_id": "124",
        "data": {
            
        },
        "msg_type": "ack_user_join"
    }

And your member will get something like:


