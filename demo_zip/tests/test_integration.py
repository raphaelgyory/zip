# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.files import File
from django.test.client import RequestFactory
from selenium.webdriver.firefox.webdriver import WebDriver
from pyvirtualdisplay import Display

from zip.users.models import User
from demo_zip.models import ZipApplication

import time


class IntegrationTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()
        # we do not display
        cls.display = Display(visible=0, size=(1024, 768))
        cls.display.start()
        cls.selenium = WebDriver()
        cls.request = RequestFactory()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.close()
        cls.selenium.quit()
        cls.display.stop()
        super(IntegrationTests, cls).tearDownClass()

    def test_integration(self):
        # we create an admin
        password = "password"
        self.admin = User(username="admin", is_active=True, is_staff=True)
        self.admin.set_password(password)
        self.admin.save()
        # we create a regular user
        self.regular = User(username="regular", is_active=True, is_staff=False)
        self.regular.set_password(password)
        self.regular.save()
        # we reuse the same package for every app, the content does not matter here
        with open(str(settings.ROOT_DIR) + '/demo_zip/tests/zip_test_dir.zip') as f:
            # the admin publishes one public and one private app
            self.admin_public_app = ZipApplication.objects.create(user=self.admin,
                                                                  name="admin public app",
                                                                  description="admin public app description",
                                                                  file=File(f))
            self.admin_private_app = ZipApplication.objects.create(user=self.admin,
                                                                   name="admin private app",
                                                                   description="admin private app description",
                                                                   file=File(f), is_private=True)
            self.regular_public_app = ZipApplication.objects.create(user=self.regular,
                                                                    name="regular public app",
                                                                    description="regular public app description",
                                                                    file=File(f))
            self.regular_private_app = ZipApplication.objects.create(user=self.regular,
                                                                     name="regular private app",
                                                                     description="regular private app description",
                                                                     file=File(f), is_private=True)
        # we visit the site as an anonymous user
        self.selenium.get(self.live_server_url)
        # we click the app link
        self.selenium.execute_script("document.querySelectorAll('.apps_link')[0].click()")
        time.sleep(1)
        # we see all the public resources
        # and none of the private ones
        row_admin_public_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.admin_public_app.id))
        row_admin_private_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.admin_private_app.id))
        row_regular_public_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.regular_public_app.id))
        row_regular_private_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.regular_private_app.id))
        # the update - delete options of the admin
        row_admin_public_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.admin_public_app.id))
        row_admin_public_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.admin_public_app.id))
        row_admin_private_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.admin_private_app.id))
        row_admin_private_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.admin_private_app.id))
        # the update - delete options of the regular user
        row_regular_public_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.regular_public_app.id))
        row_regular_public_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.regular_public_app.id))
        row_regular_private_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.regular_private_app.id))
        row_regular_private_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.regular_private_app.id))
        # we see the public apps
        self.assertEqual(1, len(row_admin_public_app))
        self.assertEqual(0, len(row_admin_private_app))
        self.assertEqual(1, len(row_regular_public_app))
        self.assertEqual(0, len(row_regular_private_app))
        # we have no option to update or delete them
        self.assertEqual(0, len(row_admin_public_app_update))
        self.assertEqual(0, len(row_admin_public_app_delete))
        self.assertEqual(0, len(row_admin_private_app_update))
        self.assertEqual(0, len(row_admin_private_app_delete))
        self.assertEqual(0, len(row_regular_public_app_update))
        self.assertEqual(0, len(row_regular_public_app_delete))
        self.assertEqual(0, len(row_regular_private_app_update))
        self.assertEqual(0, len(row_regular_private_app_delete))
        # trying to donwload a private app won't work
        self.selenium.get(self.live_server_url + '/download/' +
                          str(self.admin_private_app.id) + '/')
        self.assertEqual(1, len(self.selenium.find_elements_by_class_name("forbidden_view")))
        time.sleep(3)
        # hitting the upload button redirects us to the login form
        self.selenium.execute_script("document.querySelectorAll('.upload_link')[0].click()")
        time.sleep(1)
        # we submit it
        login_input = self.selenium.find_elements_by_id("id_login")[0]
        login_input.send_keys(self.regular.username)
        password_input = self.selenium.find_elements_by_name("password")[0]
        password_input.send_keys(password)
        self.selenium.execute_script("document.querySelectorAll('.sign-in-button')[0].click()")
        time.sleep(1)
        # he will be redirected to the file uploads
        # for now, we have 2 ZipApplication instances for the regular user
        self.assertEqual(2, ZipApplication.objects.filter(user=self.regular).count())
        # we must make the upload button visible or selenium will not interact with it
        self.selenium.execute_script("document.querySelectorAll('#id_file')[0].parentNode.className='';")
        time.sleep(1)
        # we submit an empty form to check against erros
        self.selenium.execute_script("document.querySelectorAll('.upload-button')[0].click()")
        errors = self.selenium.find_elements_by_class_name("is-invalid")
        self.assertEqual(3, len(errors))
        # we submit correct values
        self.selenium.execute_script("document.querySelectorAll('#id_file')[0].parentNode.className='';")
        time.sleep(1)
        self.selenium.find_elements_by_id("id_name")[0].send_keys("Added via form by regular")
        self.selenium.find_elements_by_id("id_description")[0].send_keys("Decription")
        self.selenium.find_elements_by_id("id_is_private")[0].send_keys(False)
        self.selenium.find_elements_by_id("id_file")[0]\
            .send_keys(str(settings.ROOT_DIR) + '/demo_zip/tests/zip_test_dir.zip')
        self.selenium.execute_script("document.querySelectorAll('.upload-button')[0].click()")
        time.sleep(5)
        # now we must have tree
        self.assertEqual(3, ZipApplication.objects.filter(user=self.regular).count())
        # we must be on the apps page
        # we must see the all the public apps and the regular user's private one
        last_app = ZipApplication.objects.latest('id')
        row_admin_public_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.admin_public_app.id))
        row_admin_private_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.admin_private_app.id))
        row_regular_public_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.regular_public_app.id))
        row_regular_private_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.regular_private_app.id))
        row_regular_new_public_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(last_app.id))
        # the update - delete options of the admin
        row_admin_public_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.admin_public_app.id))
        row_admin_public_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.admin_public_app.id))
        row_admin_private_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.admin_private_app.id))
        row_admin_private_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.admin_private_app.id))
        # the update - delete options of the regular user
        row_regular_public_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.regular_public_app.id))
        row_regular_public_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.regular_public_app.id))
        row_regular_private_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.regular_private_app.id))
        row_regular_private_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.regular_private_app.id))
        # we see the public apps
        self.assertEqual(1, len(row_admin_public_app))
        self.assertEqual(0, len(row_admin_private_app))
        self.assertEqual(1, len(row_regular_public_app))
        self.assertEqual(1, len(row_regular_private_app))
        self.assertEqual(1, len(row_regular_new_public_app))
        # we have no option to update or delete them
        self.assertEqual(0, len(row_admin_public_app_update))
        self.assertEqual(0, len(row_admin_public_app_delete))
        self.assertEqual(0, len(row_admin_private_app_update))
        self.assertEqual(0, len(row_admin_private_app_delete))
        self.assertEqual(1, len(row_regular_public_app_update))
        self.assertEqual(1, len(row_regular_public_app_delete))
        self.assertEqual(1, len(row_regular_private_app_update))
        self.assertEqual(1, len(row_regular_private_app_delete))
        # the user modifies his last app
        self.selenium.find_elements_by_class_name("update_app_row_" + str(last_app.id))[0].click()
        time.sleep(2)
        self.selenium.execute_script("document.querySelectorAll('#id_file')[0].parentNode.className='';")
        self.selenium.find_elements_by_id("id_name")[0].send_keys(" Modified")
        self.selenium.find_elements_by_id("id_description")[0].send_keys("Decription")
        self.selenium.find_elements_by_id("id_is_private")[0].send_keys(False)
        self.selenium.find_elements_by_id("id_file")[0]\
            .send_keys(str(settings.ROOT_DIR) + '/demo_zip/tests/zip_test_dir.zip')
        self.selenium.execute_script("document.querySelectorAll('.upload-button')[0].click()")
        time.sleep(5)
        # the app has been updated
        modified = ZipApplication.objects.latest('id')
        self.assertEqual(last_app.id, modified.id)
        self.assertNotEqual(last_app.name, modified.name)
        # he deletes an app
        self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.regular_public_app.id))[0].click()
        time.sleep(1)
        self.selenium.find_elements_by_class_name("confirm_delete_btn")[0].click()
        time.sleep(3)
        # now go back to two apps
        self.assertEqual(2, ZipApplication.objects.filter(user=self.regular).count())
        # we logout and re-login as the admin
        self.selenium.execute_script("document.querySelectorAll('.logout_link')[0].click()")
        time.sleep(1)
        self.selenium.execute_script("document.querySelectorAll('.signout_confirm_btn')[0].click()")
        time.sleep(1)
        # loggin as admin
        self.selenium.execute_script("document.querySelectorAll('.login_link')[0].click()")
        time.sleep(1)
        login_input = self.selenium.find_elements_by_id("id_login")[0]
        login_input.send_keys(self.admin.username)
        password_input = self.selenium.find_elements_by_name("password")[0]
        password_input.send_keys(password)
        self.selenium.execute_script("document.querySelectorAll('.sign-in-button')[0].click()")
        time.sleep(1)
        row_admin_public_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.admin_public_app.id))
        row_admin_private_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.admin_private_app.id))
        row_regular_public_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.regular_public_app.id))
        row_regular_private_app =\
            self.selenium.find_elements_by_class_name("app_row_" + str(self.regular_private_app.id))
        # the update - delete options of the admin
        row_admin_public_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.admin_public_app.id))
        row_admin_public_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.admin_public_app.id))
        row_admin_private_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.admin_private_app.id))
        row_admin_private_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.admin_private_app.id))
        # the update - delete options of the regular user
        row_regular_public_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.regular_public_app.id))
        row_regular_public_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.regular_public_app.id))
        row_regular_private_app_update =\
            self.selenium.find_elements_by_class_name("update_app_row_" + str(self.regular_private_app.id))
        row_regular_private_app_delete =\
            self.selenium.find_elements_by_class_name("delete_app_row_" + str(self.regular_private_app.id))
        # we see the public apps
        self.assertEqual(1, len(row_admin_public_app))
        self.assertEqual(1, len(row_admin_private_app))
        self.assertEqual(0, len(row_regular_public_app))  # it has been deleted
        self.assertEqual(1, len(row_regular_private_app))
        # he may update or delete anything
        self.assertEqual(1, len(row_admin_public_app_update))
        self.assertEqual(1, len(row_admin_public_app_delete))
        self.assertEqual(1, len(row_admin_private_app_update))
        self.assertEqual(1, len(row_admin_private_app_delete))
        self.assertEqual(1, len(row_regular_private_app_update))
        self.assertEqual(1, len(row_regular_private_app_delete))
        # the admin modifies the regular user's last app
        self.selenium.find_elements_by_class_name("update_app_row_" + str(last_app.id))[0].click()
        time.sleep(2)
        self.selenium.execute_script("document.querySelectorAll('#id_file')[0].parentNode.className='';")
        self.selenium.find_elements_by_id("id_name")[0].send_keys(" Modified by admin")
        self.selenium.find_elements_by_id("id_description")[0].send_keys("Decription")
        self.selenium.find_elements_by_id("id_is_private")[0].send_keys(False)
        self.selenium.find_elements_by_id("id_file")[0]\
            .send_keys(str(settings.ROOT_DIR) + '/demo_zip/tests/zip_test_dir.zip')
        self.selenium.execute_script("document.querySelectorAll('.upload-button')[0].click()")
        time.sleep(2)
        # the app has been updated
        self.assertEqual(modified.id, ZipApplication.objects.latest('id').id)
        self.assertNotEqual(modified.name, ZipApplication.objects.latest('id').name)
        # he deletes it
        self.selenium.find_elements_by_class_name("delete_app_row_" + str(modified.id))[0].click()
        time.sleep(1)
        self.selenium.find_elements_by_class_name("confirm_delete_btn")[0].click()
        time.sleep(3)
        # only one app remains
        self.assertEqual(1, ZipApplication.objects.filter(user=self.regular).count())
