from django.test import TestCase
from django.test import TransactionTestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth
from django.db import IntegrityError
from django.db import transaction
from eugo.views import EmailExistsException
from eugo.views import register
from eugo.models import Lecturer
from eugo.models import MapEvent
import requests

from eugo.models import Player

class TestLogin(TestCase):
    def setUp(self):
        self.client = Client()

    def testUnregisteredUser(self):
        # If a user enters an unregistered username/password combination then the sigin view returns the login.html template
        response = self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        self.assertTemplateUsed(response, "login.html")

        # Make sure the unregistered user has not been authenticated
        user = auth.get_user(self.client)
        assert not user.is_authenticated

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
        'username': 'TestUser', 'password1': '12345678', 'sprite': '1', 'canvas-output': ''})

        # Send post request to login with the newly created user. If the login is succesful, the index.html template is returned
        response = self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        self.assertTemplateUsed(response, "index.html")

        self.assertEquals(User.objects.get(username__exact="TestUser").username, "TestUser")

    def testRegisterDuplicateUsername(self):

        # Send post request to register a test user with username=TestUser and password=12345678
        response = self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test@eugo.com',
        'username': 'TestUser', 'password1': '12345678', 'sprite': '1', 'canvas-output': ''})

        self.assertRedirects(response, '/eugo/login/')

        with transaction.atomic():
            # Register a duplicate of the newly registered user
            response = self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test1@eugo.com',
            'username': 'TestUser', 'password1': '12345678', 'sprite': '1', 'canvas-output': ''})

            messages = response.context
            print(messages)

            # Assert that the user is redirected to the register page if they attempt to create a duplicate user
            # Should also test error messages for this
            self.assertRedirects(response, '/eugo/register/')
            print("hello")

        self.assertEquals(len(User.objects.all()), 1)

    def testRegisterDuplicateEmail(self):

        # Send post request to register a test user with username=TestUser and password=12345678
        response = self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test@eugo.com',
        'username': 'TestUser', 'password1': '12345678', 'sprite': '1', 'canvas-output': ''})

        self.assertRedirects(response, '/eugo/login/')

        with transaction.atomic():
            # Register a different username with the same email
            response = self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test@eugo.com',
            'username': 'TestUser1', 'password1': '12345678', 'sprite': '1', 'canvas-output': ''})

            # Assert that the user is redirected to the register page if they attempt to create a duplicate user
            # Should also test error messages for this
            self.assertRedirects(response, '/eugo/register/')

        self.assertEquals(len(User.objects.all()), 1)

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

class TestMapmod(TestCase):
    def setUp(self):
        self.client = Client()

    def createNewLecturer(self):

        # Send post request to create new wild lecturer called  TesrLecturer
        response = self.client.post("/eugo/mapmod/", {'duration': '1', 'name': 'TestLecturer', 'hp': '1', 'attack': '1', 'type': 'english',
        'sprite': '1', 'gameop': 'lecNewLi'})

        # Assert that the new lecturer has been stored in the Lecturer database
        self.assertEquals(len(Lecturer.objects.all()), 1)

        # User the id of the newly generated lecturer to acquire its QR code filepath
        qr_key = (Lecturer.objects.get(name="TestLecturer").id)
        file_path = 'eugo/static/eugo/img/qr/' + qr_key + '.png'

        # Test to see if we can open the QR at this filepath. If we cannot, the QR code has been incorrectly generated
        try:
            with open(file_path, 'r') as handler:
                pass
        except FileNotFoundError:
            self.fail("QR Code not generated correctly for new lecturer.")

        # Make sure the mapmod template is rendered
        self.assertTemplateUsed(response,"mapmod.html")

    def testQrAPI(self):
        # Test to make sure the QR code API is working
        qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + "123456TestLectutrer"
        self.assertEquals(requests.get(qrUrl).status_code, 200)

    def testWildLecturerSpawn(self):

        # Save new lectutrer in the database
        newLec = Lecturer(id="123456TestLectutrer", duration="1", name="TestLecturer", hp="1", attack="1", sprite="1",
        type="english", qrUrl = "123456TestLectutrer.png")
        newLec.save()

        # Send post request to spawn this new lectuter on the map
        response = self.client.post("/eugo/mapmod/", {'lecturer': '123456TestLectutrer', 'coords': '[469,509]', 'gameop': 'lecSpawnLi'})

        # Check that the spawn has been added and that it is saved in the databse as a wild lectutrer nd not a battle
        self.assertEquals(len(MapEvent.objects.all()), 1)
        self.assertEquals(MapEvent.objects.get(lec_id='123456TestLectutrer').wildOrBattle, 'lecSpawnLi')

        # Make sure the mapmod template is rendered
        self.assertTemplateUsed(response,"mapmod.html")
