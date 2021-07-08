import glob
import os
from uploader import pdf_loader
import requests

url = "http://localhost:9200/_ingest/pipeline/cbor-attachment"


headers = {'content-type': 'application/json'}

data = '{"description": "Extract attachment information", "processors": [{"attachment": {"field": "data"}}]}'


r = requests.put(
    url,
    data=data,
    headers=headers
)


os.chdir("./pdf")
for file in glob.glob("*.pdf"):
    with open(file, 'rb') as f:
        pdf_loader(f, file)

print('done')


