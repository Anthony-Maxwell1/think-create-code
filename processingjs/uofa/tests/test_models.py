from django.test import TestCase
from django.core import mail

from uofa.models import User, UserManager

class UserManagerTests(TestCase):

    def test_create_staffuser(self):
        staff_user = User.objects.create_staffuser('staff_member', password='bad password')
        self.assertTrue(staff_user.is_staff)


class UserTests(TestCase):

    def test_full_name(self):
        noname = User.objects.create_user('noname')
        self.assertEquals(noname.get_full_name(), '')

        firstname = User.objects.create_user('firstname', first_name = 'First')
        self.assertEquals(firstname.get_full_name(), firstname.first_name)

        lastname = User.objects.create_user('lastname', last_name = 'Last')
        self.assertEquals(lastname.get_full_name(), lastname.last_name)

        fullname = User.objects.create_user('fullname', first_name='First', last_name = 'Last')
        self.assertEquals(fullname.get_full_name(), 
                          '%s %s' % (fullname.first_name, fullname.last_name))

        trimname = User.objects.create_user('trimname', first_name=' First', last_name = 'Last ')
        self.assertEquals(trimname.get_full_name(), 
                          ('%s %s' % (trimname.first_name, trimname.last_name)).strip())

    def test_short_name(self):
        noname = User.objects.create_user('noname')
        self.assertEquals(noname.get_short_name(), '')

        firstname = User.objects.create_user('firstname', first_name = 'First')
        self.assertEquals(firstname.get_short_name(), firstname.first_name)

        lastname = User.objects.create_user('lastname', last_name = 'Last')
        self.assertEquals(lastname.get_short_name(), '')

        fullname = User.objects.create_user('fullname', first_name='First', last_name = 'Last')
        self.assertEquals(fullname.get_short_name(), fullname.first_name)

        trimname = User.objects.create_user('trimname', first_name=' First', last_name = 'Last ')
        self.assertEquals(trimname.get_short_name(), trimname.first_name)

    def test_email_user(self):
        # valid send_mail parameters
        kwargs = {
            "fail_silently": False,
            "auth_user": None,
            "auth_password": None,
            "connection": None,
            "html_message": None,
        }
        user = User(email='foo@bar.com')
        user.email_user(subject="Subject here",
            message="This is a message", from_email="from@domain.com", **kwargs)
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
        # Verify that test email contains the correct attributes:
        message = mail.outbox[0]
        self.assertEqual(message.subject, "Subject here")
        self.assertEqual(message.body, "This is a message")
        self.assertEqual(message.from_email, "from@domain.com")
        self.assertEqual(message.to, [user.email])
