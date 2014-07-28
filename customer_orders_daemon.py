from smtplib import SMTP as smtp
from os import listdir
from os import remove
from time import sleep

def is_listed(email,status):        #status is 'admin' or 'user'
    is_a_member = False
    if status == 'user': file_name = '/home/my_username/coop/customers'
    elif status == 'admin': file_name = '/home/my_username/coop/admin'
    fp = open(file_name, 'r')
    for eachline in fp:
        if email == eachline.strip():
            is_a_member = True
    fp.close()
    return is_a_member

def email_re(list_of_words):        #email regular expression
    email='NO'
    for eachword in list_of_words:
        eachword.strip()
        if eachword.startswith('<'): email = eachword.replace('<','').replace('>','')
        elif eachword.find('@') != -1: email = eachword
    return email

#returns alist of the orders if format is order-like, otherwise returns an empty list
def is_order_format(order_list):
    formatted = []
    for eachline in order_list:
        eachline = eachline.split()
        if len(eachline) == 2 and eachline[0].strip().isdigit():
            formatted.append(eachline[0].strip() + ' ' + eachline[1].strip())
    return formatted


def read_emails():                  #does what it sais on the tin
    order = False   #is a food order
    request = False #is admin request for order list
    new_user = False #add a new member
    islisted = False
    islisted_admin = False
    email = ''
    order_list = []
    new_user_list = []
    for eachfile in listdir('/home/my_username/Maildir/new'):
        file_name = '/home/my_username/Maildir/new/' + eachfile
        fp = open(file_name, 'r')
        for eachline in fp:
          if len(eachline.split()) >= 2:
            eachline = eachline.split()
            if eachline[0].strip() == 'Subject:' and eachline[1].strip().lower() == 'request': request = True
            if eachline[0].strip() == 'Subject:' and eachline[1].strip().lower() == 'new_user': new_user = True
            if eachline[0].strip() == 'Subject:' and eachline[1].strip().lower() == 'food': order = True
            if eachline[0].strip() == 'From:' and is_listed(email_re(eachline), 'user'):
                islisted = True
                email = email_re(eachline)
            if eachline[0].strip() == 'From:' and is_listed(email_re(eachline), 'admin'):
                islisted_admin = True
                email = email_re(eachline)
            elif eachline[0].strip() == 'From:': email = email_re(eachline) #email not listed so will send them an email about coop

        if order and islisted:
            is_message = False
            fp.close()
            fp = open(file_name,'r')
            for eachline in fp:
                if len(eachline.strip()) == 0:
                    is_message = True
                if is_message and len(eachline.strip()) > 0:
                    order_list.append(eachline.strip())
            fp.close()
            if is_order_format(order_list):
                order_list = is_order_format(order_list)
                fp = open('/home/my_username/coop/orders','a')
                fp.write(email + '\n')
                for eachline in order_list:
                    if eachline: fp.write(eachline + '\n')
                fp.write('\n\n')
                fp.close()

                confirm_order(email, 'success')
                remove(file_name)

            else:
                confirm_order(email, 'failed')
                remove(file_name)

        elif order and not islisted:
            confirm_order(email, 'not_listed')
            remove(file_name)

        elif request and islisted_admin:  #request order list
            message_body = '\r\n'
            fp = open('/home/my_username/coop/orders', 'r')
            for eachline in fp:
                message_body = message_body + eachline.strip() + '\r\n'
            confirm_order(email, 'request', message_body)
            remove(file_name)
            fp.close()

        elif new_user and islisted_admin: #add a new user
            np = open('members','a')
            is_message = False
            fp.seek(0)
            for eachline in fp:
