import os
import requests
import shutil
import json

Url = "https://nextdoornikki.com/hosted/gal/whitesheer2/images/1.jpg"
Path = "c:\\temp\\pics"
message = {"img": "https://nextdoornikki.com/hosted/gal/whitesheer2/images/1.jpg", "path": "c:\\temp\\pics"}

data = {}
data['Url'] = "https://nextdoornikki.com/hosted/gal/whitesheer2/images/1.jpg"
data['Path'] = "c:\\temp\\pics"
message = json.dumps(data)
message = json.loads(message)

print("saving...")
# Image
res = requests.get(message["Url"], stream = True)

# create folder if it doesn't already exist
if not os.path.exists(message["Path"]):
    print( "creating path")
    os.makedirs(message["Path"])

# determine save file name and full path
print("calculating file name/path")
filename = message["Url"].split('/')[-1]
fullsavepath = os.path.join(message["Path"],filename)

# Save Image
if res.status_code == 200:
    print(f"filepath {fullsavepath}")
    with open(fullsavepath,'wb') as f:
        shutil.copyfileobj(res.raw, f)
    print('Image sucessfully Downloaded: ',fullsavepath)
else:
    print('Image Couldn\'t be retrieved')
                                