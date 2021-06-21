import elasticsearch
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import os
from uploader import pdf_loader

UPLOAD_FOLDER = './pdf'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'u of del'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def welcome():
    return "welcome"


@app.route("/pdf", methods=["GET", "POST"])
def pdf():
    q = None
    numresults = None
    final_result = None

    if request.method == "POST":
        q = request.form["searchTerm"]

        es = elasticsearch.Elasticsearch(['elasticsearch'])

        numResults = 99

        results = es.search(index="documents",
                            body={
                                "size": numResults,
                                "query": {
                                    "match": {
                                        "text": {
                                            "query": q,
                                        }
                                    }
                                }
                            })

        final_result = []
        numresults = len(final_result)

        for hit in results['hits']['hits']:
            text = hit["_source"]["text"]
            line_num = hit["_source"]["line_num"]
            score = hit["_score"]
            page_num = hit["_source"]["page_num"]
            file_name = hit["_source"]["file_name"]
            temp = dict()
            temp["text"] = text
            temp["line_num"] = line_num
            temp["page_num"] = page_num
            temp["file_name"] = file_name
            temp["score"] = score
            final_result.append(temp)

        done = set()
        result = []
        for d in final_result:
            if d['file_name'] not in done:
                done.add(d['file_name'])  # note it down for further iterations
                result.append(d)

    # return json.dumps(final_result)
    return render_template('index.html', query=q, numresults=numresults, results=final_result)


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
            # filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try:
                pdf_loader(file)
                # print(file)
                flash("File uploaded successfully")
            except:
                flash("Error!")
        else:
            flash("File not supported")

    return render_template('add.html')


if __name__ == "__main__":
    app.run(debug=True)
