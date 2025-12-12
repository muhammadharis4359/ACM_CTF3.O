from flask import Flask, request, redirect, render_template
import secrets
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Dummy database
users = {
    "admin@example.com": {"password": "admin123"},
    "user@example.com": {"password": "user123"}
}

reset_tokens = {}


# ---------------- SENDGRID FUNCTION ----------------
def send_reset_email(to_email, reset_link):
    message = Mail(
        from_email=os.getenv("FROM_EMAIL", "no-reply@ctf-challenge.com"),
        to_emails=to_email,
        subject="Password Reset Request",
        html_content=f"""
        <p>You requested a password reset.</p>
        <p><strong>Reset Link:</strong></p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        """
    )

    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sg.send(message)
        print("SENDGRID RESPONSE:", response.status_code)
    except Exception as e:
        print("SendGrid Error:", e)


# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email in users and users[email]["password"] == password:
            return f"<h1>Welcome {email} — Login Successful!</h1>"

        return "<h3>Invalid Credentials</h3>"

    return render_template("login.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":

        # Default email — players can override via Burp Suite
        email = "default@example.com"

        if "email" in request.form:
            email = request.form.get("email")

        token = secrets.token_hex(16)
        reset_tokens[token] = email

        reset_link = f"https://{request.host}/reset/{token}"

        send_reset_email(email, reset_link)

        return "<h3>If the email exists, a reset link has been sent.</h3>"

    return render_template("forgot.html")


@app.route("/reset/<token>", methods=["GET", "POST"])
def reset(token):
    if token not in reset_tokens:
        return "<h3>Invalid or Expired Token</h3>"

    email = reset_tokens[token]

    if request.method == "POST":
        newpass = request.form.get("newpass")
        users[email] = {"password": newpass}
        del reset_tokens[token]

        return f"<h3>Password changed for {email}. <a href='/'>Login</a></h3>"

    return render_template("reset.html")


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
