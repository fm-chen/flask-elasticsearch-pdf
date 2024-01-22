
import math
import os
from flask_cors import CORS
from flask import send_file

from elasticsearch import Elasticsearch
from flask import Flask, flash, request, redirect, render_template, url_for, session
from werkzeug.utils import secure_filename
from uploader import pdf_loader

from forms import UploadForm, SearchForm, LoginForm, addLoginForm
from flask_bootstrap import Bootstrap

from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token


UPLOAD_FOLDER = './uploadedfiles'
ALLOWED_EXTENSIONS = {'pdf'}
ALLOWED_EXTENSIONS1 = {'csv'}

app = Flask(__name__, static_url_path='')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'u of del infolab'
Bootstrap(app)



oauth = OAuth(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

numResults = 10

es_host = os.environ['ELASTICSEARCH_URL']

# es = Elasticsearch("http://localhost:9201")

es = Elasticsearch([es_host])

logged_in = False

credentials = {"username": "password", "example1": "example1"}

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


#@app.route("/", methods=["GET"])
#def welcome():
#    return "welcome to pdf search"

@app.route('/')
def index():
    return render_template('google_login.html')

@app.route("/login", methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    global credentials
    global logged_in

    if form.validate_on_submit():
        if form.username.data in credentials:
            if form.password.data == credentials[form.username.data]:
                logged_in = True
                return redirect('/search')
            else:
                flash("Incorrect password")
        else:
            flash("Incorrect username")

    return render_template(
        "login.html",
        form=form)

@app.route("/add_login", methods=['GET', 'POST'])
def addLogin():
    form = addLoginForm()
    global credentials

    if form.validate_on_submit():
        if form.username.data in credentials:
            flash("Username already exists")
        else:
            credentials[form.username.data] = form.password.data
            return redirect('/login')

    return render_template(
        "new_login.html",
        form=form)

@app.route("/search", methods=["GET", "POST"])
def search():
    global logged_in
    if not logged_in:
        return redirect(url_for('index'))

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
    #global logged_in
    #if not logged_in:
    #    return redirect('/login')

    form = UploadForm()
    if form.validate_on_submit():
        file_type = form.options.data
        # handle the file
        for f in form.files.data:
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

@app.route('/google/')
def google():

    GOOGLE_CLIENT_ID = '434419428278-p390gt30vrks5gsfanmsf70iqfeibh9l.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = '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'

    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True, _scheme='https')
    print(redirect_uri)
    session['nonce'] = generate_token()
    return oauth.google.authorize_redirect(redirect_uri, nonce=session['nonce'])

@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token, nonce=session['nonce'])
    session['user'] = user
    print(" Google User ", user)
    global logged_in
    logged_in = True
    return redirect(url_for('search'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    # app.run(debug=True, port=5001)
    app.run(ssl_context='adhoc')