"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class UserViewsTest(TestCase):
    #Same username & case
    def test_username_equivalence(self):
        User.objects.create_user("test0","No Email","password")
        new_user = {'username':'test0','password':'password','confirmpw':'password'}
        response = self.client.post('/register/', new_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "User already exists!")

    #Same username and different case should fail
    def test_username_case_equivalence(self):
        User.objects.create_user("test0","No Email","password")
        new_user = {'username':'tEST0','password':'password','confirmpw':'password'}
        response = self.client.post('/register/', new_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "User already exists!")

    def test_password_mismatch(self):
        new_user = {'username':'test1','password':'password','confirmpw':'password1'}
        response = self.client.post('/register/', new_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Passwords do not match!")