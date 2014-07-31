#send new members a welcome email
from smtplib import SMTP as smtp
from time import sleep


def welcome_bot():
 fp = open('busters','r')
 np = open('welcomed','a')
 for eachline in fp:
    if not is_in(eachline.strip()):
        send_welcome(eachline.strip())
        np.write(eachline.strip()+'\n')
 fp.close()
 np.close()

def is_in(email):
    is_in_welcomed = False
    mp = open('welcomed','r')
    for eachline in mp:
        if eachline.strip() == email: is_in_welcomed = True
    return is_in_welcomed
    mp.close()

def send_welcome(email):
    FROM = 'customer_services@my_domain.com'
    TO = email
    BODY_success = "\r\nThankyou for joining the Food Coop! To make an order go to www.my_website.com\r\n\
Pick the items you want and copy-paste the code to customer_services@my_domain.com with the \
subject line of the email set to 'food' (all lower-case letters and without the quotation marks)\r\n\r\n\
If your order is successful you'll receive a confirmation email from the Food Coop within 5 minutes \
of you sending in your order\r\n\r\n\
Pickup is on Wednesday on Mars (on the first floor of the Food Department. We will put signs up \
on the day) from 12 to 3pm. See you there!\r\n\r\nThe Food Coop Team\r\n(automated email. \
write to customer_services@my_domain.com if you're having trouble)\r\n"
    SUBJECT_success = "Food Coop membership"
    message = 'From: ' + FROM + '\r\nTo: ' + TO + '\r\nSubject: ' + SUBJECT_success + '\r\n\r\n' + BODY_success
    SMTPSERVER = 'localhost'

    sendserver = smtp(SMTPSERVER)
    errors = sendserver.sendmail(FROM, TO, message)
    sendserver.quit()

    if len(errors) != 0:
        lp = open('welcome_errors', 'a')
        for eachline in errors:
            lp.write(eachline+'\n')
        lp.write('\n\n')
        lp.close()

while True:
    sleep(10)
    welcome_bot()
