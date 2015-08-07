from django.core.urlresolvers import reverse
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from django.contrib.auth import get_user_model
import time

from artwork.models import Artwork
from exhibitions.models import Exhibition
from submissions.models import Submission
from votes.models import Vote
from django_adelaidex.util.test import SeleniumTestCase, NoHTML5SeleniumTestCase, wait_for_page_load


class ArtworkListIntegrationTests(SeleniumTestCase):

    def test_private_artwork_list(self):

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        # Public can't see any artworks
        list_path = reverse('artwork-list')
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            0
        )

        # Can login to see my artwork, but no one else's
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork1.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-list-zip'))
        )

    def test_shared_artwork_list(self):

        list_path = reverse('artwork-list')

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', shared=1, author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', shared=4, author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', shared=78, author=self.super_user)

        # Shared artwork is visible to the public
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )
        titles = self.selenium.find_elements_by_css_selector('.artwork-title')
        self.assertEqual(
            titles[0].text,
            artwork3.title
        )
        self.assertEqual(
            titles[1].text,
            artwork2.title
        )
        self.assertEqual(
            titles[2].text,
            artwork1.title
        )

        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-list-zip'))
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-add')
        )

        # Shared artwork + own private artwork is visible to logged-in users
        artwork4 = Artwork.objects.create(title='Artwork 4', code='// code goes here', shared=1, author=self.user)
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            4
        )
        titles = self.selenium.find_elements_by_css_selector('.artwork-title')
        self.assertEqual(
            titles[0].text,
            artwork4.title
        )
        self.assertEqual(
            titles[1].text,
            artwork3.title
        )
        self.assertEqual(
            titles[2].text,
            artwork2.title
        )
        self.assertEqual(
            titles[3].text,
            artwork1.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-list-zip'))
        )

    def test_artwork_shared_list(self):

        list_path = reverse('artwork-shared')

        artwork1p = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', shared=1, author=self.user)
        artwork2p = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', shared=4, author=self.staff_user)
        artwork3p = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', shared=78, author=self.super_user)

        # Shared artwork is visible to the public
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )
        titles = self.selenium.find_elements_by_css_selector('.artwork-title')
        self.assertEqual(
            titles[0].text,
            artwork3.title
        )
        self.assertEqual(
            titles[1].text,
            artwork2.title
        )
        self.assertEqual(
            titles[2].text,
            artwork1.title
        )

        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-shared-zip'))
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-add')
        )

        # Shared artwork only on the Shared Artwork page
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )
        titles = self.selenium.find_elements_by_css_selector('.artwork-title')
        self.assertEqual(
            titles[0].text,
            artwork3.title
        )
        self.assertEqual(
            titles[1].text,
            artwork2.title
        )
        self.assertEqual(
            titles[2].text,
            artwork1.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-shared-zip'))
        )

    def test_private_artwork_author_list(self):

        # private artwork is not visible to public
        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        list_path = reverse('artwork-author-list', kwargs={'author': self.user.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            0
        )

        list_path = reverse('artwork-author-list', kwargs={'author': self.staff_user.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            0
        )

        list_path = reverse('artwork-author-list', kwargs={'author': self.super_user.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            0
        )

    def test_shared_artwork_author_list(self):

        # Shared artwork is visible to public
        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', shared=1, author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', shared=1, author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', shared=1, author=self.super_user)

        list_kwargs = {'author': self.user.id}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork1.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        list_kwargs['shared'] = 1
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-author-list-zip', kwargs=list_kwargs))
        )


        list_kwargs = {'author': self.staff_user.id}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork2.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        list_kwargs['shared'] = 1
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-author-list-zip', kwargs=list_kwargs))
        )

        list_kwargs = {'author': self.super_user.id}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork3.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        list_kwargs['shared'] = 1
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-author-list-zip', kwargs=list_kwargs))
        )


    def test_studio_artwork_list(self):

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        # My Studio URL redirects to login page for unauthenticated users
        studio_path = reverse('artwork-studio')
        studio_url = '%s%s' % (self.live_server_url, studio_path)
        with wait_for_page_load(self.selenium):
            self.selenium.get(studio_url)
        login_url = '%s%s?next=%s' % (self.live_server_url, reverse('login'), studio_path)
        self.assertEqual(self.selenium.current_url, login_url)

        # My Studio URL redirects to author list for authenticated users
        
        # Student login
        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(studio_url)
        list_kwargs = {'author': self.user.id, 'shared': 0}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork1.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-author-list-zip', kwargs=list_kwargs))
        )

        # Staff login
        self.performLogin(user='staff')
        with wait_for_page_load(self.selenium):
            self.selenium.get(studio_url)
        list_kwargs = {'author': self.staff_user.id, 'shared': 0}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork2.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-author-list-zip', kwargs=list_kwargs))
        )

        # Super login
        self.performLogin(user='super')
        with wait_for_page_load(self.selenium):
            self.selenium.get(studio_url)
        list_kwargs = {'author': self.super_user.id, 'shared': 0}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork3.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-author-list-zip', kwargs=list_kwargs))
        )

    def test_my_artwork_author_list(self):

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        # Author list shows only shared artwork
        list_kwargs = {'author':self.user.id}
        list_url = '%s%s' % (self.live_server_url, reverse('artwork-author-list', kwargs=list_kwargs))

        # Student user
        self.performLogin(user="student")
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            0
        )

        artwork1.shared = 1
        artwork1.save()
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork1.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        list_kwargs['shared'] = 1
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-author-list-zip', kwargs=list_kwargs))
        )

        # Staff user
        self.performLogin(user="staff")
        list_kwargs = {'author':self.staff_user.id}
        list_url = '%s%s' % (self.live_server_url, reverse('artwork-author-list', kwargs=list_kwargs))
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            0
        )
        artwork2.shared = 1
        artwork2.save()
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork2.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        list_kwargs['shared'] = 1
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-author-list-zip', kwargs=list_kwargs))
        )

        # Super user
        self.performLogout()
        self.performLogin(user="super")
        list_kwargs = {'author':self.super_user.id}
        list_url = '%s%s' % (self.live_server_url, reverse('artwork-author-list', kwargs=list_kwargs))
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            0
        )
        artwork3.shared = 1
        artwork3.save()
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork3.title
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#download-all')),
            1
        )
        download_form = self.selenium.find_elements_by_css_selector('#download-all-form')
        self.assertEqual(
            len(download_form),
            1
        )
        list_kwargs['shared'] = 1
        self.assertEqual(
            download_form[0].get_attribute('action'),
            '%s%s' % (self.live_server_url, reverse('artwork-author-list-zip', kwargs=list_kwargs))
        )

    def test_add_artwork_link(self):

        list_path = reverse('artwork-list')
        self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-add')
        )


