""" ---------------------------- IMPORTS -------------------------------------------------------------- """
""" IMPORTS FROM DJANGO TEST - """
""" These are all for testing both client and server side """
from django.test import TestCase                                
from django.test import TransactionTestCase
from django.test import Client

""" IMPORTS FROM CONTRIB ----- """
""" Here to set up models and make sure that django build in functions are available """
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth

""" IMPORTS FROM DB ---------- """
""" These are for transactions and integrity errors """
from django.db import IntegrityError
from django.db import transaction

""" IMPORTS FROM VIEWS ------- """
""" These are used for the email exception and the built in register function """
from eugo.views import EmailExistsException
from eugo.views import register

""" IMPORTS FROM MODELS ------ """
""" These are all used so the database can be used and checked """
from eugo.models import Lecturer
from eugo.models import MapEvent
from eugo.models import Player
from eugo.models import Hand
from eugo.models import CompleteEvents
from eugo.models import FriendRequest
from eugo.models import FriendsList
from eugo.models import Player

""" OTHER IMPORTS ------------ """
""" Requests is used for sending selective data to the program """
import requests

""" ---------------------------- TESTS ---------------------------------------------------------------- """
""" LOGIN TESTS -------------- """
class TestLogin(TestCase):
    """ This method sets up the tests by creating a client """
    def setUp(self):
        self.client = Client()

    """ This method tests how the program treats unregistered players trying to login """
    def testUnregisteredUser(self):
        # If a user enters an unregistered username/password combination then the sigin view returns the login.html template
        response = self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        self.assertTemplateUsed(response, "login.html")

        # Make sure the unregistered user has not been authenticated
        user = auth.get_user(self.client)
        assert not user.is_authenticated

    """ This method tests how the program treats registered users logging in """
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


""" REGISTER TESTS ----------- """
class TestRegister(TestCase):
    """ This method sets up the tests by creating a client """
    def setUp(self):
        self.client = Client()

    """ This method test registering users with correct data """
    def testRegisterUser(self):
        # Send post request to register a test user with username=TestUser and password=12345678
        response = self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test@eugo.com',
        'username': 'TestUser', 'password1': '12345678', 'sprite': '1', 'canvas-output': '', 'staffno': ''})

        # Send post request to login with the newly created user. If the login is succesful, the index.html template is returned
        response = self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        self.assertTemplateUsed(response, "index.html")

        self.assertEquals(User.objects.get(username__exact="TestUser").username, "TestUser")

    """ This method tests regisetering users when a username already exists """
    def testRegisterDuplicateUsername(self):
        # Send post request to register a test user with username=TestUser and password=12345678
        response = self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test@eugo.com',
        'username': 'TestUser', 'password1': '12345678', 'sprite': '1', 'canvas-output': '', 'staffno': ''})

        self.assertRedirects(response, '/eugo/login/')

        with transaction.atomic():
            # Register a duplicate of the newly registered user
            response = self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test1@eugo.com',
            'username': 'TestUser', 'password1': '12345678', 'sprite': '1', 'canvas-output': '', 'staffno': ''})

            messages = response.context

            # Assert that the user is redirected to the register page if they attempt to create a duplicate user
            # Should also test error messages for this
            self.assertRedirects(response, '/eugo/register/')

        self.assertEquals(len(User.objects.all()), 1)

    """ This method tests registering users when the email address is already used """
    def testRegisterDuplicateEmail(self):
        # Send post request to register a test user with username=TestUser and password=12345678
        response = self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test@eugo.com',
        'username': 'TestUser', 'password1': '12345678', 'sprite': '1', 'canvas-output': '', 'staffno': ''})

        self.assertRedirects(response, '/eugo/login/')

        with transaction.atomic():
            # Register a different username with the same email
            response = self.client.post("/eugo/register/", {'firstname': 'Test', 'surname': 'User', 'email': 'Test@eugo.com',
            'username': 'TestUser1', 'password1': '12345678', 'sprite': '1', 'canvas-output': '', 'staffno': ''})

            # Assert that the user is redirected to the register page if they attempt to create a duplicate user
            # Should also test error messages for this
            self.assertRedirects(response, '/eugo/register/')

        self.assertEquals(len(User.objects.all()), 1)


