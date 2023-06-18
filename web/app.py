import math
import os
from flask_cors import CORS
from flask import send_file

from elasticsearch import Elasticsearch
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from uploader import pdf_loader

from forms import UploadForm, SearchForm
from flask_bootstrap import Bootstrap

UPLOAD_FOLDER = './uploadedfiles'
ALLOWED_EXTENSIONS = {'pdf'}
ALLOWED_EXTENSIONS1 = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'u of del'
Bootstrap(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

numResults = 10

es_host = os.environ['ELASTICSEARCH_URL']

es = Elasticsearch([es_host])
# es = Elasticsearch(['http://23.92.20.76'])
# es = Elasticsearch()


def if_pdf(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def if_csv(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS1


def search_q(query, page):

    results = es.search(index="my-index-file",
                        body={
                            "from": numResults * (page - 1),
                            "size": numResults,
                            "query": {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["filename", "desc"]
                                }
                            }
                        })
    return results


def search_by_c(query, page):

    results = es.search(index="my-index-file",
                        body={
                            "from": numResults * (page - 1),
                            "size": numResults,
                            "query": {
                                "bool": {
                                    "must": {
                                        "match": {"attachment.content": {"query": query}}
                                    },
                                    "filter": {
                                        "term": {
                                            "file_type": "pdf"
                                        }
                                    }
                                }
                            },
                            "highlight": {
                                "fields": {
                                    "attachment.content": {}
                                }
                            }
                        })
    return results


def search_by_f(query, page):

    results = es.search(index="my-index-file",
                        body={
                            "from": numResults * (page - 1),
                            "size": numResults,
                            "query": {
                                "bool": {
                                    "must": {
                                        "match": {"reg_data": {"query": query}}
                                    },
                                    "filter": {
                                        "term": {
                                            "file_type": "excel"
                                        }
                                    }
                                }
                            },
                            "highlight": {
                                "fields": {
                                    "attachment.content": {}
                                }
                            }
                        })
    return results


def search_by_solr(query, page):

    results = es.search(index="news_es",
                        body={
                            "from": numResults * (page - 1),
                            "size": numResults,
                            "query": {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["Call_Number", "Keywords"]
                                }
                            }
                        })
    return results


@app.route("/", methods=["GET"])
def welcome():
    return "welcome to pdf search"


@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    q = request.args.get("q", "")
    option = request.args.get("option", "")

    if form.validate_on_submit():
        q = form.search.data
        option = form.options.data

    page = int(request.args.get("page", 1))

    if option == 'opt1':
        res = search_by_c(q, page)
    elif option == 'opt2':
        res = search_by_f(q, page)
    elif option == 'opt3':
        res = search_by_solr(q, page)
    else:
        res = search_q(q, page)

    final_result = []
    total = res['hits']['total']['value']

    for hit in res['hits']['hits']:
        base64 = hit["_source"].get('data')
        text = hit["_source"]['attachment'].get("content")
        desc = hit["_source"].get("desc")
        # desc = hit["_source"].get("Call_Number")
        score = hit["_score"]
        file_name = hit["_source"]['filename']
        # file_name = hit["_source"]['Call_Number']
        if option == 'opt1':
            snippets = hit['highlight']['attachment.content']
            snippets = [sub.replace("<em>", '<b>').replace("</em>", "</b>") for sub in snippets]
        if option == 'opt2':
            c_names = hit["_source"]['reg_data']

        temp = dict()
        temp["text"] = text
        temp["desc"] = desc
        temp["score"] = score
        temp["file_name"] = file_name
        temp["base64"] = base64
        if option == 'opt1':
            temp["snippets"] = snippets
        if option == 'opt2':
            temp["c_names"] = c_names
        final_result.append(temp)

    pagination = dict()
    pagination["page_num"] = math.ceil(total / 10)
    pagination["prev_num"] = page - 1
    pagination["next_num"] = page + 1

    return render_template('index.html',
                           query=q,
                           results=final_result,
                           numresults=total,
                           page=page,
                           pagination=pagination,
                           form=form,
                           option=option
                           )


@app.route('/download/<path:filename>')
def downloadFile(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(path, as_attachment=True)


@app.route("/add", methods=["GET", "POST"])
def upload_file():
    """Standard `contact` form."""
    form = UploadForm()
    if form.validate_on_submit():
        file_type = form.options.data
        # handle the file
        f = form.file.data
        filename = secure_filename(f.filename)
        # get file description
        desc = form.desc.data
        # print(f.read())

        if file_type == 'pdf':
            if not if_pdf(filename):
                flash('wrong file type')
            else:
                try:
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    f.seek(0)
                    pdf_loader(f, filename, file_type, desc)
                    flash("File uploaded successfully")
                except:
                    flash("Error!")

        elif file_type == 'excel':
            if not if_csv(filename):
                flash('wrong file type')
            else:
                try:
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    f.seek(0)
                    pdf_loader(f, filename, file_type, desc)
                    flash("File uploaded successfully")
                except:
                    flash("Error!")

        else:
            try:
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                f.seek(0)
                pdf_loader(f, filename, file_type, desc)
                flash("File uploaded successfully")
            except:
                flash("Error!")

    return render_template(
        "add.html",
        form=form)


if __name__ == "__main__":
    # app.run(debug=True, port=5001)
    app.run(debug=True)