class SubmittedArtworkListTests(SeleniumTestCase):

    def setUp(self):
        super(SubmittedArtworkListTests, self).setUp()

        self.artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        self.artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.user)
        self.exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.user)
        self.submission1 = Submission.objects.create(
            artwork=self.artwork1,
            exhibition=self.exhibition,
            submitted_by=self.user)
        vote1 = Vote.objects.create(submission=self.submission1,
            status=Vote.THUMBS_UP, voted_by=self.user)
        self.submission2 = Submission.objects.create(
            artwork=self.artwork2,
            exhibition=self.exhibition,
            submitted_by=self.user)

        self.artwork1 = Artwork.objects.get(id=self.artwork1.id)
        self.artwork2 = Artwork.objects.get(id=self.artwork2.id)

    def test_submitted_artwork_list(self):
        # Can see submitted artwork in list
        list_path = reverse('artwork-list')
        self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            2
        )

        # Can see submission URL, not artwork URL
        view_artwork1_url = '%s%s' % (self.live_server_url, 
            reverse('submission-view', kwargs={'pk': self.artwork1.shared}))
        self.assertEqual(
            self.selenium.find_element_by_link_text(self.artwork1.title).get_attribute('href'),
            view_artwork1_url
        )
        view_artwork2_url = '%s%s' % (self.live_server_url, 
            reverse('submission-view', kwargs={'pk': self.artwork2.shared}))
        self.assertEqual(
            self.selenium.find_element_by_link_text(self.artwork2.title).get_attribute('href'),
            view_artwork2_url
        )

        # Can see voting block for both artworks
        votes = self.selenium.find_elements_by_css_selector('.artwork-votes')
        self.assertEqual(len(votes), 2)

        # anonymous users see login link
        login_path = reverse('login')
        login_url = '%s%s?next=%s' % (self.live_server_url, login_path, list_path)

        vote1_link = self.selenium.find_element_by_id('vote-%d' % self.submission1.id)
        self.assertEqual(vote1_link.get_attribute('href'), login_url)

        vote2_link = self.selenium.find_element_by_id('vote-%d' % self.submission2.id)
        self.assertEqual(vote1_link.get_attribute('href'), login_url)

        # Click on a vote link to login and return to list
        with wait_for_page_load(self.selenium):
            vote1_link.click()
        self.assertLogin(next_path=list_path)

        # Vote links have been changed to like/unlike links
        vote1_link = self.selenium.find_element_by_id('vote-%d' % self.submission1.id)
        self.assertEqual(vote1_link.get_attribute('class'), 'post-vote unlike')

        vote2_link = self.selenium.find_element_by_id('vote-%d' % self.submission2.id)
        self.assertEqual(vote2_link.get_attribute('class'), 'post-vote like')


        # Click both vote links to toggle the votes
        vote1_link.click()
        time.sleep(2)
        self.assertEqual(vote1_link.get_attribute('class'), 'post-vote like')

        vote2_link.click()
        time.sleep(2)
        self.assertEqual(vote2_link.get_attribute('class'), 'post-vote unlike')


        # Reload the page to ensure the votes were updated
        self.selenium.get('%s%s' % (self.live_server_url, list_path))
        vote1_link = self.selenium.find_element_by_id('vote-%d' % self.submission1.id)
        self.assertEqual(vote1_link.get_attribute('class'), 'post-vote like')

        vote2_link = self.selenium.find_element_by_id('vote-%d' % self.submission2.id)
        self.assertEqual(vote2_link.get_attribute('class'), 'post-vote unlike')


class ArtworkViewIntegrationTests(SeleniumTestCase):

    def test_404_artwork_view(self):
        view_path = reverse('artwork-view', kwargs={'pk': 1})
        view_url = '%s%s' % (self.live_server_url, view_path)
        self.selenium.get(view_url)
        error_404 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_404.text, 'Not Found'
        )

    def test_own_artwork_view(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        view_url = '%s%s' % (self.live_server_url, view_path)

        # Public cannot see unshared artwork, redirects to login
        self.selenium.get(view_url)

        # Author can see it
        self.assertLogin(view_path)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

        # Staff cannot
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

        # Super cannot
        self.performLogout()
        self.performLogin(user="super")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

    def test_shared_artwork_view(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=3, author=self.user)
        view_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': artwork.id}))

        # Public can see shared artwork
        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

        # Owner can see it
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

        # Staff can see it
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

        # Super can see it
        self.performLogout()
        self.performLogin(user="super")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

    def test_private_artwork_links(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        # Public can't see artwork
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        view_url = '%s%s' % (self.live_server_url, view_path)

        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        # and no save, edit, delete
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector, ('.play')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector, ('.pause')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector, ('.paused')
        )

        # Owner can see it
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        # with in-page editing
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('save_artwork')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('play')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('pause')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector, ('.paused')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        # and delete links
        self.assertIsNotNone(
            self.selenium.find_element_by_link_text, ('DELETE')
        )
        # and clicking on delete redirects to expected page
        self.selenium.find_element_by_link_text('DELETE').click()
        self.assertEqual(self.selenium.current_url, 
            '%s%s' % (self.live_server_url, reverse('artwork-delete', kwargs={'pk': artwork.id})))


        # Staff can't see it
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        # and no save, edit, delete
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('play')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('pause')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector, ('.paused')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )

        # Super can't see it
        self.performLogout()
        self.performLogin(user="super")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        # and no save, edit, delete
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('play')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('pause')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector, ('.paused')
        )

    def test_shared_artwork_links(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=3, author=self.user)

        # Public can see shared artwork
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        view_url = '%s%s' % (self.live_server_url, view_path)

        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        # and no save, edit, delete
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('play')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('pause')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector, ('.paused')
        )

        # Owner can see it
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        # with in-page editing
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('save_artwork')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('play')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('pause')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector, ('.paused')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        # and no delete links
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )

        # Staff can see it
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        # and no save, edit, delete
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('play')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('pause')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector, ('.paused')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )

        # Super can see it
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        # and no save, edit, delete
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('play')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id, ('pause')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector, ('.paused')
        )

    def test_artwork_share_url(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        view_url = '%s%s' % (self.live_server_url, view_path)

        # Public can't see shared artwork
        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )

        # Owner can, but no share link shown until Artwork is shared.
        self.assertLogin(view_path)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.share-link')),
            0
        )

        # Share the artwork shared to see the share link
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='goes here',
            author=self.staff_user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=self.user)

        artwork = Artwork.objects.get(pk=artwork.id)
        self.assertEqual(artwork.shared, submission.id)

        submission_path = reverse('submission-view', kwargs={'pk': artwork.shared})
        submission_url = '%s%s' % (self.live_server_url, submission_path)

        with wait_for_page_load(self.selenium):
            self.selenium.get(submission_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.share-link')),
            1
        )

        # Ensure that visiting the share_link redirects back to the submission view url
        share_link = self.selenium.find_element_by_css_selector('.share-link').text
        self.selenium.get(share_link)
        self.assertEqual(self.selenium.current_url, submission_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.share-link')),
            1
        )

        # Un-share the artwork, logout, and ensure share link 404s
        submission.delete()
        artwork = Artwork.objects.get(pk=artwork.id)
        self.assertEqual(artwork.shared, 0)

        with wait_for_page_load(self.selenium):
            self.selenium.get(share_link)
        error_404 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_404.text, 'Not Found', self.selenium.page_source
        )

        # even when logged in
        self.performLogout()
        self.selenium.get(share_link)
        error_404 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_404.text, 'Not Found', self.selenium.page_source
        )


class ArtworkCodeViewIntegrationTests(SeleniumTestCase):

    def test_404_artwork_view(self):
        code_path = reverse('artwork-code', kwargs={'pk': 1})
        code_url = '%s%s' % (self.live_server_url, code_path)
        self.selenium.get(code_url)
        error_404 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_404.text, 'Not Found'
        )

    def test_own_artwork_view(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        code_path = reverse('artwork-code', kwargs={'pk': artwork.id})
        code_url = '%s%s' % (self.live_server_url, code_path)

        # Public cannot see unshared artwork
        self.selenium.get(code_url)

        # Note: we can't test the actual file download with selenium, but we can
        # ensure we were redirected to login.
        login_url = '%s%s?next=%s' % (self.live_server_url, reverse('login'), code_path)
        self.assertEqual(self.selenium.current_url, login_url)

        # Staff cannot
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(code_url)
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

        # Super cannot
        self.performLogout()
        self.performLogin(user="super")
        with wait_for_page_load(self.selenium):
            self.selenium.get(code_url)
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

    def test_shared_artwork_view(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=3, author=self.user)
        code_url = '%s%s' % (self.live_server_url, reverse('artwork-code', kwargs={'pk': artwork.id}))

        self.performLogout()
        self.assertEqual(self.selenium.current_url, '%s/' % self.live_server_url)

        # Public can see shared artwork
        # Note: we can't test the actual file download with selenium, but we can
        # test the returned url.
        # Note 2: Visiting a link containing a file download does not change the
        # current URL.
        self.selenium.get(code_url)
        self.assertEqual(self.selenium.current_url, '%s/' % self.live_server_url)

        # Owner can see it
        self.performLogin()
        self.selenium.get(code_url)
        self.assertEqual(self.selenium.current_url, '%s/' % self.live_server_url)

        # Staff can see it
        self.performLogout()
        self.performLogin(user="staff")
        self.selenium.get(code_url)
        self.assertEqual(self.selenium.current_url, '%s/' % self.live_server_url)

        # Super can see it
        self.performLogout()
        self.performLogin(user="super")
        self.selenium.get(code_url)
        self.assertEqual(self.selenium.current_url, '%s/' % self.live_server_url)

    def test_download_code_link(self):
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=3, author=self.user)
        code_url = '%s%s' % (self.live_server_url, reverse('artwork-code', kwargs={'pk': artwork.id}))

        # download link showed on artwork view page
        view_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': artwork.id}))
        self.selenium.get(view_url)
        self.assertEqual(
            self.selenium.find_element_by_link_text('DOWNLOAD').get_attribute('href'),
            code_url
        )

        # download link showed on artwork edit page
        edit_url = '%s%s' % (self.live_server_url, reverse('artwork-edit', kwargs={'pk': artwork.id}))
        self.selenium.get(edit_url)
        self.assertEqual(
            self.selenium.find_element_by_link_text('DOWNLOAD').get_attribute('href'),
            code_url
        )


class ArtworkRenderViewIntegrationTests(SeleniumTestCase):

    def test_artwork_render(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        render_path = reverse('artwork-render', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, render_path))

        # Render page must be iframed to actually render code

        # Should show not-rendered div
        self.assertEqual(self.get_style_property('artwork-not-rendered', 'display'), 'block')

        # .. instead of the rendered div
        self.assertEqual(self.get_style_property('artwork-rendered', 'display'), 'none')

        script_code = self.selenium.find_element_by_id('script-preview').get_attribute('innerHTML');
        self.assertEqual(
            script_code, ''
        )


class ArtworkAddIntegrationTests(SeleniumTestCase):

    def test_add_artwork(self):

        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path)

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys('// code goes here')

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_artwork').click()

        # add action redirects to view/edit url
        edit_path = reverse('artwork-view', kwargs={'pk': 1})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, edit_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

    def test_add_artwork_cancel(self):

        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path)

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('do not submit')
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys('// code goes here')

        # No more 'cancel' link on New Artwork page
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_cancel')
        )

        # But if we go to the list url, our artwork is not there.
        list_path = reverse('artwork-list')
        self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )


