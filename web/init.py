import glob
import os
from uploader import pdf_loader
import requests

# base_url = "http://23.92.20.76:9200"
# base_url = "https://infolab.ece.udel.edu:9200"
base_url = "http://localhost:9200"
url_pip = base_url + "/_ingest/pipeline/cbor-attachment"
url_index = base_url + "/my-index-file/"

# url = "http://elasticsearch:9200/_ingest/pipeline/cbor-attachment"
# url = "https://infolab.ece.udel.edu:9200/_ingest/pipeline/cbor-attachment"

headers = {'content-type': 'application/json'}

params = (
    ('pretty', 'true'),
)

data = '{"description": "Extract attachment information", "processors": [{"attachment": {"field": "data"}}]}'

# init cbor pipeline
r = requests.put(
    url_pip,
    data=data,
    headers=headers
)

print(r.text)

# init filename tokenizer
json_data = {
    'settings': {
        'analysis': {
            'analyzer': {
                'filename_search': {
                    'tokenizer': 'filename',
                    'filter': [
                        'lowercase',
                    ],
                },
                'filename_index': {
                    'tokenizer': 'filename',
                    'filter': [
                        'lowercase',
                        'edge_ngram',
                    ],
                },
            },
            'tokenizer': {
                'filename': {
                    'pattern': '[^\\p{L}\\d]+',
                    'type': 'pattern',
                },
            },
            'filter': {
                'edge_ngram': {
                    'side': 'front',
                    'max_gram': 20,
                    'min_gram': 1,
                    'type': 'edge_ngram',
                },
            },
        },
    },
    'mappings': {
        'properties': {
            'filename': {
                'type': 'text',
                'search_analyzer': 'filename_search',
                'analyzer': 'filename_index',
            },
        },
    },
}

r1 = requests.put(
    url_index,
    headers=headers,
    params=params,
    json=json_data)
print(r1.text)

'''
# init files
os.chdir("./pdf")
for file in glob.glob("*.pdf"):
    with open(file, 'rb') as f:
        pdf_loader(f, file)
'''


print('done')


