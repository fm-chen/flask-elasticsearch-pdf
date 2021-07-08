import math
import elasticsearch
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from uploader import pdf_loader

UPLOAD_FOLDER = './pdf'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'u of del'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def search_q(query, page):
    es = elasticsearch.Elasticsearch(['elasticsearch'])
    
    # es = elasticsearch.Elasticsearch()

    numResults = 10

    results = es.search(index="my-index-07",
                        body={
                            "from": numResults * (page - 1),
                            "size": numResults,
                            "query": {
                                "match": {
                                    "attachment.content": {
                                        "query": query,
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


@app.route("/", methods=["GET"])
def welcome():
    return "welcome to pdf search"


@app.route("/search", methods=["GET", "POST"])
def search():
    q = request.args.get("q", "")

    page = int(request.args.get("page", 1))
    res = search_q(q, page)

    final_result = []
    total = res['hits']['total']['value']

    for hit in res['hits']['hits']:
        base64 = hit["_source"].get('data')
        text = hit["_source"]['attachment'].get("content")
        date = hit["_source"]['attachment'].get("date")
        score = hit["_score"]
        file_name = hit["_source"]['file_name']
        snippets = hit['highlight']['attachment.content']
        snippets = [sub.replace("<em>", '<b>').replace("</em>", "</b>") for sub in snippets]

        temp = dict()
        temp["text"] = text
        temp["date"] = date
        temp["score"] = score
        temp["file_name"] = file_name
        temp["base64"] = base64
        temp["snippets"] = snippets
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
                           pagination=pagination
                           )


@app.route('/add', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try:
                # print(file.read())
                pdf_loader(file, filename)
                # print(file)
                flash("File uploaded successfully")
            except:
                flash("Error!")
        else:
            flash("File not supported")

    return render_template('add.html')


if __name__ == "__main__":
    app.run()
