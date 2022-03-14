from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth

from eugo.models import Player

class TestLogin(TestCase):
    def setUp(self):
        self.client = Client()

    def testUnregisteredUser(self):
        # If a user enters an unregistered username/password combination then the sigin view returns the login.html template
        response = self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        self.assertTemplateUsed(response, "login.html")

    def testRegisteredUser(self):
        # Register a test user with username=TestUser and password=12345678
        user = User.objects.create_user("TestUser", "TestUser@gmail.com", "12345678")
        user.first_name = "Test"
        user.last_name = "User"
        user.save()

        # If a user enters a registered username/password combination then the sigin view returns the index.html template
        response = self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        self.assertTemplateUsed(response,"index.html")

        # Check the user has actually been authenticated and logged in
        user = auth.get_user(self.client)
        assert user.is_authenticated

class TestRegister(TestCase):
    def setUp(self):
        self.client = Client()

    def testRegisterUser(self):

        # Send post request to register a test user with username=TestUser and password=12345678
        response = self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test@eugo.com',
        'username': 'TestUser', 'password1': '12345678', 'sprite': 'eugo/static/eugo/img/teacher_sprites/teacher_1.png'})

        # Send post request to login with the newly created user. If the login is succesful, the index.html template is returned
        response = self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        self.assertTemplateUsed(response, "index.html")

        self.assertEquals(User.objects.get(username__exact="TestUser").username, "TestUser")

    def testRegisterDuplicateUser(self):

        # Send post request to register a test user with username=TestUser and password=12345678
        self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test@eugo.com',
        'username': 'TestUser', 'password1': '12345678', 'sprite': 'eugo/static/eugo/img/teacher_sprites/teacher_1.png'})

        # Register a duplicate of the newly registered user
        response = self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test@eugo.com',
        'username': 'TestUser', 'password1': '12345678', 'sprite': 'eugo/static/eugo/img/teacher_sprites/teacher_1.png'})

        # Assert that the user is redirected to the register page if they attempt to create a duplicate user
        # Should also test error messages for this
        self.assertRedirects(response, '/eugo/register/')
        # self.assertEquals(User.objects.all(), 1)

class TestPlayer(TestCase):
    def setUp(self):
        self.client = Client()

        # Register user in database with password 12345678
        user = User.objects.create_user("TestUser", "TestUser@gmail.com", "12345678")
        user.first_name = "Test"
        user.last_name = "User"
        user.save()

    def testChangePassword(self):

        # Login with the newly created user
        self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})

        # Change the users password to 87654321 and then assert that this has been carried out correctly
        response = self.client.post("/eugo/player/", {"pass1": "87654321"})
        user = User.objects.get(username__exact="TestUser")
        self.assertEquals(user.check_password("87654321"), True)
