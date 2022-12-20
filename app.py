from flask import Flask, render_template


app = Flask(__name__)
app_name = "Plagiarism Checker"

@app.route("/")
def dashboard():
    return render_template(
        'page/dashboard.html', 
        app_name=app_name, 
        page='dashboard'
    )


@app.route("/scan", methods=["GET", "POST"])
def scan():
    return render_template(
        'page/scan.html', 
        app_name=app_name, 
        page='scan'
    )


@app.route("/result")
def result():
    return render_template(
        'page/result.html', 
        app_name=app_name, 
        page='result'
    )

if __name__ == "__main__":
    app.run(debug=1)