class ArtworkCloneIntegrationTests(SeleniumTestCase):

    def setUp(self):
        super(ArtworkCloneIntegrationTests, self).setUp()

        self.artwork = Artwork.objects.create(
            title='Title bar',
            code='// code goes here',
            author=self.user,
        )
        # Share the artwork shared to see the share link
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='goes here',
            author=self.staff_user)
        submission = Submission.objects.create(
            artwork=self.artwork,
            exhibition=exhibition,
            submitted_by=self.user)
        self.artwork = Artwork.objects.get(pk=self.artwork.id)

        self.clone_path = reverse('artwork-clone', kwargs={'pk': self.artwork.id })
        self.clone_url = '%s%s' % (self.live_server_url, self.clone_path)

        self.view_url = '%s%s' % (self.live_server_url, 
            reverse('artwork-view', kwargs={'pk': self.artwork.id}))
        self.list_url = '%s%s' % (self.live_server_url, reverse('artwork-list'))


    def test_clone_artwork(self):

        # Ensure only 1 artwork in the list
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            self.artwork.title
        )

        # clone viewlredirects to login form
        self.selenium.get(self.clone_url)
        self.assertLogin(self.clone_path)

        # login form redirects to clone form
        self.assertEqual(
            self.selenium.find_element_by_id('id_title').get_attribute('value'),
            '[Clone] %s' % self.artwork.title
        )
        self.assertEqual(
            self.selenium.find_element_by_id('id_code').get_attribute('value'),
            '''/* Cloned from %s */
%s''' % (self.view_url, self.artwork.code)
        )

        title_field = self.selenium.find_element_by_id('id_title')
        title_field.clear()
        cloned_title = 'Testing clone update'
        title_field.send_keys('Testing clone update')

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_artwork').click()

        # clone action redirects to view url for cloned artwork
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

        # Ensure changes were saved
        self.assertEqual(
            self.selenium.find_element_by_id('id_title').get_attribute('value'),
            cloned_title
        )
        self.assertEqual(
            self.selenium.find_element_by_id('id_code').get_attribute('value'),
            '''/* Cloned from %s */
%s''' % (self.view_url, self.artwork.code)
        )

        # Ensure 2 artwork in the (logged-in) list
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            2
        )
        titles = self.selenium.find_elements_by_css_selector('.artwork-title')
        self.assertEqual(
            len(titles),
            2
        )
        self.assertEqual(
            titles[0].text,
            cloned_title
        )
        self.assertEqual(
            titles[1].text,
            self.artwork.title
        )

        # Logout, and ensure there's only one (shared setting does not get Cloned)
        self.performLogout()
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        titles = self.selenium.find_elements_by_css_selector('.artwork-title')
        self.assertEqual(
            len(titles),
            1
        )
        self.assertEqual(
            titles[0].text,
            self.artwork.title
        )
        
    def test_clone_artwork_cancel(self):

        # Ensure only 1 artwork in the list
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            self.artwork.title
        )

        # clone view redirects to login form
        self.selenium.get(self.clone_url)
        self.assertLogin(self.clone_path)

        # login form redirects to clone form
        self.assertEqual(
            self.selenium.find_element_by_id('id_title').get_attribute('value'),
            '[Clone] %s' % self.artwork.title
        )
        self.assertEqual(
            self.selenium.find_element_by_id('id_code').get_attribute('value'),
            '''/* Cloned from %s */
%s''' % (self.view_url, self.artwork.code)
        )

        title_field = self.selenium.find_element_by_id('id_title')
        title_field.clear()
        cloned_title = 'Testing clone update'
        title_field.send_keys('Testing clone update')

        # Hit 'cancel' link on clone page
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_cancel').click()

        # cancel clone action redirects to absolute url of original artwork
        self.assertEqual(self.selenium.current_url, 
            '%s%s' % (self.live_server_url, self.artwork.get_absolute_url()))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

        # Ensure changes were not saved
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            self.artwork.title
        )

        # Ensure 1 artwork in the (logged-in) list
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        titles = self.selenium.find_elements_by_css_selector('.artwork-title')
        self.assertEqual(
            len(titles),
            1
        )
        self.assertEqual(
            titles[0].text,
            self.artwork.title
        )

        # Logout, and ensure there's still only one
        self.performLogout()
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        titles = self.selenium.find_elements_by_css_selector('.artwork-title')
        self.assertEqual(
            len(titles),
            1
        )
        self.assertEqual(
            titles[0].text,
            self.artwork.title
        )


