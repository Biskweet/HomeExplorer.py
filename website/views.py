import datetime
import os
import random
import string

from flask import Flask, render_template, redirect, request, send_file, session, url_for

from website import utils

sessions = []


app = Flask(__name__)
app.config.from_object("config")
utils.autodelete_sessions(sessions)

print("================== pass", os.environ.get("password"))


@app.route("/")
def root():
    return redirect(url_for("login"))

@app.route("/unauthorized/")
def unauthorized():
    return render_template("unauthorized.html", message="Sorry, an error occured.")


@app.route("/login/", methods=["GET", "POST"])
def login():
    # if utils.session_is_valid(request.cookies.get("session-token"), sessions):
    #     return redirect(url_for("files", directory="Desktop"))

    if request.method == "POST":
        password = request.form.get("password")

        if password != '1234':
            return render_template("unauthorized.html", message="Sorry, but the password is incorrect.")

        else:
            session_token = ''.join([random.choice(string.printable) for _ in range(32)])

            # 1h session duration
            session_expire = datetime.datetime.now() + datetime.timedelta(hours=1)

            sessions.append(utils.Session(session_expire, session_token))

            response = redirect(url_for("files", directory="Desktop"))
            response.set_cookie("session-token", session_token)

            return response

    return render_template("login.html")


@app.route("/files/<path:directory>")
def files(directory):
    directory = directory.replace("..", ".")  # Securing the path

    # token = session.get("session-token")
    # if not utils.session_is_valid(token, sessions):
    #     return render_template("unauthorized.html", message="Sorry but your session is invalid.")

    files, folders = utils.get_dir_content(utils.STORAGE_DIR + directory)

    return render_template("files.html",
                           title=directory.strip('/').rsplit('/')[-1],
                           len_folders=len(folders), folders=folders,
                           len_files=len(files), files=files)


if __name__ == "__main__":
    app.run()