""" PLAYER TESTS ------------- """
class TestPlayer(TestCase):
    """ This method sets up the tests by creating a client and registering a user """
    def setUp(self):
        self.client = Client()

        # Register user in database with password 12345678
        user = User.objects.create_user("TestUser", "TestUser@gmail.com", "12345678")
        user.first_name = "Test"
        user.last_name = "User"
        user.save()

    """ This method tests the user changing passwords """
    def testChangePassword(self):

        # Login with the newly created user
        self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})

        # Change the users password to 87654321 and then assert that this has been carried out correctly
        response = self.client.post("/eugo/player/", {"pass1": "87654321"})
        user = User.objects.get(username__exact="TestUser")
        self.assertEquals(user.check_password("87654321"), True)


""" MAPMOD TESTS ------------- """
class TestMapmod(TestCase):
    """ This method sets up the tests by creating a client and a player and user objects """
    def setUp(self):
        self.client = Client()

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

        self.player = Player.objects.create(firstname = 'Test', surname = 'User', email = 'Test@eugo.com', username = 'TestUser',
        pokemon_caught = 0, sprite_url = '1', is_admin=True)
        self.player.save()

    """ This method test the creation of new lecturers """
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
        print("swag")

    """ This method test if the QR API code works correctly """
    def testQrAPI(self):
        # Test to make sure the QR code API is working
        qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + "123456TestLecturer"
        self.assertEquals(requests.get(qrUrl).status_code, 200)

    """ This method test if spawning wild lecturers works corrrectly """
    def testWildLecturerSpawn(self):
        # Save new lectutrer in the database
        newLec = Lecturer(id="123456TestLecturer", duration="1", name="TestLecturer", hp="1", attack="1", sprite="1",
        type="english", qrUrl = "123456TestLecturer.png")
        newLec.save()

        # Send post request to spawn this new lectuter on the map
        response = self.client.post("/eugo/mapmod/", {'lecturer': '123456TestLecturer', 'coords':
        '[469,509]', 'gameop': 'lecSpawnLi'})

        # Check that the spawn has been added and that it is saved in the databse as a wild lectutrer nd not a battle
        self.assertEquals(len(MapEvent.objects.all()), 1)
        self.assertEquals(MapEvent.objects.get(lec_id='123456TestLecturer').wildOrBattle, 'lecSpawnLi')

        # Make sure the mapmod template is rendered
        self.assertTemplateUsed(response,"mapmod.html")

    """ This method tests if creating a lecturer battle works correctly """
    def testLecturerBattle(self):
        # Save new lectutrer in the database
        newLec = Lecturer(id="123456TestLecturer", duration="1", name="TestLecturer", hp="1", attack="1", sprite="1",
        type="english", qrUrl = "123456TestLecturer.png")
        newLec.save()

        # Send post request to start new battle on the map
        response = self.client.post("/eugo/mapmod/", {'lecturer': '123456TestLecturer', 'coords':
        '[469,509]', 'gameop': 'lecBattleLi'})

        # Check that the spawn has been added and that it is saved in the databse as a battle
        self.assertEquals(len(MapEvent.objects.all()), 1)
        self.assertEquals(MapEvent.objects.get(lec_id='123456TestLecturer').wildOrBattle, 'lecBattleLi')

        # Make sure the mapmod template is rendered
        self.assertTemplateUsed(response,"mapmod.html")


""" CATCH TESTS -------------- """
class TestCatch(TestCase):
    """ This method sets up the test by creating a cliend and user and player objects """
    def setUp(self):
        self.client = Client()

        # Set up a new user
        user = User.objects.create_user("TestUser", "TestUser@gmail.com", "12345678")
        user.first_name = "Test"
        user.last_name = "User"
        user.save()

        # Log in with the new user and check it is authenticated
        self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        user = auth.get_user(self.client)
        assert user.is_authenticated

        self.player = Player.objects.create(firstname = 'Test', surname = 'User', email = 'Test@eugo.com', username = 'TestUser',
        pokemon_caught = 0, sprite_url = '1')
        self.player.save()

    """ This method test the catching of lecturers """
    def testCatch(self):
        newLec = Lecturer(id="123456TestLecturer", duration="1", name="TestLecturer", hp="1", attack="1", sprite="1",
        type="english", qrUrl = "123456TestLecturer.png")
        newLec.save()
        response = self.client.post("/eugo/catch/", {'lecID': ['123456TestLecturer'], 'eventID': ['709,33316:15:10']})
        self.assertTemplateUsed(response,'catch.html')


