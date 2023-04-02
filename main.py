import json
import paho.mqtt.client as mqtt
import argparse, sys
import time
from queue import Queue
import requests 
import shutil
import os

# ----- MQTT Call Back functions
def on_connect(client, userdata, flags, rc):
    # https://pypi.org/project/paho-mqtt/#on-connect
    match rc:
        case 0:
            print(f"RC = {rc}: Connection Successful.")
            client.connected_flag=True
        case 1:
            print(f"Error Connecting: RC = {rc}: Invalid Protocl Version.")
            client.loop_stop()
            sys.exit()
        case 2:
            print(f"Error Connecting: RC = {rc}: Invalid Client Identifier.")
            client.loop_stop()
            sys.exit()
        case 3:
            print(f"Error Connecting: RC = {rc}: Server Unavailable.")
            client.loop_stop()
            sys.exit()
        case 4:
            print(f"Error Connecting: RC = {rc}: Bad Username or Password.")
            client.loop_stop()
            sys.exit()
        case 5:
            print(f"Error Connecting: RC = {rc}: Not Authorized.")
            client.loop_stop()
            sys.exit()
        case _:
            print( f"Error Connection: RC = {rc}: Currently Unused code.")
            client.loop_stop()
            sys.exit()

def on_message(client, userdata, message):
    # Convert Message to Json object
    message_received=str(message.payload.decode("utf-8"))
    print(f"Recieved Message from broker: {message_received}")
    msg=json.loads(message_received)
    q.put(msg)

def on_publish(client, userdata, mid):
    print("message published." )

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    client.suback_flag=True

def on_disconnect(client, userdata, rc):
    print(f"disconnected OK: RC = {rc}")

if __name__ == '__main__':
    # process inputs
    parser=argparse.ArgumentParser()

    parser.add_argument("-b","--broker", help="MQ Broker",required=True)
    parser.add_argument("-p","--port", help="MQ Read Port",required=True)

    args=parser.parse_args()

    print("args: ")
    print(args)

    # assign to local vars
    broker=args.broker
    port=int(args.port)

    # Initialize Client 
    mqtt.Client.connected_flag=False

    client = mqtt.Client("imgsave1") 

    # callbacks
    client.on_connect=on_connect  
    client.on_publish=on_publish
    client.on_message=on_message
    client.on_subscribe=on_subscribe
    client.on_disconnect=on_disconnect

    print("Connecting to broker ",broker,": ",port)
    client.connect(broker,port) 

    client.loop_start()   

    # Wait for client to connect
    while not client.connected_flag: 
        print("Waiting for MQTT Connection.")
        time.sleep(1)
    
    client.subscribe("/imgscrape/save",qos=1)

    # Continue forever (loop_forever giving me problems)
    q=Queue()
    try:
        while True:
            time.sleep(1)

            # pulling data from message into queue
            while not q.empty():
                message = q.get()
                if message is None:
                    continue

                print(f"saving...{message}")
                # Image
                res = requests.get(message["img"], stream = True)

                print("folder exist")
                # create folder if it doesn't already exist
                if not os.path.exists(message["path"]):
                    print( "creating path")
                    os.makedirs(message["path"])

                # determine save file name and full path
                print("calculating file name/path")
                filename = message["img"].split('/')[-1]
                fullsavepath = os.path.join(message["path"],filename)

                # Save Image
                if res.status_code == 200:
                    print(f"filepath {fullsavepath}")
                    with open(fullsavepath,'wb') as f:
                        shutil.copyfileobj(res.raw, f)
                    print('Image sucessfully Downloaded: ',fullsavepath)
                else:
                    print('Image Couldn\'t be retrieved')
                                
    except:
        print("Exception: Stopping")

        client.loop_stop()
        client.disconnect()
    