class ArtworkEditIntegrationTests(SeleniumTestCase):

    def test_author_edit_unshared_artwork(self):
        
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})

        # edit redirects to login form
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # Login as author
        self.assertLogin(edit_path)

        # Update the title text
        self.selenium.find_element_by_id('id_title').clear()
        self.selenium.find_element_by_id('id_title').send_keys('updated title')

        # Save succeeds as author
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_artwork').click()
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))

        # Wait for iframe to load
        time.sleep(5)

        # ensure edit was saved
        artwork = Artwork.objects.get(pk=artwork.id)
        self.assertEqual(
            artwork.title,
            'updated title'
        )

    def test_author_cant_edit_shared_artwork(self):
        
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=1, author=self.user)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        edit_url = '%s%s' % (self.live_server_url, edit_path)
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})

        # Edit view for shared artwork allowed
        with wait_for_page_load(self.selenium):
            self.selenium.get(edit_url)
        self.assertEqual(self.selenium.current_url, edit_url)

        # But no save button shown
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )

        # Login as author
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get(edit_url)

        # Still no Save button; can't edit shared Artwork
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )

        # Cannot update the title text
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('id_title')
        )


    def test_non_author_cant_edit_unshared_artwork(self):
        
        # Create unshared artwork owned by another student user
        otherUser = get_user_model().objects.create(username='other')
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=otherUser)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})

        # edit redirects to login form
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # Login as student
        self.assertLogin(edit_path)

        # Permission denied
        self.assertEqual(
            self.selenium.find_element_by_tag_name('h1').text, '403 Forbidden'
        )

    def test_non_author_cant_edit_shared_artwork(self):
        
        # Create unshared artwork owned by another student user
        otherUser = get_user_model().objects.create(username='other')
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=1, author=otherUser)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        edit_url = '%s%s' % (self.live_server_url, edit_path)
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})

        # Edit view for shared artwork allowed
        self.selenium.get(edit_url)
        self.assertEqual(self.selenium.current_url, edit_url)

        # But no save button shown
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )

        # Login as student
        self.performLogin()
        self.selenium.get(edit_url)
        self.assertEqual(self.selenium.current_url, edit_url)

        # Still no save button shown
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )

    def test_staff_cant_edit_shared_artwork(self):
        
        # Create unshared artwork owned by another student user
        otherUser = get_user_model().objects.create(username='other')
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=1, author=otherUser)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        edit_url = '%s%s' % (self.live_server_url, edit_path)
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})

        # Edit view for shared artwork allowed
        self.selenium.get(edit_url)
        self.assertEqual(self.selenium.current_url, edit_url)

        # But no save button shown
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )

        # Login as student
        self.performLogin("staff")
        self.selenium.get(edit_url)
        self.assertEqual(self.selenium.current_url, edit_url)

        # Still no save button shown
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )

    def test_super_edit_shared_artwork(self):
        
        # Create unshared artwork owned by another student user
        otherUser = get_user_model().objects.create(username='other')
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=1, author=otherUser)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        edit_url = '%s%s' % (self.live_server_url, edit_path)
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})

        # Edit view for shared artwork allowed
        self.selenium.get(edit_url)
        self.assertEqual(self.selenium.current_url, edit_url)

        # But no save button shown
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_artwork')
        )

        # Login as superuser
        self.performLogin("super")
        self.selenium.get(edit_url)
        self.assertEqual(self.selenium.current_url, edit_url)

        # Save button shown
        self.assertIsNotNone(
            self.selenium.find_element_by_id('save_artwork')
        )

        # But save fails
        self.selenium.find_element_by_id('id_title').clear()
        self.selenium.find_element_by_id('id_title').send_keys('updated title')

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_artwork').click()
        self.assertEqual(
            self.selenium.find_element_by_tag_name('h1').text, '403 Forbidden'
        )

        # ensure edit was not saved
        artwork = Artwork.objects.get(pk=artwork.id)
        self.assertEqual(
            artwork.title,
            'Title bar'
        )

    def test_edit_artwork_cancel(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # edit redirects to login form
        self.assertLogin(edit_path)

        # Update the title text
        self.selenium.find_element_by_id('id_title').clear()
        self.selenium.find_element_by_id('id_title').send_keys('updated title')

        # Click cancel
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_cancel').click()

        # Cancel returns us to the view page
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))

        # edit was canceled
        artwork = Artwork.objects.get(pk=artwork.id)
        self.assertEqual(
            artwork.title,
            'Title bar'
        )

    def test_not_author_edit(self):
        # 1. Create a second user
        otherUser = get_user_model().objects.create(username='other')

        # 2. Create an artwork authored by the second user
        artwork = Artwork.objects.create(title='Other User artwork', code='// code goes here', author=otherUser)

        # 3. Login
        self.performLogin()

        # 3. Try to edit artwork via GET request
        edit_url = '%s%s' % (self.live_server_url, reverse('artwork-edit', kwargs={'pk': artwork.id}))
        self.selenium.get(edit_url)
        
        # 4. Ensure permission denied
        self.assertEqual(self.selenium.current_url, edit_url)
        self.assertEqual(
            self.selenium.find_element_by_tag_name('h1').text, '403 Forbidden'
        )

    def test_edit_artwork_code(self):

        '''Ensure that the code editor widget communicates changes ok.'''

        title = 'Title bar'
        code = '// code goes here'
        artwork = Artwork.objects.create(title=title, code=code, author=self.user)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # edit redirects to login form
        self.assertLogin(edit_path)

        # Update the title text 
        new_code = ['''void setup() { size(640, 360); }\n''',
                    '''void draw() { background(0); }''',]

        textarea = self.selenium.find_element_by_css_selector('.ace_text-input')
        textarea.click()
        textarea.send_keys(Keys.CONTROL, 'a') # select all
        textarea.send_keys(Keys.CONTROL, 'x') # delete

        # Editor will handle indenting and ending braces
        textarea.send_keys(new_code[0])
        textarea.send_keys(new_code[1])

        # form POSTs replace newlines with CRLF, so we need to too.
        new_code = ''.join(new_code)
        new_code = new_code.replace('\n', '\r\n')

        # Click Save
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_artwork').click()

        # save returns us to the view page
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))

        # ensure edit was saved
        artwork = Artwork.objects.get(pk=artwork.id)
        self.assertEqual(
            artwork.title,
            title
        )
        self.assertEqual(
            artwork.code,
            new_code
        )


class ArtworkDeleteIntegrationTests(SeleniumTestCase):

    def test_delete_artwork(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        delete_path = reverse('artwork-delete', kwargs={'pk':artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, delete_path))

        # delete redirects to login form
        self.assertLogin(delete_path)

        # login form redirects to delete form
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('artwork_delete').click()

        # delete action redirects to list url
        list_path = reverse('artwork-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        
    def test_delete_artwork_cancel(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        delete_path = reverse('artwork-delete', kwargs={'pk':artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, delete_path))

        # delete redirects to login form
        self.assertLogin(delete_path)

        # login form redirects to delete form
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('artwork_do_not_delete').click()

        # delete action redirects to view url
        view_path = artwork.get_absolute_url()
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1,
        )

        # Check artwork still exists in list
        list_path = reverse('artwork-list')
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1,
            self.selenium.page_source
        )

    def test_not_author_delete(self):
        # 1. Create a second user
        otherUser = get_user_model().objects.create(username='other')

        # 2. Create an artwork authored by the second user
        artwork = Artwork.objects.create(title='Other User artwork', code='// code goes here', author=otherUser)

        # 3. Login
        self.performLogin()

        # 3. Try to delete artwork via GET request
        delete_url = '%s%s' % (self.live_server_url, reverse('artwork-delete', kwargs={'pk': artwork.id}))
        self.selenium.get(delete_url)
        
        # 4. Ensure we're redirected back to view
        view_url = '%s%s' % (self.live_server_url, artwork.get_absolute_url())
        self.assertEqual(self.selenium.current_url, view_url)


class ArtworkRender_NoHTML5Iframe_IntegrationTests(NoHTML5SeleniumTestCase):
    '''Tests the artwork rendering in a browser that does not support HTML5 iframe sandbox'''

    def test_artwork_render_compile_error(self):

        # Create artwork with bad code, and share it
        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)

        render_path = reverse('artwork-render', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, render_path))

        # Render page must be iframed to do its job
        # Should show not-rendered div
        self.assertEqual(self.get_style_property('artwork-not-rendered', 'display'), 'block')

        # .. instead of the rendered div
        self.assertEqual(self.get_style_property('artwork-rendered', 'display'), 'none')

        script_code = self.selenium.find_element_by_id('script-preview').get_attribute('innerHTML');
        self.assertEqual(
            script_code, ''
        )

        # We should get no errors shown
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, '')

        # and no errors in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_view_artwork_compile_error(self):

        # Create artwork with bad code, and share it
        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)

        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, view_path))

        # The paused overlay should be hidden
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork.id).is_displayed())

        # We should get no iframes loaded
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_tag_name, ('iframe')
        )

        # and no errors in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

        # We should be able to see the HTML5 support warning text
        upgradeBrowser = self.selenium.find_element_by_css_selector('.artwork h4')
        self.assertEqual(
            upgradeBrowser.text,
            'Please upgrade your browser'
        )

    def test_artwork_list_compile_error(self):

        # Create 3 artworks, 2 with bad code, and share them
        artwork1 = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)
        artwork2 = Artwork.objects.create(title='Good test code1', code='// good code!', shared=1, author=self.user)
        artwork3 = Artwork.objects.create(title='Bad test code2', code='still bad code!', shared=1, author=self.user)

        list_path = reverse('artwork-list')
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )

        # The paused overlays should be hidden
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork1.id).is_displayed())
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork2.id).is_displayed())
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork3.id).is_displayed())

        # We should get no iframes loaded
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_tag_name, ('iframe')
        )

        # and no errors in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

        # We should be able to see the HTML5 support warning text
        upgradeBrowser = self.selenium.find_elements_by_css_selector('.artwork h4')
        self.assertEqual(len(upgradeBrowser), 3);
        self.assertEqual(
            upgradeBrowser[0].text,
            'Please upgrade your browser'
        )

    def test_add_artwork_compile_error(self):
        '''Add requires HTML5 iframe'''
        
        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # Add redirects to login form
        self.assertLogin(add_path)

        # The paused overlay won't exist
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_css_selector, ('.paused')
        )

        # We should get no iframes loaded
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_tag_name, ('iframe')
        )

        # and no errors in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

        # We should be able to see the HTML5 support warning text
        upgradeBrowser = self.selenium.find_elements_by_css_selector('.artwork h4')
        self.assertEqual(len(upgradeBrowser), 1);
        self.assertEqual(
            upgradeBrowser[0].text,
            'Please upgrade your browser'
        )


