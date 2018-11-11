from django.test import TestCase
from mysite.settings import EMAIL_HOST_USER
import random
import string
from time import sleep
# from django.contrib.auth.models import User
# from mysite.core.models import Profile

from django.utils.timezone import datetime, timedelta
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from django.contrib.sites.models import Site

from mysite.mutils.mgmail import MGmail

import logging
logger = logging.getLogger(__name__)

# --------
# RUN: python manage.py test


class AccountCreateTestCase(TestCase):
    """

    """

    def setUp(self):

        # current_site = Site.objects.get_current()
        self.base_url = 'http://localhost:8000/'
        logger.debug(self.base_url)

        # logger.debug('setUp')
        self.mgm = MGmail()
        self.testuser = {'username': 'django-test-user',
                         'email': EMAIL_HOST_USER,
                         'password': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
                         }
        # self.testusertmp = {'username': 'django-test-user-tmp',
        #                     'email': EMAIL_HOST_USER,
        #                     'password': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
        #                     }

        # user = User.objects.get(username=self.testusertmp['username'])
        # print(user)

        # Image.objects.filter(object_id=object_to_be_deleted.id,
        #                      content_type=ContentType.objects.get_for_model(bject_to_be_deleted.get_profile())).delete()
        # object_to_be_deleted.delete()

        # user = User.objects.all()  #get(email=self.testuser['email'])
        # logger.debug('setUp, user: %s', user)
        # if user:
        #     logger.debug('setUp, DELETE user: %s', user)
        #     user.delete()

        self.selenium = webdriver.Firefox()
        # self.selenium.maximize_window()
        self.selenium2 = webdriver.Firefox()

    def tearDown(self):

        self.selenium.quit()
        pass

    def testCreateLoginLogout(self):
        """
        test create account,
        test login to it and logout
        :return:
        """

        self.selenium.get(self.base_url)
        id_signup = self.selenium.find_element_by_id("signup")
        id_signup.click()

        id_username = self.selenium.find_element_by_id('id_username')
        id_email = self.selenium.find_element_by_id('id_email')
        id_password1 = self.selenium.find_element_by_id('id_password1')
        id_password2 = self.selenium.find_element_by_id('id_password2')
        button_submit = self.selenium.find_element_by_xpath("//button[@type='submit']")

        id_username.send_keys(self.testuser['username'])
        id_email.send_keys(self.testuser['email'])
        id_password1.send_keys(self.testuser['password'])
        id_password2.send_keys(self.testuser['password'])
        button_submit.click()

        look_for = 'Please confirm your email address to complete the registration.'
        is_web_confirmation = self.selenium.find_elements_by_xpath("//*[contains(text(), '" + look_for + "')]")
        # print(is_web_confirmation)
        if is_web_confirmation:
            logger.debug('look like SIGNUP first etap successfully, now recive email and confirm it by click')

            seleniums_list = {}
            ml = self.mgm.read_list()
            ten_sec = 10
            while not ml:
                logger.debug('waiting %s sec for EMAIL with confirmation link recived...', ten_sec)
                ml = self.mgm.read_list()
                sleep(ten_sec)
            if ml:
                for id in ml:
                    one = self.mgm.read_list_message_id(id, self.base_url, self.testuser['username'])
                    if one:
                        seleniums_list[id] = webdriver.Firefox()
                        logger.debug('CONDIRMED by email-link-clicked')
                        seleniums_list[id].get(one)
                        seleniums_list[id].quit()
                seleniums_list.clear()
        else:
            look_for = 'A user with that username already exists.'
            user_exist = self.selenium.find_elements_by_xpath("//*[contains(text(), '" + look_for + "')]")
            if user_exist:
                logger.debug('look like USER IS REGISTERED')

        if is_web_confirmation:

            self.selenium2.get(self.base_url)
            id_login = self.selenium2.find_element_by_id("login")

            id_login.click()
            logger.debug('LOGIN click')

            id_username = self.selenium2.find_element_by_id('id_username')
            id_password = self.selenium2.find_element_by_id('id_password')

            id_username.send_keys(self.testuser['username'])
            id_password.send_keys(self.testuser['password'])

            button_submit = self.selenium2.find_element_by_xpath("//button[@type='submit']")
            button_submit.click()
            logger.debug('LOGIN BUTTON click after user and pass inputed')

            id_logout = self.selenium2.find_element_by_id("logout")
            id_logout.click()
            logger.debug('LOGOUT click')

            id_login = self.selenium2.find_element_by_id("login")
            logger.debug('LOGOUT success')

