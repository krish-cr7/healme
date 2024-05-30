from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, session, request
import razorpay
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


# Razorpay Configuration
razorpay_client = razorpay.Client(auth=(os.environ.get('RAZORPAY_KEY_ID'), os.environ.get('RAZORPAY_KEY_SECRET')))

@app.before_first_request
def before_first_request():
    session['screenshot_uploaded'] = False
    session['logged_in'] = False

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # if request.method == 'POST':
    #     # Assuming you have a simple form with username and password
    #     if request.form['username'] == 'your_username' and request.form['password'] == 'your_password':
    #         session['logged_in'] = True
    #         return redirect(url_for('form'))
    #     else:
    #         return "Invalid credentials. Please try again."
    return render_template('form.html')

# @app.route('/logout')
# def logout():
#     session['logged_in'] = False
#     session['screenshot_uploaded'] = False
#     return redirect(url_for('landing_page'))

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')
@app.route('/contactus')
def contactus():
    return render_template('contactus.html')
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')
@app.route('/refund')
def refund():
    return render_template('refund.html')
@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    session['screenshot_uploaded'] = True
    return redirect(url_for('schedule'))

@app.route('/pay', methods=["GET", "POST"])
def pay():
    if request.form.get("amount") != "":
        # amount=request.form.get("amt")
        razorpay_key = os.environ.get('RAZORPAY_KEY_ID')
        amount = 50000
        data = { "amount": 50000, "currency": "INR", "receipt": "order_rcptid_11" }
        payment = razorpay_client.order.create(data=data)
        pdata=[amount, payment["id"]]
        return render_template("index.html", pdata=pdata, razorpay_key=razorpay_key)
    return redirect("/form")

@app.route('/schedule')
def schedule():
    # if not session.get('logged_in'):
    #     return redirect(url_for('login'))
    if not session.get('screenshot_uploaded'):
        return "Unauthorized: Please upload a screenshot first", 401
    return render_template("schedule_meeting.html")

# if __name__ == '__main__':
#     app.run(debug=True)