class ArtworkRender_HTML5Iframe_IntegrationTests(SeleniumTestCase):
    '''Tests the artwork rendering in a browser that does support HTML5 iframe sandbox'''

    def test_artwork_render_compile_error(self):

        # Create artwork with bad code, and share it
        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)

        render_path = reverse('artwork-render', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, render_path))

        # Render page must be iframed to do its job
        # Should show not-rendered div
        self.assertEqual(self.get_style_property('artwork-not-rendered', 'display'), 'block')

        # .. instead of the rendered div
        self.assertEqual(self.get_style_property('artwork-rendered', 'display'), 'none')

        script_code = self.selenium.find_element_by_id('script-preview').get_attribute('innerHTML');
        self.assertEqual(
            script_code, ''
        )

        # We should get no error shown
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, '')

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_artwork_list_compile_error(self):

        # Create 3 artworks, 2 with bad code, and share them
        artwork1 = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)
        artwork2 = Artwork.objects.create(title='Good test code1', code='// good code!', shared=1, author=self.user)
        artwork3 = Artwork.objects.create(title='Bad test code2', code='still bad code!', shared=1, author=self.user)

        list_path = reverse('artwork-list')
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )

        # The paused overlays should be shown
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork1.id).is_displayed())
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork2.id).is_displayed())
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork3.id).is_displayed())

        # Push play-all to start all animations
        self.selenium.find_element_by_id('play-all').click()
        time.sleep(1)

        # The paused overlays should be hidden
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork1.id).is_displayed())
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork2.id).is_displayed())
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork3.id).is_displayed())

        # We should get 2 errors shown for artworks 1 & 3
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork1.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork1.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork3.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork3.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # and no error shown for artwork 2
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork2.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork2.id)
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_artwork_list_play_buttons(self):

        # Create 3 artworks, 2 with bad code, and share them
        artwork1 = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)
        artwork2 = Artwork.objects.create(title='Good test code1', code='// good code!', shared=1, author=self.user)
        artwork3 = Artwork.objects.create(title='Bad test code2', code='still bad code!', shared=1, author=self.user)

        list_path = reverse('artwork-list')
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )

        # The paused overlays should be shown
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork1.id).is_displayed())
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork2.id).is_displayed())
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork3.id).is_displayed())

        # We should get no errors yet
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork1.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork1.id)
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()

        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork3.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork3.id)
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()

        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork2.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork2.id)
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

        # Play 1
        # Hit paused-1's play link
        self.selenium.find_element_by_css_selector('#paused-%s a' % artwork1.id).click()
        time.sleep(1)

        # The first paused overlay should be hidden, the others should be shown
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork1.id).is_displayed())
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork2.id).is_displayed())
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork3.id).is_displayed())

        # We should get errors shown for artwork 1
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork1.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork1.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # and no error for artwork 3
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork3.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork3.id)
        self.assertEqual(error.text, '');
        self.selenium.switch_to.default_content()

        # and no error shown for artwork 2
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork2.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork2.id)
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()


        # Play 2
        # Hit paused-2's play link
        self.selenium.find_element_by_css_selector('#paused-%s a' % artwork2.id).click()
        time.sleep(1)

        # The first 2 paused overlays should be hidden, the other should be shown
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork1.id).is_displayed())
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork2.id).is_displayed())
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork3.id).is_displayed())

        # We should get errors shown for artwork 1
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork1.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork1.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # and no error for artwork 3
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork3.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork3.id)
        self.assertEqual(error.text, '');
        self.selenium.switch_to.default_content()

        # and no error shown for artwork 2
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork2.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork2.id)
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()


        # Play 3
        # Hit paused-1's play link
        self.selenium.find_element_by_css_selector('#paused-%s a' % artwork3.id).click()
        time.sleep(1)

        # All the paused overlays should be hidden now
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork1.id).is_displayed())
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork2.id).is_displayed())
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork3.id).is_displayed())

        # We should get 2 errors shown for artworks 1 & 3
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork1.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork1.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork3.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork3.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # and no error shown for artwork 2
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork2.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork2.id)
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_artwork_view_compile_error(self):

        # Create artwork with bad code, and share it
        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)

        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, view_path))

        # HTML5 attributes should be detectable via javascript
        self.assertTrue(self.selenium.execute_script('return Modernizr.sandbox;'))

        # The paused overlay should be displayed
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork.id).is_displayed())

        # Push play to start the animation
        self.selenium.find_element_by_id('play').click()
        time.sleep(1)

        # The paused overlay should be hidden
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork.id).is_displayed())

        # Ensure error is showing in iframe
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_edit_artwork_compile_error(self):

        # Create artwork with bad code, and share it
        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # The paused overlay should be displayed
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork.id).is_displayed())

        # Push play to start the animation
        self.selenium.find_element_by_id('play').click()
        time.sleep(1)

        # The paused overlay should be hidden
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % artwork.id).is_displayed())

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_add_artwork_compile_error(self):
        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))
        # add redirects to login form
        self.assertLogin(add_path)

        # The paused overlay won't even exist
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_css_selector, ('.paused')
        )

        # Push play to start the animation while we send keys
        self.selenium.find_element_by_id('play').click()
 
        self.selenium.find_element_by_id('id_title').send_keys('bad submission')
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys("bad code!")

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % '')
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % '')
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)


