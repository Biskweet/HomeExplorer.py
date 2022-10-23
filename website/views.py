import datetime
import os
import random
import string

# Third-party imports
from flask import Flask, render_template, redirect, request, send_file, session, url_for, abort
import dotenv

# Custom imports
from website import utils


sessions = []

app = Flask(__name__)
app.config.from_object("config")

dotenv.load_dotenv()

utils.autodelete_sessions(sessions)

BASE_DIR = os.environ.get("BASE_DIR")


@app.route("/")
def root():
    return redirect(url_for("login"))


@app.route("/unauthorized/")
def unauthorized():
    return render_template("unauthorized.html", message="Sorry, an error occured.")


@app.route("/login/", methods=["GET", "POST"])
def login():
    if utils.session_is_valid(session.get("session"), sessions):
        return redirect(url_for("files", path="storage"))

    if request.method == "POST":
        password = request.form.get("password")

        if password != os.environ.get("PASSWORD"):
            return render_template("unauthorized.html", message="Sorry, but the password is incorrect.\nPlease try again.")

        else:
            session_token = ''.join([random.choice(string.printable) for _ in range(32)])

            # 1h session duration
            session_expire = datetime.datetime.now() + datetime.timedelta(hours=4)

            sessions.append(utils.Session(session_expire, session_token))

            # Writing the session token to the user's session storage
            session["session"] = session_token

            response = redirect(url_for("files", path="storage"))

            return response

    return render_template("login.html")


@app.route("/files/")
def files_root():
    return redirect(url_for("files", path="storage"))


@app.route("/files/<path:path>")
def files(path):
    if not utils.session_is_valid(session.get("session"), sessions):
        return render_template("unauthorized.html", message="Sorry but your session is invalid or has probably expired. Please log in again.")

    path = path.replace("..", ".").replace("~", ".")  # Securing the path

    if not path.startswith("storage"):
        return redirect(url_for("files", path="storage"))


    # If the requested path is a file
    if os.path.isfile(BASE_DIR + path):
        # Send the file with preview mode if it is of previewable type
        if os.path.splitext(BASE_DIR + path)[1][1:] in utils.viewable_formats:
            return send_file(BASE_DIR + path, as_attachment=False)

        # File isn't previewable, send as attachment download only
        return send_file(BASE_DIR + path, as_attachment=True)

    # If the path provided doesn't exist
    elif not os.path.exists(BASE_DIR + path):
        return abort(404)  # Show "Not found" page


    files, folders = utils.get_dir_content(BASE_DIR + path)

    return render_template("files.html",
                           path=path, title=path.strip('/').rsplit('/')[-1],
                           len_folders=len(folders), folders=sorted(folders),
                           len_files=len(files), files=sorted(files, key=lambda file: file[0].lower()),
                           emoji_selector=utils.emoji_selector
                           )


@app.route("/resetcookie/")
def resetcookie():
    for i, s in enumerate(sessions):
        if s.token == session.get("session"):
            del sessions[i]

    return redirect(url_for("login"))


@app.errorhandler(404)
def notfound(_):
    return render_template("notfound.html")


if __name__ == "__main__":
    app.run(debug=True)
