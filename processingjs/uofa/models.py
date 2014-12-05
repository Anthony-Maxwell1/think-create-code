from django.db import models
from django.forms import ModelForm
from django.core import validators
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager

from uofa.fields import NullableCharField


class UserManager(UserManager):

    def create_staffuser(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, is_staff=True, is_superuser=False,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Duplicate of the django AbstractUser model, customised for edX LTI users.

    Username, password and email are required. Other fields are optional.
    """
    username = models.CharField(_('user_id'), max_length=255, unique=True,
        help_text=_('Required. 255 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$', _('Enter a valid username.'), 'invalid')
        ])
    first_name = NullableCharField(_('username'), max_length=255, blank=True, null=True, unique=True, default=None)
    last_name = models.CharField(_('last name'), max_length=255, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'auth_user'

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        # Require non-empty values with one or more non-whitespace character
        self.fields['first_name'].required = True
        self.fields['first_name'].validators=[
            validators.RegexValidator(r'\S', _('Enter a valid username.'), 'invalid')
        ]

    def clean_first_name(self):
        # Strip leading/trailing spaces
        first_name = self.cleaned_data.get('first_name', '').strip()
        return first_name
