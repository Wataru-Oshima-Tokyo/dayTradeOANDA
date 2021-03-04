import smtplib
from email.mime.text import MIMEText
from datetime import datetime

my_addr = "bigisland.business@gmail.com"
my_pass = "vtimcmvrnktbxyhp"
# メッセージの作成
def create_message(from_addr, to_addr, subject, body_txt):
    msg = MIMEText(body_txt)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    return msg

# メールの送信
def send_mail(msg):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(my_addr, my_pass)
        server.send_message(msg)

def main(rateofwintext, titletext):
    now = datetime.now()
    todays_date = str(now.strftime("%Y年%m月%d日%H:%M:%S ")) 
    title = todays_date + str(titletext)
    showResult = rateofwintext
    if showResult:
        msg = create_message(my_addr, my_addr, title, showResult)
        send_mail(msg)
        print("successfully emailed to the user")
