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
                eachline = eachline.strip()
                if len(eachline) == 0:
                    is_message = True
                if is_message and len(eachline) > 0 and ('@' in eachline.split()[0].strip()):
                    new_user_list.append(eachline.split()[0].strip())
            fp.close()
            for eachline in new_user_list: np.write(eachline + '\n')
            remove(file_name)
            np.close()

def confirm_order(email, status, order_list = False): #status is failed (for bad formatting) or success or request or not_listed
    FROM = 'customer_service@mywebsite.com'
    TO = email
    BODY_success = "\r\nOrder completed! See you on Wednesday between 12 and 3pm\r\n\r\nThe Food Coop Team\r\n(automated email. \
write to customer_service@mywebsite.com if you're having trouble)\r\n"
    SUBJECT_success = "Food Coop: order completed"
    BODY_failed = "\r\nwe couldn't complete your order! computer sais: 'you entered order in the wrong format'\
\r\nIf you think its wrong please email me at customer_service@mywebsite.com\r\n"
    SUBJECT_failed = "Food Coop couldn't complete your order this time"
    BODY_failed_helper = "\r\nthe following couldnt process their food coop order: " + email + "\r\n"
    SUBJECT_failed_helper = "\r\n food coop order failed for " + email
    BODY_request = order_list
    SUBJECT_request = "food coop order list"
    BODY_not_listed = "\r\nFood Coop couldn't complete your order because you are not on our Food Coop members list!\r\n\
To get on the list just speak to one of the Food Coop team by emailing customer_service@mywebsite.com\r\n"
    SUBJECT_not_listed = "Food Coop - you need to register first"

    if status == 'success':
        message = 'From: ' + FROM + '\r\nTo: ' + TO + '\r\nSubject: ' + SUBJECT_success + '\r\n\r\n' + BODY_success
    elif status == 'failed':
        message = 'From: ' + FROM + '\r\nTo: ' + TO + '\r\nSubject: ' + SUBJECT_failed + '\r\n\r\n' + BODY_failed
        message_helper = 'From: ' + FROM + '\r\nTo: ' + TO + '\r\nSubject: ' \
+ SUBJECT_failed_helper + '\r\n\r\n' + BODY_failed_helper
    elif status == 'request':
        message = 'From: ' + FROM + '\r\nTo: ' + TO + '\r\nSubject: ' + SUBJECT_request + '\r\n\r\n' + BODY_request
    elif status == 'not_listed':
        message = 'From: ' + FROM + '\r\nTo: ' + TO + '\r\nSubject: ' + SUBJECT_not_listed + '\r\n\r\n' + BODY_not_listed

    SMTPSERVER = 'localhost'

    sendserver = smtp(SMTPSERVER)
    errors = sendserver.sendmail(FROM, TO, message)

    if status =='failed':
        errors_helper = sendserver.sendmail(FROM, 'customer_service@mywebsite.com', message_helper)
        if len(errors_helper) != 0:
            fp = open('errors', 'a')
            for eachline in errors:
                fp.write(eachline+'\n')
            fp.write('\n\n')
            fp.close()

