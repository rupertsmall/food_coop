from smtplib import SMTP as smtp
from os import listdir
from os import remove

def is_listed(email):
    is_a_member = False
    fp = open('/foodcoop/members', 'r')
    for eachline in fp:
        if email == eachline.strip():
            is_a_member = True
    fp.close()
    return is_a_member

def email_re(list_of_words):
    email='NO'
    for eachword in list_of_words:
        eachword.strip()
        if eachword.startswith('<'): email = eachword.replace('<','').replace('>','')
        elif eachword.find('@') != -1: email = eachword
    return email


def read_emails():
    order = False
    islisted = False
    email = ''
    order_list = []

    for eachfile in listdir('/home/my_username/Maildir/new'):
        file_name = '/home/my_username/Maildir/new/' + eachfile
        fp = open(file_name, 'r')
        for eachline in fp:
            eachline = eachline.strip() + ' 0 1'   #to stop index errors
            eachline = eachline.split()
            if eachline[0].strip() == 'Subject:' and eachline[1].strip().lower() == 'food': order = True
            if eachline[0].strip() == 'From:' and is_listed(email_re(eachline)):
                islisted = True
                email = email_re(eachline)

        is_message = False
        fp.seek(0)
        for eachline in fp:
            eachline = eachline.strip()
            if len(eachline) == 0:
                is_message = True
            if is_message:
                order_list.append(eachline)
        fp.close()
        print order_list

        if order and islisted:
            fp = open('/home/foodcoop/orders','a')
            fp.write(email + '\n')
            for eachline in order_list:
                if eachline: fp.write(eachline + '\n')
            fp.write('\n\n')
            fp.close()

            confirm_order(email)
            remove(file_name)

def confirm_order(email='my_email_address@gmail.com'):
    NAME = email
    FROM = 'customer_service@foodcoop.com'
    TO = NAME
    BODY = '\r\norder complete!\r\n'
    SMTPSERVER = 'localhost'

    message = 'From: ' + FROM + '\r\nTo: ' + TO + '\r\nSubject: Food order\r\n\r\n' + BODY

    sendserver = smtp(SMTPSERVER)
    errors = sendserver.sendmail(FROM, TO, message)
    sendserver.quit()

    if len(errors) != 0:
        fp = open('errors', 'a')
        for eachline in errors:
            fp.write(eachline+'\n')
        fp.write('\n\n')
        fp.close()

read_emails()

