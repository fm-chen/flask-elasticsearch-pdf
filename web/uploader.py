import cbor2
import requests
import datetime
import pandas as pd

# base_url = "http://localhost:9200"
# base_url = "elasticsearch:9200"


def pdf_loader(file, filename, filetype, desc):
    ct = datetime.datetime.today().date()
    headers = {'content-type': 'application/cbor'}
    index = 'my-index-file'
    _id = filename
    index_time = str(ct)

    # url = base_url + '/%s/_doc/%s?pipeline=cbor-attachment' % (index, _id)
    # url = 'http://localhost:9200/%s/_doc/%s?pipeline=cbor-attachment' % (index, _id)
    # url = 'https://infolab.ece.udel.edu:9200/%s/_doc/%s?pipeline=cbor-attachment' % (index, _id)
    url = 'http://23.92.20.76:9200/%s/_doc/%s?pipeline=cbor-attachment' % (index, _id)

    content = ''
    content1 = ''
    if filetype == 'pdf':
        content = file.read()
    if filetype == 'excel':
        df = pd.read_csv(file, encoding='utf8')
        content1 = df.columns.to_list()

    try:
        doc = {
            'data': content,
            'filename': filename,
            'desc': desc,
            'index_time': index_time,
            'file_type': filetype,
            'reg_data': content1,
        }
        r = requests.put(
            url,
            data=cbor2.dumps(doc),
            headers=headers
        )
        print(r.json)
    except Exception as e:
        print(e)