class ArtworkRenderHtmlEntities(SeleniumTestCase):

    def test_artwork_with_unencoded_html_entity_spaced(self):
        '''Testing with i< limit'''
        code = '''
int limit = 3;
int go = true;
for (int i=0; i< limit && go; i+=1) { 
    rect(i*10,i*10,10-(i*10),10-(i*10)); 
}
'''
        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))
        # add redirects to login form
        self.assertLogin(add_path)

        # Send the code to the text editor
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys(code)

        # Push play to start the animation
        self.selenium.find_element_by_id('play').click()
        time.sleep(1)

        # We should have no error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % '')
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % '')
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_artwork_with_unencoded_html_entity_no_space(self):
        '''Testing with i<limit'''
        code = '''
int limit = 3;
int go = true;
for (int i=0; i<limit && go; i+=1) { 
    rect(i*10,i*10,10-(i*10),10-(i*10)); 
}
'''
        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))
        # add redirects to login form
        self.assertLogin(add_path)

        # Send the code to the text editor
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys(code)

        # Push play to start the animation
        self.selenium.find_element_by_id('play').click()
        time.sleep(1)

        # We should have no error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % '')
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % '')
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_artwork_with_encoded_html_entity_no_space(self):
        '''Testing with i&lt;limit'''
        code = '''
int limit = 3;
int go = true;
for (int i=0; i&lt;limit &amp;&amp;go; i+=1) { 
    rect(i*10,i*10,10-(i*10),10-(i*10)); 
}
'''
        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))
        # add redirects to login form
        self.assertLogin(add_path)

        # Send the code to the text editor
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys(code)

        # Push play to start the animation
        self.selenium.find_element_by_id('play').click()
        time.sleep(1)

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % '')
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % '')
        self.assertEqual(error.text, 'lt is not defined')
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_artwork_with_encoded_html_entity_spaced(self):
        '''Testing with i&lt; limit'''
        code = '''
int limit = 3;
int go = true;
for (int i=0; i&lt; limit &amp;&amp; go; i+=1) { 
    rect(i*10,i*10,10-(i*10),10-(i*10)); 
}
'''
        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))
        # add redirects to login form
        self.assertLogin(add_path)

        # Send the code to the text editor
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys(code)

        # Push play to start the animation
        self.selenium.find_element_by_id('play').click()
        time.sleep(1)

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % '')
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % '')
        self.assertEqual(error.text, 'lt is not defined')
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_artwork_with_encoded_html_entity_edit_view(self):
        '''Testing with i&lt; limit'''
        code = '''
int limit = 3;
int go = true;
for (int i=0; i&lt; limit &amp;&amp; go; i+=1) { 
    rect(i*10,i*10,10-(i*10),10-(i*10)); 
}
'''
        artwork = Artwork.objects.create(title='Title bar', code=code, author=self.user)
        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))
        # add redirects to login form
        self.assertLogin(edit_path)

        # Push play to start the animation
        self.selenium.find_element_by_id('play').click()
        time.sleep(1)

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, 'lt is not defined')
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)


class ArtworkRenderHtmlEntitiesWithoutEditForm(SeleniumTestCase):

    def test_artwork_with_unencoded_entity_unspaced_before_number(self):
        '''Testing with i<400'''
        code = '''
size(400,300);
for(var i=100;i<400;i+=10)
{
    for(var j=i-50;j<300;j+=10)
    {
        fill(i,j,j-i);
        ellipse(i,j*j/300,7,8+j/15);
        ellipse(400-i,j*j/300,7,8+j/15);
    }
}
'''
        # Create a shared Artwork so we can see non-editing view page
        artwork = Artwork.objects.create(title='Title bar', code=code, author=self.user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='goes here',
            author=self.staff_user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=self.user)

        view_path = reverse('submission-view', kwargs={'pk': submission.id})
        view_url = '%s%s' % (self.live_server_url, view_path)

        self.selenium.get(view_url)

        # Push play to start the animation
        self.selenium.find_element_by_id('play').click()
        time.sleep(1)

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

        # We should have no error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()

    def test_artwork_with_unencoded_entity_spaced_before_number(self):
        '''Testing with i < 400'''
        code = '''
size(400,300);
for(var i=100;i < 400;i+=10)
{
    for(var j=i-50;j<300;j+=10)
    {
        fill(i,j,j-i);
        ellipse(i,j*j/300,7,8+j/15);
        ellipse(400-i,j*j/300,7,8+j/15);
    }
}
'''
        # Create a shared Artwork so we can see non-editing view page
        artwork = Artwork.objects.create(title='Title bar', code=code, author=self.user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='goes here',
            author=self.staff_user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=self.user)

        view_path = reverse('submission-view', kwargs={'pk': submission.id})
        view_url = '%s%s' % (self.live_server_url, view_path)

        self.selenium.get(view_url)

        # Push play to start the animation
        self.selenium.find_element_by_id('play').click()
        time.sleep(1)

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

        # We should have no error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()

    def test_artwork_with_unencoded_entity_list_view(self):
        '''Testing with i<400'''
        code = '''
size(400,300);
for(var i=100;i<400;i+=10)
{
    for(var j=i-50;j<300;j+=10)
    {
        fill(i,j,j-i);
        ellipse(i,j*j/300,7,8+j/15);
        ellipse(400-i,j*j/300,7,8+j/15);
    }
}
'''
        # Create a shared Artwork so we can see non-editing view page
        artwork = Artwork.objects.create(title='Title bar', code=code, author=self.user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='goes here',
            author=self.staff_user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=self.user)

        view_path = reverse('exhibition-view', kwargs={'pk': exhibition.id})
        view_url = '%s%s' % (self.live_server_url, view_path)

        self.selenium.get(view_url)

        # Push play to start the animation
        self.selenium.find_element_by_id('paused-%s' % artwork.id).click()
        time.sleep(1)

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

        # We should have no error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()