""" NEWCATCH TESTS ----------- """
class TestNewCatch(TestCase):
    """ This method sets up the test by creating a cliend and user, player, lecturer and wild lecturer objects """
    def setUp(self):
        self.client = Client()

        # Set up a new user
        user = User.objects.create_user("TestUser", "TestUser@gmail.com", "12345678")
        user.first_name = "Test"
        user.last_name = "User"
        user.save()

        # Log in with the new user and check it is authenticated
        self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        user = auth.get_user(self.client)
        assert user.is_authenticated

        # Create a new player objects
        self.player = Player.objects.create(firstname = 'Test', surname = 'User', email = 'Test@eugo.com', username = 'TestUser',
        pokemon_caught = 0, sprite_url = '1')
        self.player.save()

        # Create a new lecturer object
        self.newLec = Lecturer(id="123456TestLecturer", duration="1", name="TestLecturer", hp="1", attack="1", sprite="1",
        type="english", qrUrl = "123456TestLecturer.png")
        self.newLec.save()

        # Create a new wild lectuter spawn with the lecturer we created above
        self.event = MapEvent(id = '709,33316:15:10', lec_id = self.newLec, pos=[709,33316], wildOrBattle='lecSpawnLi')
        self.event.save()

    def testCatch(self):

        # Send a post request to catch the new pokemon. We simulate canning a QR code to retrieve the lec
        # id and then send it to the /newcatch view
        response = self.client.post("/eugo/newcatch/", {'lec_id': '123456TestLecturer', 'event_id': ['709,33316:15:10'],
        'balls': 0})

        # Assert that the player has their poken caught count incremented by 1
        self.assertEquals(Player.objects.get(username="TestUser").pokemon_caught, 1)

        # Assert that a new hand has been created for TestUser and the caught lectuter with id 123456TestLecturer
        self.assertEquals(len(Hand.objects.all()), 1)
        self.assertEquals(Hand.objects.get(username=self.player).username.username, 'TestUser')
        self.assertEquals(Hand.objects.get(lec_id=self.newLec).lec_id.id, '123456TestLecturer')

        # Assert that a new event has been completed with the player that caught the pokemon and the event on the map
        self.assertEquals(len(CompleteEvents.objects.all()), 1)
        event = CompleteEvents.objects.get(username=self.player)
        self.assertEquals(event.event, self.event)

        # Assert that the catch.html template is rendered back to the user
        self.assertTemplateUsed(response, "catch.html")

""" LECTURER DEX TESTS ------- """
class TestLecturerdex(TestCase):
    """ This method sets up the tests by creating a client and user, player lecturer objects """
    def setUp(self):
        self.client = Client()

        # Set up a new user
        user = User.objects.create_user("TestUser", "TestUser@gmail.com", "12345678")
        user.first_name = "Test"
        user.last_name = "User"
        user.save()

        # Log in with the new user and check it is authenticated
        self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        user = auth.get_user(self.client)
        assert user.is_authenticated

        # Create a new player objects
        self.player = Player.objects.create(firstname = 'Test', surname = 'User', email = 'Test@eugo.com', username = 'TestUser',
        pokemon_caught = 0, sprite_url = '1')
        self.player.save()

        # Create a new lecturer object
        self.newLec = Lecturer(id="123456TestLecturer", duration="1", name="TestLecturer", hp="1", attack="1", sprite="1",
        type="english", qrUrl = "123456TestLecturer.png")
        self.newLec.save()

    """ This method tests if lecturerdex returns what it should """
    def testLecturerdex(self):
        # Get request for the lecturerdex
        response = self.client.get("/eugo/lecturerdex/")

        # Check that the lecturerdex template is rendered
        self.assertTemplateUsed(response, 'lecturerdex.html')

        # Check that it is rendered with the new lectutrer object
        self.assertEquals(response.context["lec"].get(id="123456TestLecturer").name, "TestLecturer")


