from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, session, request
from flask_oauthlib.client import OAuth
import razorpay
import os
import secrets

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=os.environ.get('GOOGLE_CONSUMER_KEY'),
    consumer_secret=os.environ.get('GOOGLE_CONSUMER_SECRET'),
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Razorpay Configuration
razorpay_client = razorpay.Client(auth=(os.environ.get('RAZORPAY_KEY_ID'), os.environ.get('RAZORPAY_KEY_SECRET')))

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('landing_page'))

@app.route('/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason={}, error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    return redirect(url_for('form'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

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

@app.route('/success', methods=["POST"])
def success():
    pid = request.form.get("razorpay_payment_id")
    ordid = request.form.get("razorpay_order_id")
    sign = request.form.get("razorpay_signature")
    print(f"The payment id : {pid}, order id : {ordid} and signature : {sign}")
    params = {
        'razorpay_order_id': ordid,
        'razorpay_payment_id': pid,
        'razorpay_signature': sign
    }
    final = razorpay_client.utility.verify_payment_signature(params)
    if final:
        session['payment_success'] = True
        return redirect("/schedule")
    return "Something Went Wrong Please Try Again"

@app.route('/form')
def form():
    if 'google_token' not in session:
        return redirect(url_for('login'))
    return render_template('form.html')

@app.route('/schedule')
def schedule():
    if 'google_token' not in session:
        return redirect(url_for('login'))

    if session.get('payment_success') != True:
        return "Unauthorized", 401

    return render_template('schedule_meeting.html')

# if __name__ == '__main__':
#     app.run(debug=True)
