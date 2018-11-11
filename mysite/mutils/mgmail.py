from mysite.settings import EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
import poplib
import email
import logging
logger = logging.getLogger('mysite.core.tests')


class MGmail():

    # https://codehandbook.org/how-to-read-email-from-gmail-using-python/
    # https://pythonprogramminglanguage.com/read-gmail-using-python/

    def __init__(self):

        self.username = 'django-test-user'
        SERVER = 'pop.gmail.com'
        # connect to server
        logging.debug('connecting to ' + SERVER)
        self.server = poplib.POP3_SSL(SERVER)
        # self.server = poplib.POP3(SERVER)

        # log in
        logging.debug('log in')
        self.server.user(EMAIL_HOST_USER)
        self.server.pass_(EMAIL_HOST_PASSWORD)

    def read_list(self):
        """

        :return:
        """
        ret = []
        resp, items, octets = self.server.list()
        sresp = resp.decode('ascii')
        # print (sresp)  # b'+OK 5 messages (56347 bytes)'
        # print (octets)  # 39
        if '+OK' in sresp:
            for one in items:
                # print(one)
                sone = one.decode('ascii')
                # print (sone)
                '''
                b'1 40218'
                b'2 13610'
                b'3 830'
                b'4 843'
                b'5 846'
                '''
                sone_list = sone.split(' ')
                # print(sone_list)
                if sone_list and len(sone_list) == 2:
                    id = sone_list[0]
                    # print (id)
                    if id:
                        ret.append(id)
        return ret

    def read_list_message_id(self, id, base_url='http://localhost:8000', username='django-test-user'):
        """

        :return:
        """
        # base_url = 'http://localhost:8000'
        # self.username = 'django-test-user'
        # print (id)
        ret2 = None
        resp, bytes_line_list, octets = self.server.retr(id)
        sresp2 = resp.decode('ascii')
        # print (sresp2)
        # print(octets)  #
        if '+OK' in sresp2:
            # print(bytes_line_list)
            # [
            # b'Return-Path: <wikstester@gmail.com>',
            # b'Received: from dell.wiks (ip-92-42-117-251.uznam.net.pl. [92.42.117.251])',
            # b'        by smtp.gmail.com with ESMTPSA id d126-v6sm2165111lfe.75.2018.11.10.14.35.44',
            # b'        for <wikstester@gmail.com>',
            # b'        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);',
            # b'        Sat, 10 Nov 2018 14:35:44 -0800 (PST)',
            # b'From: wikstester@gmail.com',
            # b'X-Google-Original-From: webmaster@localhost',
            # b'Content-Type: text/plain; charset="utf-8"',
            # b'MIME-Version: 1.0',
            # b'Content-Transfer-Encoding: 7bit',
            # b'Subject: Activate Your MySite Account',
            # b'To: wikstester@gmail.com', b'Date: Sat, 10 Nov 2018 22:35:44 -0000',
            # b'Message-ID: <154188934417.7488.14869954994231636527@dell.wiks>',
            # b'',
            # b'',
            # b'Hi django-test-user,',
            # b'',
            # b'Please click on the link below to confirm your registration:',
            # b'',
            # b'http://localhost:8000/activate/MTM/516-eda2f55eb69ac327c9f9/'
            # ]
            bytes_rx = b"\n".join(bytes_line_list)
            ret = email.message_from_bytes(bytes_rx)

            # print (ret._headers)
            h = {}
            for k, v in ret._headers:
                # print (k, v)
                h[k] = v
            # print (h)
            if h and 'Subject' in h.keys() and 'To' in h.keys() and 'From' in h.keys():
                if h['Subject'] == 'Activate Your MySite Account' \
                        and h['To'] == 'wikstester@gmail.com' \
                        and h['From'] == 'wikstester@gmail.com':
                    if ret.is_multipart():
                        for payload in ret.get_payload():
                            # if payload.is_multipart(): ...
                            cont = payload.get_payload()
                            ret2 = self.is_mail_setup_confirm(cont, base_url, username)
                    else:
                        cont = ret.get_payload()
                        ret2 = self.is_mail_setup_confirm(cont, base_url, username)
        else:
            print('none of +OK')
        return ret2

    def is_mail_setup_confirm(self, content, base_url = 'http://localhost:8000', username='django-test-user'):
        """

        :param content:
        :param username:
        :return:
        """
        # base_url = 'http://localhost:8000'
        ret = None
        if 'Please click on the link below to confirm your registration:' in content and username in content:
            # print(content)
            pos = content.find(base_url)
            if pos > 0:
                ret = content[pos:]
                r_list = ret.split()
                if r_list:
                    ret = r_list[0]
        else:
            pass
        return ret


if __name__ == '__main__':

    mgm = MGmail()
    ml = mgm.read_list()
    for id in ml:
        one = mgm.read_list_message_id(id)
        print (one)

# https://stackoverflow.com/questions/1463074/how-can-i-get-an-email-messages-text-content-using-python
