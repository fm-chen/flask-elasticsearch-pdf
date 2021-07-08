import cbor2
import requests
import datetime


def pdf_loader(pdf_file, filename):
    ct = datetime.datetime.today().date()
    headers = {'content-type': 'application/cbor'}
    index = 'my-index-07'
    _id = filename + "_" + str(ct)
    # url = 'http://localhost:9200/%s/_doc/%s?pipeline=cbor-attachment' % (index, _id)
    # url = 'elasticsearch:9200/%s/_doc/%s?pipeline=cbor-attachment' % (index, _id)
    url = 'http://147.182.174.38:9200/%s/_doc/%s?pipeline=cbor-attachment' % (index, _id)
    try:
        doc = {
            'data': pdf_file.read(),
            'file_name': filename,
        }
        r = requests.put(
            url,
            data=cbor2.dumps(doc),
            headers=headers
        )
        print(r.text)
    except Exception as e:
        print(e)