class ArtworkRenderCrash(SeleniumTestCase):

    def test_nicks_hanging_artwork(self):
        '''Tests code provided by Nick Faulkner, which was crashing his browser.'''
        code = '''//This code won't work because it's not
//actually Processing.  This is pseudo-code.

for (<initialisation>; <test>; <update>) {
    <instructions>;
}
'''
        artwork = Artwork.objects.create(title='Bad test code1', code=code, shared=1, author=self.user)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # The paused overlay should be displayed
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % artwork.id).is_displayed())

        # Push play to start the animation
        self.selenium.find_element_by_id('play').click()
        time.sleep(1)

        # We get Javascript exceptions thrown when we try to access elements.
        # Nick's code still makes my browser loop infinitely, but the selenium
        # browser doesn't, somehow.  Or we can't detect it.
        self.assertRaises(
            WebDriverException,
            self.selenium.find_element_by_id, ('ace_editor')
        )
        self.assertRaises(
            WebDriverException,
            self.selenium.find_element_by_css_selector, ('.ace_text-input')
        )
        self.assertRaises(
            WebDriverException,
            self.selenium.find_element_by_tag_name, ('iframe')
        )

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)


class ArtworkPlayPauseTests(SeleniumTestCase):

    def test_edit_artwork_overlay_play_pause(self):

        # Create artwork with bad code, and share it
        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        pausedOverlay = self.selenium.find_element_by_id('paused-%s' % artwork.id)
        playBtn = self.selenium.find_element_by_id('play')
        pauseBtn = self.selenium.find_element_by_id('pause')

        # The paused overlay should be displayed
        self.assertTrue(pausedOverlay.is_displayed())

        # The Play button should be enabled
        self.assertFalse(playBtn.get_attribute('disabled'))
        
        # The Pause button should be disabled
        self.assertTrue(pauseBtn.get_attribute('disabled'))


        # Push play link in paused overlay to start the animation
        self.selenium.find_element_by_css_selector('#paused-%s a' % artwork.id).click()
        time.sleep(1)

        # The paused overlay should be hidden
        self.assertFalse(pausedOverlay.is_displayed())

        # The Play button should be disabled
        self.assertTrue(playBtn.get_attribute('disabled'))
        
        # The Pause button should be enabled
        self.assertFalse(pauseBtn.get_attribute('disabled'))

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)


        # Click Pause
        pauseBtn.click()

        # The paused overlay should be hidden
        self.assertFalse(pausedOverlay.is_displayed())

        # The Play button should be enabled
        self.assertFalse(playBtn.get_attribute('disabled'))
        
        # The Pause button should be disabled
        self.assertTrue(pauseBtn.get_attribute('disabled'))

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)


        # Update code
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys("bad code")

        # The paused overlay should be hidden
        self.assertFalse(pausedOverlay.is_displayed())

        # The Play button should be enabled
        self.assertFalse(playBtn.get_attribute('disabled'))
        
        # The Pause button should be disabled
        self.assertTrue(pauseBtn.get_attribute('disabled'))

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)


        # Click Play
        playBtn.click()
        time.sleep(1)

        # The paused overlay should be hidden
        self.assertFalse(pausedOverlay.is_displayed())

        # The Play button should be disabled
        self.assertTrue(playBtn.get_attribute('disabled'))
        
        # The Pause button should be enabled
        self.assertFalse(pauseBtn.get_attribute('disabled'))

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_edit_artwork_play_pause(self):

        # Create artwork with bad code, and share it
        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        pausedOverlay = self.selenium.find_element_by_id('paused-%s' % artwork.id)
        playBtn = self.selenium.find_element_by_id('play')
        pauseBtn = self.selenium.find_element_by_id('pause')

        # The paused overlay should be displayed
        self.assertTrue(pausedOverlay.is_displayed())

        # The Play button should be enabled
        self.assertFalse(playBtn.get_attribute('disabled'))
        
        # The Pause button should be disabled
        self.assertTrue(pauseBtn.get_attribute('disabled'))


        # Click play button
        playBtn.click()
        time.sleep(1)

        # The paused overlay should be hidden
        self.assertFalse(pausedOverlay.is_displayed())

        # The Play button should be disabled
        self.assertTrue(playBtn.get_attribute('disabled'))
        
        # The Pause button should be enabled
        self.assertFalse(pauseBtn.get_attribute('disabled'))

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)


        # Click Pause
        pauseBtn.click()

        # The paused overlay should be hidden
        self.assertFalse(pausedOverlay.is_displayed())

        # The Play button should be enabled
        self.assertFalse(playBtn.get_attribute('disabled'))
        
        # The Pause button should be disabled
        self.assertTrue(pauseBtn.get_attribute('disabled'))

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)


        # Update code
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys("bad code")

        # The paused overlay should be hidden
        self.assertFalse(pausedOverlay.is_displayed())

        # The Play button should be enabled
        self.assertFalse(playBtn.get_attribute('disabled'))
        
        # The Pause button should be disabled
        self.assertTrue(pauseBtn.get_attribute('disabled'))

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)


        # Click Play
        playBtn.click()
        time.sleep(1)

        # The paused overlay should be hidden
        self.assertFalse(pausedOverlay.is_displayed())

        # The Play button should be disabled
        self.assertTrue(playBtn.get_attribute('disabled'))
        
        # The Pause button should be enabled
        self.assertFalse(pauseBtn.get_attribute('disabled'))

        # We should have an error shown
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % artwork.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # no errors reported to the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

