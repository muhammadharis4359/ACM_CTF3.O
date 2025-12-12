from flask import Flask, request, redirect, render_template_string
import secrets
import smtplib
import os
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "supersecretkey"

users = {
    "admin@example.com": {"password": "admin123"},
    "user@example.com": {"password": "user123"}
}

reset_tokens = {}

# SMTP CONFIG
SMTP_EMAIL = "memon.muhammadharis11@gmail.com"
SMTP_PASSWORD = "gsci jwxr zpxo wogs"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# SEND EMAIL FUNCTION
def send_reset_email(to_email, reset_link):
    msg = MIMEText(f"Here is your password reset link:\n\n{reset_link}")
    msg["Subject"] = "Password Reset Request"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())

# ---------------- HOME PAGE ----------------
home_html = """
<h2>Login</h2>
<form method='POST'>
    Email: <input name='email'><br>
    Password: <input type='password' name='password'><br>
    <button type='submit'>Login</button>
</form>
<br>
<a href='/forgot'>Forgot Password?</a>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email in users and users[email]['password'] == password:
            return f"<h1>Welcome {email}! Login Successful.</h1>"
        return "<h3>Invalid Credentials</h3>"

    return render_template_string(home_html)

# ---------------- FORGOT PASSWORD ----------------
forgot_html = """
<h2>Forgot Password</h2>
<form method='POST'>
    <button type='submit'>Send Reset Link</button>
</form>
"""

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':

        # DEFAULT EMAIL (players can replace this via Burp)
        email = "default@example.com"

        # If user tampers the request with email=whatever@example.com
        if "email" in request.form:
            email = request.form.get('email')

        token = secrets.token_hex(16)
        reset_tokens[token] = email

        reset_link = f"http://localhost:5000/reset/{token}"

        # Send the real email
        send_reset_email(email, reset_link)

        return "<h3>If the email exists, the reset link has been sent.</h3>"

    return render_template_string(forgot_html)

# ---------------- RESET PAGE ----------------
reset_html = """
<h2>Reset Your Password</h2>
<form method='POST'>
    New Password: <input type='password' name='newpass'><br>
    <button type='submit'>Change Password</button>
</form>
"""

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    if token not in reset_tokens:
        return "<h3>Invalid or Expired Token</h3>"

    email = reset_tokens[token]

    if request.method == 'POST':
        newpass = request.form.get('newpass')

        # Allow resetting even if the email does not exist
        if email not in users:
            users[email] = {"password": newpass}
        else:
            users[email]['password'] = newpass

        del reset_tokens[token]
        return f"<h3>Password changed for {email}. <a href='/'>Login</a></h3>"

    return render_template_string(reset_html)


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