""" LECTURERS TESTS ---------- """
class TestLecturers(TestCase):
    """ This method sets up the tests by creating a cliend and user, player, lecturer, wild lecturer and hand objects """
    def setUp(self):
        self.client = Client()

        # Set up a new user
        user = User.objects.create_user("TestUser", "TestUser@gmail.com", "12345678")
        user.first_name = "Test"
        user.last_name = "User"
        user.save()

        # Log in with the new user and check it is authenticated
        self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        user = auth.get_user(self.client)
        assert user.is_authenticated

        # Create a new player objects
        self.player = Player.objects.create(firstname = 'Test', surname = 'User', email = 'Test@eugo.com', username = 'TestUser',
        pokemon_caught = 0, sprite_url = '1')
        self.player.save()

        # Create a new lecturer object
        self.newLec = Lecturer(id="123456TestLecturer", duration="1", name="TestLecturer", hp="1", attack="1", sprite="1",
        type="english", qrUrl = "123456TestLecturer.png")
        self.newLec.save()

        # Create a new wild lectuter spawn with the lecturer we created above
        self.event = MapEvent(id = '709,33316:15:10', lec_id = self.newLec, pos=[709,33316], wildOrBattle='lecSpawnLi')
        self.event.save()

        hand = Hand(username = self.player, lec_id = self.newLec)
        hand.save()

    """ This method tests if lecturers method return the right html template with the right data """
    def testLecturers(self):
        # Get request for the lecturers
        response = self.client.get("/eugo/lecturers/")

        # Check that the lecturers template is rendered
        self.assertTemplateUsed(response, 'lecturers.html')

        # Check that it is rendered with the hand object
        self.assertEquals(response.context["hand"].get(username=self.player).lec_id, self.newLec)


""" FRIEND REQUEST TEST ------ """
class TestFriendRequest(TestCase):
    """ This method sets up the tests by creating a client and user, player, objects """
    def setUp(self):
        self.client = Client()

        # Set up a new user TestUser
        user1 = User.objects.create_user("TestUser", "TestUser@gmail.com", "12345678")
        user1.first_name = "Test"
        user1.last_name = "User"
        user1.save()

        # Log in with the new user and check it is authenticated
        self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        user1 = auth.get_user(self.client)
        assert user1.is_authenticated

        # Create a new player objects
        self.player1 = Player.objects.create(firstname = 'Test', surname = 'User', email = 'TestUser@eugo.com', username = 'TestUser',
        pokemon_caught = 0, sprite_url = '1')
        self.player1.save()

        # Set up a new user TestUser1
        user2 = User.objects.create_user("TestUser1", "TestUser1@gmail.com", "12345678")
        user2.first_name = "Test"
        user2.last_name = "User"
        user2.save()

        # Log in with the new user and check it is authenticated
        self.client.post('/eugo/login/', {'username': 'TestUser1', 'password': '12345678'})
        user2 = auth.get_user(self.client)
        assert user2.is_authenticated

        # Create a new player objects
        self.player2 = Player.objects.create(firstname = 'Test', surname = 'User', email = 'TestUser1@eugo.com', username = 'TestUser1',
        pokemon_caught = 0, sprite_url = '1')
        self.player2.save()

    def testFriendRequest(self):

        # TestUser sends a friend request to TestUser1 via a post request
        response = self.client.post("/eugo/friendreq/", {'type': 'send', 'sender': 'TestUser', 'reciever': 'TestUser1'})

        # Assert that a new friend request object is generated
        self.assertEquals(len(FriendRequest.objects.all()), 1)

        # Check that the correct sender and reciver are stored in the request
        friend_req = FriendRequest.objects.get(sender=self.player1)
        self.assertEquals(friend_req.sender.username, "TestUser")
        self.assertEquals(friend_req.reciever.username, "TestUser1")

        # Check the the rendered template is map.html
        self.assertTemplateUsed(response, 'map.html')

        # Send a post request to simulate TestUser1 accepting the request
        response = self.client.post("/eugo/friendreq/", {'type': 'accept', 'sender': 'TestUser', 'reciever': 'TestUser1'})

        # Asser that the two users have been added to the others friend list
        self.assertEquals(str(FriendsList.objects.get(user1=self.player1).friends), "," + str(self.player2.id))
        self.assertEquals(str(FriendsList.objects.get(user1=self.player2).friends), "," + str(self.player1.id))

        # Check that the friend reuqest is made inactive after it is accepted
        friend_req = FriendRequest.objects.get(sender=self.player1)
        self.assertEquals(friend_req.is_active, False)

        # Check the the rendered template is map.html
        self.assertTemplateUsed(response, 'map.html')

    def testDuplicateFriendRequest(self):

        # TestUser sends two friend requests to TestUser1 via a post request
        response = self.client.post("/eugo/friendreq/", {'type': 'send', 'sender': 'TestUser', 'reciever': 'TestUser1'})
        response = self.client.post("/eugo/friendreq/", {'type': 'send', 'sender': 'TestUser', 'reciever': 'TestUser1'})

        # Assert that only one new friend request object is generated
        self.assertEquals(len(FriendRequest.objects.all()), 1)

        # Check the the rendered template is map.html
        self.assertTemplateUsed(response, 'map.html')

    def testPlayerNotFound(self):

        # TestUser sends two friend requests to TestUser2 via a post request
        try:
            response = self.client.post("/eugo/friendreq/", {'type': 'send', 'sender': 'TestUser', 'reciever': 'TestUser2'})
            self.fail("Player does not exist.")
        except:
            pass

        # Assert that no new friend request object is generated
        self.assertEquals(len(FriendRequest.objects.all()), 0)


class TestTrade(TestCase):
    def setUp(self):
        self.client = Client()

        # Set up a new user TestUser
        user1 = User.objects.create_user("TestUser", "TestUser@gmail.com", "12345678")
        user1.first_name = "Test"
        user1.last_name = "User"
        user1.save()

        # Log in with the new user and check it is authenticated
        self.client.post('/eugo/login/', {'username': 'TestUser', 'password': '12345678'})
        user1 = auth.get_user(self.client)
        assert user1.is_authenticated

        # Create a new player objects
        self.player1 = Player.objects.create(firstname = 'Test', surname = 'User', email = 'TestUser@eugo.com', username = 'TestUser',
        pokemon_caught = 0, sprite_url = '1')
        self.player1.save()

        # Create a new lecturer object
        self.newLec1 = Lecturer(id="123456TestLecturer", duration="1", name="TestLecturer", hp="1", attack="1", sprite="1",
        type="english", qrUrl = "123456TestLecturer.png")
        self.newLec1.save()

        # Store the new lectuter is TestUser's hadnds
        self.hand1 = Hand(username = self.player1, lec_id = self.newLec1)
        self.hand1.save()

        # Set up a new user TestUser1
        user2 = User.objects.create_user("TestUser1", "TestUser1@gmail.com", "12345678")
        user2.first_name = "Test"
        user2.last_name = "User"
        user2.save()

        # Log in with the new user and check it is authenticated
        self.client.post('/eugo/login/', {'username': 'TestUser1', 'password': '12345678'})
        user2 = auth.get_user(self.client)
        assert user2.is_authenticated

        # Create a new player objects
        self.player2 = Player.objects.create(firstname = 'Test', surname = 'User', email = 'TestUser1@eugo.com', username = 'TestUser1',
        pokemon_caught = 0, sprite_url = '1')
        self.player2.save()

        # Create a new lecturer object
        self.newLec2 = Lecturer(id="123456TestLecturer1", duration="1", name="TestLecturer1", hp="1", attack="1", sprite="2",
        type="english", qrUrl = "123456TestLecturer1.png")
        self.newLec2.save()

        # Store the new lectuter is TestUser's hadnds
        self.hand2 = Hand(username = self.player2, lec_id = self.newLec2)
        self.hand2.save()

    def testTrade(self):

        response = self.client.post("/eugo/trade/", {'reciever': 'TestUser1', 'sender': 'TestUser'})

        # Assert that the post request renders the trade.html template with the names of the sender
        # and the name of the receiver and their respective lecturer hands
        self.assertEquals(response.context["sender"].get(username=self.player1), self.hand1)
        self.assertEquals(response.context["sender_name"], "TestUser")
        self.assertEquals(response.context["reciever"].get(username=self.player2), self.hand2)
        self.assertEquals(response.context["reciever_name"], "TestUser1")
        self.assertTemplateUsed(response, "trade.html")

        # <QueryDict: {'left': [''], 'right': ['']}>
