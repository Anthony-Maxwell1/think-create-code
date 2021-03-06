from django.core.urlresolvers import reverse
from selenium.common.exceptions import NoSuchElementException
import time

from artwork.models import Artwork
from exhibitions.models import Exhibition
from submissions.models import Submission
from votes.models import Vote
from django_adelaidex.util.test import SeleniumTestCase, NoHTML5SeleniumTestCase, wait_for_page_load


class SubmissionShowIntegrationTests(SeleniumTestCase):
    def setUp(self):
        super(SubmissionShowIntegrationTests, self).setUp()
        self.exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='goes here',
            author=self.staff_user)
        self.artwork = Artwork.objects.create(
            title='Title bar',
            code='// code goes here',
            author=self.user)

    def test_404(self):
        view_path = reverse('submission-view', kwargs={'pk': 1})
        view_url = '%s%s' % (self.live_server_url, view_path)
        self.selenium.get(view_url)
        error_404 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_404.text, 'Not Found'
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('submission-view-content')
        )
        
    def test_view(self):
        submission = Submission.objects.create(
            artwork=self.artwork,
            exhibition=self.exhibition,
            submitted_by=self.user)

        view_path = reverse('submission-view', kwargs={'pk': submission.id})
        view_url = '%s%s' % (self.live_server_url, view_path)
        self.selenium.get(view_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('submission-view-content'),
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-title')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.share-link')),
            1
        )
        vote_link = self.selenium.find_element_by_id('vote-%s' % submission.id)
        self.assertEqual(vote_link.get_attribute('href'), 
            '%s%s?next=%s' % (self.live_server_url, reverse('login'), view_path))
        self.assertEqual(vote_link.text, '0')
        self.assertEqual(vote_link.get_attribute('title'), 'Sign in to vote')
        self.assertEqual(vote_link.get_attribute('unlike-url'), None)
        self.assertEqual(vote_link.get_attribute('like-url'), None)

        artwork_score = self.selenium.find_element_by_css_selector('.artwork-score')
        self.assertEquals(artwork_score.text, '0')

        self.assertEqual(
            len(self.selenium.find_elements_by_link_text('unshare')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-detail')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-author')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_link_text(self.exhibition.title)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.submission-date')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.code-block')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%d' % self.artwork.id)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('save_artwork')),
            0
        )
        
    def test_author_view(self):
        submission = Submission.objects.create(
            artwork=self.artwork,
            exhibition=self.exhibition,
            submitted_by=self.user)

        self.performLogin()
        view_path = reverse('submission-view', kwargs={'pk': submission.id})
        view_url = '%s%s' % (self.live_server_url, view_path)
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('submission-view-content'),
        )

        vote_link = self.selenium.find_element_by_id('vote-%s' % submission.id)
        self.assertEqual(vote_link.get_attribute('href'), '%s#' % (view_url))
        self.assertEqual(vote_link.text, '0')

        artwork_score = self.selenium.find_element_by_css_selector('.artwork-score')
        self.assertEquals(artwork_score.text, '0')

        self.assertEqual(
            len(self.selenium.find_elements_by_link_text('UNSHARE')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-detail')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-author')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_link_text(self.exhibition.title)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.submission-date')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.code-block')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%d' % self.artwork.id)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('save_artwork')),
            0
        )

    def test_anonymous_votes_view(self):
        submission = Submission.objects.create(
            artwork=self.artwork,
            exhibition=self.exhibition,
            submitted_by=self.user)
        vote = Vote.objects.create(submission=submission,
            status=Vote.THUMBS_UP, voted_by=self.user)

        # anonymous users don't see others' votes, just the score
        view_path = reverse('submission-view', kwargs={'pk': submission.id})
        view_url = '%s%s' % (self.live_server_url, view_path)
        self.selenium.get(view_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('submission-view-content')
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-title')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.share-link')),
            1
        )

        vote_link = self.selenium.find_element_by_id('vote-%s' % submission.id)
        self.assertEqual(vote_link.get_attribute('href'), 
            '%s%s?next=%s' % (self.live_server_url, reverse('login'), view_path))
        self.assertEqual(vote_link.text, '1')
        self.assertEqual(vote_link.get_attribute('title'), 'Sign in to vote')
        self.assertEqual(vote_link.get_attribute('unlike-url'), None)
        self.assertEqual(vote_link.get_attribute('like-url'), None)

        artwork_score = self.selenium.find_element_by_css_selector('.artwork-score')
        self.assertEquals(artwork_score.text, '1')

        self.assertEqual(
            len(self.selenium.find_elements_by_link_text('UNSHARE')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_link_text(' 1')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-detail')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-author')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_link_text(self.exhibition.title)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.submission-date')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.code-block')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%d' % self.artwork.id)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('save_artwork')),
            0
        )

    def test_author_votes_view(self):
        submission = Submission.objects.create(
            artwork=self.artwork,
            exhibition=self.exhibition,
            submitted_by=self.user)
        vote = Vote.objects.create(submission=submission,
            status=Vote.THUMBS_UP, voted_by=self.user)

        view_path = reverse('submission-view', kwargs={'pk': submission.id})
        view_url = '%s%s' % (self.live_server_url, view_path)
        unlike_path = reverse('submission-unlike', kwargs={'submission': submission.id})
        like_path = reverse('submission-like', kwargs={'submission': submission.id})

        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('submission-view-content')
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-title')),
            1
        )

        vote_link = self.selenium.find_element_by_id('vote-%s' % submission.id)
        self.assertEqual(vote_link.get_attribute('href'), '%s#' % (view_url))
        self.assertEqual(vote_link.text, '1')
        self.assertEqual(vote_link.get_attribute('title'), 'unlike')
        self.assertEqual(vote_link.get_attribute('unlike-url'), unlike_path)
        self.assertEqual(vote_link.get_attribute('like-url'), like_path)

        artwork_score = self.selenium.find_element_by_css_selector('.artwork-score')
        self.assertEquals(artwork_score.text, '1')

        self.assertEqual(
            len(self.selenium.find_elements_by_link_text('UNSHARE')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-detail')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-author')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_link_text(self.exhibition.title)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.submission-date')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.code-block')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%d' % self.artwork.id)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('save_artwork')),
            0
        )

    def test_other_votes_view(self):
        submission = Submission.objects.create(
            artwork=self.artwork,
            exhibition=self.exhibition,
            submitted_by=self.user)
        vote = Vote.objects.create(submission=submission,
            status=Vote.THUMBS_UP, voted_by=self.user)

        view_path = reverse('submission-view', kwargs={'pk': submission.id})
        view_url = '%s%s' % (self.live_server_url, view_path)
        unlike_path = reverse('submission-unlike', kwargs={'submission': submission.id})
        like_path = reverse('submission-like', kwargs={'submission': submission.id})

        self.performLogin(user='staff')
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('submission-view-content')
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-title')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.share-link')),
            1
        )

        vote_link = self.selenium.find_element_by_id('vote-%s' % submission.id)
        self.assertEqual(vote_link.get_attribute('href'), '%s#' % (view_url))
        self.assertEqual(vote_link.text, '1')
        self.assertEqual(vote_link.get_attribute('title'), 'like')
        self.assertEqual(vote_link.get_attribute('unlike-url'), unlike_path)
        self.assertEqual(vote_link.get_attribute('like-url'), like_path)

        artwork_score = self.selenium.find_element_by_css_selector('.artwork-score')
        self.assertEquals(artwork_score.text, '1')

        self.assertEqual(
            len(self.selenium.find_elements_by_link_text('unshare')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-detail')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-author')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_link_text(self.exhibition.title)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.submission-date')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.code-block')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%d' % self.artwork.id)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('save_artwork')),
            0
        )

        # Click on vote link to 'like'
        vote_link.click()
        time.sleep(5)   # wait for vote to be counted
        self.assertEqual(vote_link.get_attribute('href'), '%s#' % (view_url))
        self.assertEqual(vote_link.text, '2')
        self.assertEqual(vote_link.get_attribute('title'), 'unlike')
        self.assertEqual(vote_link.get_attribute('unlike-url'), unlike_path)
        self.assertEqual(vote_link.get_attribute('like-url'), like_path)

        # Click on vote link to 'unlike'
        vote_link.click()
        time.sleep(5)   # wait for vote to be counted
        self.assertEqual(vote_link.get_attribute('href'), '%s#' % (view_url))
        self.assertEqual(vote_link.text, '1')
        self.assertEqual(vote_link.get_attribute('title'), 'like')
        self.assertEqual(vote_link.get_attribute('unlike-url'), unlike_path)
        self.assertEqual(vote_link.get_attribute('like-url'), like_path)


class SubmissionListIntegrationTests(SeleniumTestCase):
    """Exhibition view includes Submission list."""

    def setUp(self):
        super(SubmissionListIntegrationTests, self).setUp()
        self.exhibition = Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.staff_user)
        self.artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        self.exhibition_path = reverse('exhibition-view', kwargs={'pk': self.exhibition.id})
        self.exhibition_url = '%s%s' % (self.live_server_url, self.exhibition_path)

    def test_empty_list_public(self):

        self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.order_by')),
            0
        )

    def test_empty_list_student(self):

        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.order_by')),
            0
        )

    def test_empty_list_staff(self):

        self.performLogin(user='staff')
        self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.order_by')),
            0
        )

    def test_empty_list_super(self):

        self.performLogin(user='super')
        self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.order_by')),
            0
        )

    def test_list_one_public(self):

        # Submit artwork to the exhibition
        submission = Submission.objects.create(artwork=self.artwork, exhibition=self.exhibition, submitted_by=self.user)

        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.artwork.id)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.order_by')),
            0
        )

    def test_list_one_student(self):

        # Submit artwork to the exhibition
        submission = Submission.objects.create(artwork=self.artwork, exhibition=self.exhibition, submitted_by=self.user)

        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.artwork.id)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.order_by')),
            0
        )

    def test_list_one_staff(self):

        # Submit artwork to the exhibition
        submission = Submission.objects.create(artwork=self.artwork, exhibition=self.exhibition, submitted_by=self.user)

        self.performLogin(user='staff')
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.artwork.id)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.order_by')),
            0
        )

    def test_list_one_super(self):

        # Submit artwork to the exhibition
        submission = Submission.objects.create(artwork=self.artwork, exhibition=self.exhibition, submitted_by=self.user)

        self.performLogin(user='super')
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.artwork.id)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.order_by')),
            0
        )

    def test_list_two_public(self):

        # Submit artwork to the exhibition
        submission1 = Submission.objects.create(artwork=self.artwork, exhibition=self.exhibition, submitted_by=self.user)
        artwork2 = Artwork.objects.create(title='Artwork Two', code='// code goes here', author=self.user)
        submission2 = Submission.objects.create(artwork=artwork2, exhibition=self.exhibition, submitted_by=self.user)

        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            2
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.artwork.id)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % artwork2.id)),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.order_by')),
            1
        )

    def test_list_order_by(self):

        # Submit artwork to the exhibition
        artwork1 = self.artwork
        submission1 = Submission.objects.create(artwork=self.artwork, exhibition=self.exhibition, submitted_by=self.user)

        artwork2 = Artwork.objects.create(title='Artwork Two', code='// code goes here', author=self.user)
        submission2 = Submission.objects.create(artwork=artwork2, exhibition=self.exhibition, submitted_by=self.user, score=10)

        artwork3 = Artwork.objects.create(title='Artwork Three', code='// code goes here', author=self.user)
        submission3 = Submission.objects.create(artwork=artwork3, exhibition=self.exhibition, submitted_by=self.user, score=5)

        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.order_by')),
            1
        )
        artworks = self.selenium.find_elements_by_css_selector('.artwork')
        self.assertEqual(
            len(artworks),
            3
        )

        # Artworks default sorted by created at
        self.assertEqual(
            artworks[0].get_attribute('id'),
            'artwork-%s' % artwork3.id
        )
        self.assertEqual(
            artworks[1].get_attribute('id'),
            'artwork-%s' % artwork2.id
        )
        self.assertEqual(
            artworks[2].get_attribute('id'),
            'artwork-%s' % artwork1.id
        )

        # Sort by score
        order_by_score = self.selenium.find_element_by_link_text('Most Votes')
        self.assertIsNotNone(order_by_score)
        with wait_for_page_load(self.selenium):
            order_by_score.click()

        artworks = self.selenium.find_elements_by_css_selector('.artwork')
        self.assertEqual(
            len(artworks),
            3
        )

        # Artworks sorted by score
        self.assertEqual(
            artworks[0].get_attribute('id'),
            'artwork-%s' % artwork2.id
        )
        self.assertEqual(
            artworks[1].get_attribute('id'),
            'artwork-%s' % artwork3.id
        )
        self.assertEqual(
            artworks[2].get_attribute('id'),
            'artwork-%s' % artwork1.id
        )

        # Sort by most recent (back to default order)
        order_by_score = self.selenium.find_element_by_link_text('Most Recent')
        self.assertIsNotNone(order_by_score)
        with wait_for_page_load(self.selenium):
            order_by_score.click()

        artworks = self.selenium.find_elements_by_css_selector('.artwork')
        self.assertEqual(
            len(artworks),
            3
        )

        # Artworks sorted by score
        self.assertEqual(
            artworks[0].get_attribute('id'),
            'artwork-%s' % artwork3.id
        )
        self.assertEqual(
            artworks[1].get_attribute('id'),
            'artwork-%s' % artwork2.id
        )
        self.assertEqual(
            artworks[2].get_attribute('id'),
            'artwork-%s' % artwork1.id
        )

    def test_list_one_delete(self):

        # Submit artwork to the exhibition
        submission = Submission.objects.create(artwork=self.artwork, exhibition=self.exhibition, submitted_by=self.user)

        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.artwork.id)),
            1
        )

        # Delete the submission
        submission.delete()

        self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )

    def test_vote_like_unlike(self):

        # Submit artwork to the exhibition
        submission = Submission.objects.create(artwork=self.artwork, exhibition=self.exhibition, submitted_by=self.user)

        unlike_path = reverse('submission-unlike', kwargs={'submission': submission.id})
        like_path = reverse('submission-like', kwargs={'submission': submission.id})

        # One vote section per submission
        self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-votes')),
            1
        )

        # Public must login to vote
        vote_link = self.selenium.find_element_by_id('vote-%s' % submission.id)
        self.assertEqual(vote_link.get_attribute('href'), 
            '%s%s?next=%s' % (self.live_server_url, reverse('login'), self.exhibition_path))
        self.assertEqual(vote_link.text, '0')
        self.assertEqual(vote_link.get_attribute('title'), 'Sign in to vote')
        self.assertEqual(vote_link.get_attribute('unlike-url'), None)
        self.assertEqual(vote_link.get_attribute('like-url'), None)

        # Create a staff vote
        Vote.objects.create(submission=submission, status=Vote.THUMBS_UP, voted_by=self.staff_user)

        # Ensure it's counted
        self.selenium.get(self.exhibition_url)
        vote_link = self.selenium.find_element_by_id('vote-%s' % submission.id)
        self.assertEqual(vote_link.get_attribute('href'), 
            '%s%s?next=%s' % (self.live_server_url, reverse('login'), self.exhibition_path))
        self.assertEqual(vote_link.text, '1')
        self.assertEqual(vote_link.get_attribute('title'), 'Sign in to vote')
        self.assertEqual(vote_link.get_attribute('unlike-url'), None)
        self.assertEqual(vote_link.get_attribute('like-url'), None)

        # Login as student user via 'vote' link
        with wait_for_page_load(self.selenium):
            vote_link.click()
        self.assertLogin(user='student', next_path=self.exhibition_path)

        # Ensure we're back on the view page
        self.assertEqual(self.selenium.current_url, self.exhibition_url)

        # Can see staff vote
        artwork_score = self.selenium.find_element_by_css_selector('.artwork-score')
        self.assertEquals(artwork_score.text, '1')

        # Logged-in user can like this submission
        vote_link = self.selenium.find_element_by_id('vote-%s' % submission.id)
        self.assertEqual(vote_link.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link.text, '1')
        self.assertEqual(vote_link.get_attribute('title'), 'like')
        self.assertEqual(vote_link.get_attribute('unlike-url'), unlike_path)
        self.assertEqual(vote_link.get_attribute('like-url'), like_path)
        artwork_score = self.selenium.find_element_by_css_selector('.artwork-score')
        self.assertEquals(artwork_score.text, '1')

        vote_link.click()
        time.sleep(5)   # wait for vote to be counted

        self.assertEqual(vote_link.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link.text, '2')
        self.assertEqual(vote_link.get_attribute('title'), 'unlike')
        self.assertEqual(vote_link.get_attribute('unlike-url'), unlike_path)
        self.assertEqual(vote_link.get_attribute('like-url'), like_path)
        self.assertEquals(artwork_score.text, '2')

        # And we can unlike it too
        vote_link.click()
        time.sleep(5)   # wait for vote to be counted

        self.assertEqual(vote_link.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link.text, '1')
        self.assertEqual(vote_link.get_attribute('title'), 'like')
        self.assertEqual(vote_link.get_attribute('unlike-url'), unlike_path)
        self.assertEqual(vote_link.get_attribute('like-url'), like_path)
        self.assertEquals(artwork_score.text, '1')

    def test_multiple_vote_like_unlike(self):

        # Submit artworks to the exhibition
        submission1 = Submission.objects.create(artwork=self.artwork, exhibition=self.exhibition, submitted_by=self.user)
        artwork2 = Artwork.objects.create(title='Artwork Two', code='// code goes here', author=self.user)
        submission2 = Submission.objects.create(artwork=artwork2, exhibition=self.exhibition, submitted_by=self.user)

        unlike_path1 = reverse('submission-unlike', kwargs={'submission': submission1.id})
        like_path1 = reverse('submission-like', kwargs={'submission': submission1.id})
        unlike_path2 = reverse('submission-unlike', kwargs={'submission': submission2.id})
        like_path2 = reverse('submission-like', kwargs={'submission': submission2.id})

        # One vote section per submission
        self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-votes')),
            2
        )

        # Public must login to vote
        vote_link1 = self.selenium.find_element_by_id('vote-%s' % submission1.id)
        self.assertEqual(vote_link1.get_attribute('href'), 
            '%s%s?next=%s' % (self.live_server_url, reverse('login'), self.exhibition_path))
        self.assertEqual(vote_link1.text, '0')
        self.assertEqual(vote_link1.get_attribute('title'), 'Sign in to vote')
        self.assertEqual(vote_link1.get_attribute('unlike-url'), None)
        self.assertEqual(vote_link1.get_attribute('like-url'), None)

        vote_link2 = self.selenium.find_element_by_id('vote-%s' % submission2.id)
        self.assertEqual(vote_link2.get_attribute('href'), 
            '%s%s?next=%s' % (self.live_server_url, reverse('login'), self.exhibition_path))
        self.assertEqual(vote_link2.text, '0')
        self.assertEqual(vote_link2.get_attribute('title'), 'Sign in to vote')
        self.assertEqual(vote_link2.get_attribute('unlike-url'), None)
        self.assertEqual(vote_link2.get_attribute('like-url'), None)

        # Create a staff vote on submission2
        Vote.objects.create(submission=submission2, status=Vote.THUMBS_UP, voted_by=self.staff_user)

        # Ensure it's counted against the correct submission
        self.selenium.get(self.exhibition_url)
        vote_link1 = self.selenium.find_element_by_id('vote-%s' % submission1.id)
        self.assertEqual(vote_link1.get_attribute('href'), 
            '%s%s?next=%s' % (self.live_server_url, reverse('login'), self.exhibition_path))
        self.assertEqual(vote_link1.text, '0')
        self.assertEqual(vote_link1.get_attribute('title'), 'Sign in to vote')
        self.assertEqual(vote_link1.get_attribute('unlike-url'), None)
        self.assertEqual(vote_link1.get_attribute('like-url'), None)

        vote_link2 = self.selenium.find_element_by_id('vote-%s' % submission2.id)
        self.assertEqual(vote_link2.get_attribute('href'), 
            '%s%s?next=%s' % (self.live_server_url, reverse('login'), self.exhibition_path))
        self.assertEqual(vote_link2.text, '1')
        self.assertEqual(vote_link2.get_attribute('title'), 'Sign in to vote')
        self.assertEqual(vote_link2.get_attribute('unlike-url'), None)
        self.assertEqual(vote_link2.get_attribute('like-url'), None)

        # Login as student user via 'vote' link
        with wait_for_page_load(self.selenium):
            vote_link2.click()
        self.assertLogin(user='student', next_path=self.exhibition_path)

        # Ensure we're back on the view page
        self.assertEqual(self.selenium.current_url, self.exhibition_url)

        # Can see staff vote
        vote_link2 = self.selenium.find_element_by_id('vote-%s' % submission2.id)
        self.assertEqual(vote_link2.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link2.text, '1')
        self.assertEqual(vote_link2.get_attribute('title'), 'like')
        self.assertEqual(vote_link2.get_attribute('unlike-url'), unlike_path2)
        self.assertEqual(vote_link2.get_attribute('like-url'), like_path2)
        artwork_score2 = self.selenium.find_element_by_css_selector('#vote-%s .artwork-score' % submission2.id)
        self.assertEquals(artwork_score2.text, '1')

        vote_link1 = self.selenium.find_element_by_id('vote-%s' % submission1.id)
        self.assertEqual(vote_link1.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link1.text, '0')
        self.assertEqual(vote_link1.get_attribute('title'), 'like')
        self.assertEqual(vote_link1.get_attribute('unlike-url'), unlike_path1)
        self.assertEqual(vote_link1.get_attribute('like-url'), like_path1)
        artwork_score1 = self.selenium.find_element_by_css_selector('#vote-%s .artwork-score' % submission1.id)
        self.assertEquals(artwork_score1.text, '0')

        # Logged-in user can like this submission
        vote_link2.click()
        time.sleep(5)   # wait for vote to be counted

        self.assertEqual(vote_link2.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link2.text, '2')
        self.assertEqual(vote_link2.get_attribute('title'), 'unlike')
        self.assertEqual(vote_link2.get_attribute('unlike-url'), unlike_path2)
        self.assertEqual(vote_link2.get_attribute('like-url'), like_path2)
        self.assertEquals(artwork_score2.text, '2')

        self.assertEqual(vote_link1.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link1.text, '0')
        self.assertEqual(vote_link1.get_attribute('title'), 'like')
        self.assertEqual(vote_link1.get_attribute('unlike-url'), unlike_path1)
        self.assertEqual(vote_link1.get_attribute('like-url'), like_path1)
        self.assertEquals(artwork_score1.text, '0')

        # And we can unlike it too
        vote_link2.click()
        time.sleep(5)   # wait for vote to be counted

        self.assertEqual(vote_link2.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link2.text, '1')
        self.assertEqual(vote_link2.get_attribute('title'), 'like')
        self.assertEqual(vote_link2.get_attribute('unlike-url'), unlike_path2)
        self.assertEqual(vote_link2.get_attribute('like-url'), like_path2)
        self.assertEquals(artwork_score2.text, '1')

        self.assertEqual(vote_link1.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link1.text, '0')
        self.assertEqual(vote_link1.get_attribute('title'), 'like')
        self.assertEqual(vote_link1.get_attribute('unlike-url'), unlike_path1)
        self.assertEqual(vote_link1.get_attribute('like-url'), like_path1)
        self.assertEquals(artwork_score1.text, '0')

        # We can like the other submission
        vote_link1.click()
        time.sleep(5)   # wait for vote to be counted

        self.assertEqual(vote_link2.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link2.text, '1')
        self.assertEqual(vote_link2.get_attribute('title'), 'like')
        self.assertEqual(vote_link2.get_attribute('unlike-url'), unlike_path2)
        self.assertEqual(vote_link2.get_attribute('like-url'), like_path2)
        self.assertEquals(artwork_score2.text, '1')

        self.assertEqual(vote_link1.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link1.text, '1')
        self.assertEqual(vote_link1.get_attribute('title'), 'unlike')
        self.assertEqual(vote_link1.get_attribute('unlike-url'), unlike_path1)
        self.assertEqual(vote_link1.get_attribute('like-url'), like_path1)
        self.assertEquals(artwork_score1.text, '1')

        # And we can unlike the other submission
        vote_link1.click()
        time.sleep(5)   # wait for vote to be counted

        self.assertEqual(vote_link2.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link2.text, '1')
        self.assertEqual(vote_link2.get_attribute('title'), 'like')
        self.assertEqual(vote_link2.get_attribute('unlike-url'), unlike_path2)
        self.assertEqual(vote_link2.get_attribute('like-url'), like_path2)
        self.assertEquals(artwork_score2.text, '1')

        self.assertEqual(vote_link1.get_attribute('href'), '%s#' % (self.exhibition_url))
        self.assertEqual(vote_link1.text, '0')
        self.assertEqual(vote_link1.get_attribute('title'), 'like')
        self.assertEqual(vote_link1.get_attribute('unlike-url'), unlike_path1)
        self.assertEqual(vote_link1.get_attribute('like-url'), like_path1)
        self.assertEquals(artwork_score1.text, '0')

    def test_artwork_shared_list(self):
        list_path = reverse('artwork-shared')

        artwork1p = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        submission1 = Submission.objects.create(artwork=artwork1, exhibition=self.exhibition, submitted_by=self.user)
        artwork2p = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', shared=1, author=self.staff_user)
        submission2 = Submission.objects.create(artwork=artwork2, exhibition=self.exhibition, submitted_by=self.user)
        artwork3p = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', shared=1, author=self.super_user)
        submission3 = Submission.objects.create(artwork=artwork3, exhibition=self.exhibition, submitted_by=self.user)

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


class SubmissionCreateIntegrationTests(SeleniumTestCase):
    """Artwork view includes Submission create."""

    def setUp(self):
        super(SubmissionCreateIntegrationTests, self).setUp()
        self.exhibition = Exhibition(title='New Exhibition', description='goes here', author=self.staff_user)
        self.student_artwork = Artwork.objects.create(title='Student Art', code='// code goes here', author=self.user)
        self.staff_artwork = Artwork.objects.create(title='Staff Art', code='// code goes here', author=self.staff_user)
        self.staff_shared_artwork = Artwork.objects.create(title='Staff Art', code='// code goes here', shared=1, author=self.staff_user)
        self.student_shared_artwork = Artwork.objects.create(title='Student Shared Art', code='// code goes here', shared=1, author=self.user)

    def test_no_submit_link_public(self):
        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.staff_shared_artwork.id}))
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.staff_shared_artwork.id)),
            1
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SHARE')
        )

    def test_no_submit_link_student(self):
        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.staff_shared_artwork.id}))
        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.staff_shared_artwork.id)),
            1
        )

        # no submit link for unowned artwork
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SHARE')
        )

        # save the exhibition, and submit link still doesn't appear
        self.exhibition.save()
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SHARE')
        )

    def test_owned_submit_link_student(self):
        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_artwork.id}))
        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )
        # no submit link until exhibition available
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SHARE')
        )

        # save the exhibition, and submit link appears
        self.exhibition.save()
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_link_text('SHARE')
        )

    def test_submit_link_staff(self):
        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_shared_artwork.id}))
        self.performLogin(user='staff')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_shared_artwork.id)),
            1
        )

        # no submit link for non-authors
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SHARE')
        )

        # save the exhibition
        self.exhibition.save()
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)

        # submit link still not visible
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SHARE')
        )

    def test_submit_artwork(self):

        self.exhibition.save()
        exhibition_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': self.exhibition.id}))

        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_artwork.id}))
        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        # Click submit link, and wait for modal to appear
        self.selenium.find_element_by_link_text('SHARE').click()
        time.sleep(3)

        # submit the artwork to the exhibition
        self.selenium.find_element_by_css_selector('#exhibition-%s' % self.exhibition.id).click()
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Should redirect to submission view
        self.student_artwork = Artwork.objects.get(pk=self.student_artwork.id)
        submission_url = '%s%s' % (self.live_server_url, 
            reverse('submission-view', kwargs={'pk': self.student_artwork.shared}))
        self.assertEqual(self.selenium.current_url, submission_url)

        # And my submission should be in the exhibition list
        self.selenium.get(exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)
        )

    def test_cancel_submit_artwork(self):

        self.exhibition.save()
        exhibition_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': self.exhibition.id}))

        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_artwork.id}))
        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        # Click submit link to show the modal
        self.selenium.find_element_by_link_text('SHARE').click()
        time.sleep(3)

        # submit the artwork to the exhibition
        self.selenium.find_element_by_css_selector('#exhibition-%s' % self.exhibition.id).click()
        self.selenium.find_element_by_id('submit-cancel').click()

        # Should be back at artwork view
        self.assertEqual(self.selenium.current_url, artwork_url)

        # And my submission should not be in the exhibition list
        self.selenium.get(exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)
        )

    def test_submit_artwork_no_exhibition(self):

        self.exhibition.save()
        exhibition_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': self.exhibition.id}))

        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_artwork.id}))
        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        # Click submit link to show the modal
        self.selenium.find_element_by_link_text('SHARE').click()
        time.sleep(3)

        # submit the artwork to the exhibition (without selecting an exhibition)
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Should see artwork submit page
        submission_url = '%s%s' % (self.live_server_url, 
            reverse('artwork-submit', kwargs={'artwork': self.student_artwork.id}))
        self.assertEqual(self.selenium.current_url, submission_url)


        # With error : exhibition field is required
        self.assertRegexpMatches(self.selenium.page_source, r'This field is required')

        # With artwork id hidden (since it's in the url)
        artwork_input = self.selenium.find_element_by_id('artwork-%s' % self.student_artwork.id)
        self.assertEqual(
            'hidden',
            artwork_input.get_attribute('type')
        )
        self.assertEqual( 
            'artwork',
            artwork_input.get_attribute('name')
        )
        self.assertEqual( 
            self.student_artwork.id,
            long(artwork_input.get_attribute('value'))
        )
        
        # And exhibition id hidden (since it's the only choice)
        exhibition_input = self.selenium.find_element_by_id('exhibition-%s' % self.exhibition.id)
        self.assertEqual(
            'hidden',
            exhibition_input.get_attribute('type')
        )
        self.assertEqual( 
            'exhibition',
            exhibition_input.get_attribute('name')
        )
        self.assertEqual( 
            self.exhibition.id,
            long(exhibition_input.get_attribute('value'))
        )

        # Click Save button
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Should see the submission view page
        self.student_artwork = Artwork.objects.get(pk=self.student_artwork.id)
        submission_url = '%s%s' % (self.live_server_url, 
            reverse('submission-view', kwargs={'pk': self.student_artwork.shared}))
        self.assertEqual(self.selenium.current_url, submission_url)

        # Exhibition view should show submission in list
        self.selenium.get(exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)
        )

    def test_submit_artwork_cancel(self):

        self.exhibition.save()
        exhibition_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': self.exhibition.id}))
        exhibition_list = '%s%s' % (self.live_server_url, reverse('exhibition-list'))

        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_artwork.id}))
        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        # Click submit link to show the modal
        self.selenium.find_element_by_link_text('SHARE').click()
        time.sleep(3)

        # submit the artwork to the exhibition (without selecting an exhibition)
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Should see artwork submit page
        submission_url = '%s%s' % (self.live_server_url, 
            reverse('artwork-submit', kwargs={'artwork': self.student_artwork.id}))
        self.assertEqual(self.selenium.current_url, submission_url)

        # Click Cancel button
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_cancel').click()

        # Should see the exhibition list page
        self.assertEqual(self.selenium.current_url, exhibition_list)

        # Selected exhibition should not have our artwork in it
        self.selenium.get(exhibition_url)
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('artwork-%s' % self.student_artwork.id)
        )

    def test_submit_artwork_multiple_exhibitions(self):

        self.exhibition.save()
        exhibition2 = Exhibition.objects.create(title='Another Exhibition', description='goes here', author=self.staff_user)
        exhibition2_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': exhibition2.id}))

        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_artwork.id}))
        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        # Click submit link to show the modal
        self.selenium.find_element_by_link_text('SHARE').click()
        time.sleep(3)

        # submit the artwork to the exhibition (without selecting an exhibition)
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Should see artwork submit page
        submission_url = '%s%s' % (self.live_server_url, 
            reverse('artwork-submit', kwargs={'artwork': self.student_artwork.id}))
        self.assertEqual(self.selenium.current_url, submission_url)

        # With artwork id hidden (since it's in the url)
        artwork_input = self.selenium.find_element_by_id('artwork-%s' % self.student_artwork.id)
        self.assertEqual(
            'hidden',
            artwork_input.get_attribute('type')
        )
        self.assertEqual( 
            'artwork',
            artwork_input.get_attribute('name')
        )
        self.assertEqual( 
            self.student_artwork.id,
            long(artwork_input.get_attribute('value'))
        )
        
        # And exhibition options (since there's >1 choice)
        form = self.selenium.find_element_by_id('submission-edit-form')
        inputs = form.find_elements_by_tag_name('input')
        self.assertEqual(4, len(inputs))

        self.assertEqual('hidden', inputs[0].get_attribute('type'))
        self.assertEqual('csrfmiddlewaretoken', inputs[0].get_attribute('name'))

        self.assertEqual('radio', inputs[1].get_attribute('type'))
        self.assertEqual('exhibition', inputs[1].get_attribute('name'))
        self.assertEqual(self.exhibition.id, long(inputs[1].get_attribute('value')))

        self.assertEqual('radio', inputs[2].get_attribute('type'))
        self.assertEqual('exhibition', inputs[2].get_attribute('name'))
        self.assertEqual(exhibition2.id, long(inputs[2].get_attribute('value')))

        self.assertEqual('hidden', inputs[3].get_attribute('type'))
        self.assertEqual('artwork', inputs[3].get_attribute('name'))
        self.assertEqual(self.student_artwork.id, long(inputs[3].get_attribute('value')))

        # Select exhibition2
        inputs[2].click()

        # Click Save button
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Should see the submission view page
        self.student_artwork = Artwork.objects.get(pk=self.student_artwork.id)
        submission_url = '%s%s' % (self.live_server_url, 
            reverse('submission-view', kwargs={'pk': self.student_artwork.shared}))
        self.assertEqual(self.selenium.current_url, submission_url)

        # Artwork shoul dbe present in the exhibition view
        self.selenium.get(exhibition2_url)
        self.assertIsNotNone(
            self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)
        )

    def test_submit_artwork_already_submitted(self):

        self.exhibition.save()
        exhibition2 = Exhibition.objects.create(title='Another Exhibition', description='goes here', author=self.staff_user)
        exhibition_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': self.exhibition.id}))

        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_artwork.id}))
        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        # Click submit link to show the modal
        self.selenium.find_element_by_link_text('SHARE').click()
        time.sleep(3)

        # There's actually three forms on this page: search artwork, submit artwork, and edit artwork
        inputs = self.selenium.find_elements_by_tag_name('input')
        self.assertEqual(10, len(inputs))

        self.assertEqual('hidden', inputs[0].get_attribute('type'))
        self.assertEqual('action', inputs[0].get_attribute('name'))

        self.assertEqual('hidden', inputs[1].get_attribute('type'))
        self.assertEqual('site', inputs[1].get_attribute('name'))

        self.assertEqual('text', inputs[2].get_attribute('type'))
        self.assertEqual('q', inputs[2].get_attribute('name'))

        self.assertEqual('hidden', inputs[3].get_attribute('type'))
        self.assertEqual('csrfmiddlewaretoken', inputs[3].get_attribute('name'))

        self.assertEqual('text', inputs[4].get_attribute('type'))
        self.assertEqual('title', inputs[4].get_attribute('name'))
        self.assertEqual(self.student_artwork.title, inputs[4].get_attribute('value'))

        self.assertEqual('hidden', inputs[5].get_attribute('type'))
        self.assertEqual('code', inputs[5].get_attribute('name'))
        self.assertEqual(self.student_artwork.code, inputs[5].get_attribute('value'))

        self.assertEqual('hidden', inputs[6].get_attribute('type'))
        self.assertEqual('csrfmiddlewaretoken', inputs[6].get_attribute('name'))

        self.assertEqual('hidden', inputs[7].get_attribute('type'))
        self.assertEqual('artwork', inputs[7].get_attribute('name'))
        self.assertEqual(self.student_artwork.id, long(inputs[7].get_attribute('value')))

        self.assertEqual('radio', inputs[8].get_attribute('type'))
        self.assertEqual('exhibition', inputs[8].get_attribute('name'))
        self.assertEqual(self.exhibition.id, long(inputs[8].get_attribute('value')))

        self.assertEqual('radio', inputs[9].get_attribute('type'))
        self.assertEqual('exhibition', inputs[9].get_attribute('name'))
        self.assertEqual(exhibition2.id, long(inputs[9].get_attribute('value')))

        # submit the artwork to the first exhibition
        inputs[9].click()
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Should redirect to the submission view
        self.student_artwork = Artwork.objects.get(pk=self.student_artwork.id)
        submission_url = '%s%s' % (self.live_server_url, 
            reverse('submission-view', kwargs={'pk': self.student_artwork.shared}))
        self.assertEqual(self.selenium.current_url, submission_url)
         
        # Should see the artwork on the exhibition view page
        self.selenium.get(exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)
        )

        # Go back to the submission view
        with wait_for_page_load(self.selenium):
            self.selenium.get(submission_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        # No more 'SHARE' link
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SHARE')
        )

        # Unsubmit link shown instead
        self.assertIsNotNone(
            self.selenium.find_element_by_link_text('UNSHARE')
        )

    def test_submit_shares_artwork(self):

        self.exhibition.save()
        exhibition_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': self.exhibition.id}))

        # Public can't see artwork until submitted/shared
        artwork_path = reverse('artwork-view', kwargs={'pk': self.student_artwork.id})
        artwork_url = '%s%s' % (self.live_server_url, artwork_path)
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)

        # Login required
        login_url = '%s%s?next=%s' % (self.live_server_url, reverse('login'), artwork_path)
        self.assertEqual(self.selenium.current_url, login_url)

        # Login as non-author
        self.assertLogin(user='staff', next_path=artwork_path)
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

        # Create submission
        submission = Submission.objects.create(artwork=self.student_artwork, exhibition=self.exhibition, submitted_by=self.user)

        # Artwork is now shared with public
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )


class SubmissionDeleteIntegrationTests(SeleniumTestCase):
    """Artwork view includes Submission delete/unsubmit"""

    def setUp(self):
        super(SubmissionDeleteIntegrationTests, self).setUp()
        self.exhibition = Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.staff_user)
        self.student_artwork = Artwork.objects.create(title='Student Art', code='// code goes here', author=self.user)
        self.staff_artwork = Artwork.objects.create(title='Staff Art', code='// code goes here', author=self.staff_user)
        self.submission = Submission.objects.create(
            artwork=self.student_artwork,
            exhibition=self.exhibition,
            submitted_by = self.user,
        )
        self.delete_url = '%s%s' % (self.live_server_url, reverse('submission-delete', kwargs={'pk': self.submission.id}))
        self.exhibition_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': self.exhibition.id}))
        self.artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_artwork.id}))

        self.student_artwork = Artwork.objects.get(pk=self.student_artwork.id)
        self.submission_url = '%s%s' % (self.live_server_url, reverse('submission-view', kwargs={'pk': self.student_artwork.shared}))

    def test_unsubmit_link_student_own(self):

        self.performLogin(user='student')

        # Confirm my submission is on the exhibition page
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-%s' % self.student_artwork.id),
        )

        # View the submission to get to the unshare link
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.submission_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        # Click unshare link
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_link_text('UNSHARE').click()

        self.assertEqual(self.selenium.current_url, self.delete_url)
        self.assertRegexpMatches(self.selenium.page_source, r'Are you sure you want to unshare this artwork')

        # Confirm delete
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('submission_delete').click()

        # Back on Artwork view page
        self.assertEqual(self.selenium.current_url, self.artwork_url)

        # Confirm my submission was removed from the exhibition
        self.selenium.get(self.exhibition_url)
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('artwork-%s' % self.student_artwork.id)
        )

    def test_unsubmit_own_cancel(self):

        self.performLogin(user='student')

        # Go to delete submission page
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.delete_url)
        self.assertRegexpMatches(self.selenium.page_source, r'Are you sure you want to unshare this artwork')

        # Cancel delete
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('submission_do_not_delete').click()

        # Back on Submission view page
        self.assertEqual(self.selenium.current_url, self.submission_url)

        # Confirm my submission is still on the exhibition page
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-%s' % self.student_artwork.id),
        )

    def test_unsubmit_student_not_own(self):

        staff_submission = Submission.objects.create(
            artwork=self.staff_artwork,
            exhibition=self.exhibition,
            submitted_by = self.staff_user,
        )

        self.performLogin(user='student')

        # Delete submission page should throw permission denied
        delete_url = '%s%s' % (self.live_server_url, reverse('submission-delete', kwargs={'pk': staff_submission.id}))
        with wait_for_page_load(self.selenium):
            self.selenium.get(delete_url)
        self.assertRegexpMatches(self.selenium.page_source, r'403 Forbidden')


    def test_unsubmit_staff_not_own(self):
        self.performLogin(user='staff')

        # Confirm my submission is on the exhibition page
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-%s' % self.student_artwork.id),
        )

        # Go to delete submission page - should not allow
        self.selenium.get(self.delete_url)
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

    def test_unsubmit_super_not_own(self):

        self.performLogin(user='super')

        # Confirm my submission is on the exhibition page
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-%s' % self.student_artwork.id),
        )

        # Go to delete submission page - should allow
        self.selenium.get(self.delete_url)
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

    def test_unsubmit_deletes_votes(self):
        # Create two votes
        Vote.objects.create(submission=self.submission, status=Vote.THUMBS_UP, voted_by=self.user)
        Vote.objects.create(submission=self.submission, status=Vote.THUMBS_UP, voted_by=self.staff_user)

        # Confirm that votes were created
        submission_votes = Vote.objects.filter(submission=self.submission)
        self.assertEqual(submission_votes.count(), 2)

        self.performLogin(user='student')

        # Visit submission delete page
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.delete_url)
        self.assertRegexpMatches(self.selenium.page_source, r'Are you sure you want to unshare this artwork')

        # Confirm delete
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('submission_delete').click()

        # Back on Artwork view page
        self.assertEqual(self.selenium.current_url, self.artwork_url)

        # Confirm my submission was removed from the exhibition
        self.selenium.get(self.exhibition_url)
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('artwork-%s' % self.student_artwork.id)
        )

        # Confirm that votes were deleted
        submission_votes = Vote.objects.filter(submission=self.submission)
        self.assertEqual(submission_votes.count(), 0)

    def test_unsubmit_cancel_keeps_votes(self):

        # Create two votes
        Vote.objects.create(submission=self.submission, status=Vote.THUMBS_UP, voted_by=self.user)
        Vote.objects.create(submission=self.submission, status=Vote.THUMBS_UP, voted_by=self.staff_user)

        # Confirm that votes were created
        submission_votes = Vote.objects.filter(submission=self.submission)
        self.assertEqual(submission_votes.count(), 2)

        self.performLogin(user='student')

        # Visit submission delete page
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.delete_url)
        self.assertRegexpMatches(self.selenium.page_source, r'Are you sure you want to unshare this artwork')

        # Cancel delete
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('submission_do_not_delete').click()

        # Should see the submission view page
        submission_url = '%s%s' % (self.live_server_url, 
            reverse('submission-view', kwargs={'pk': self.student_artwork.shared}))
        self.assertEqual(self.selenium.current_url, submission_url)

        # Confirm my submission is still on the exhibition page
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-%s' % self.student_artwork.id),
        )

        # Confirm that votes were not deleted
        submission_votes = Vote.objects.filter(submission=self.submission)
        self.assertEqual(submission_votes.count(), 2)

    def test_unsubmit_hides_artwork(self):

        self.exhibition.save()
        exhibition_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': self.exhibition.id}))

        # Delete any existing submissions
        Submission.objects.filter(exhibition=self.exhibition, artwork=self.student_artwork).delete()

        # Public can't see artwork or code until submitted/shared
        artwork_path = reverse('artwork-view', kwargs={'pk': self.student_artwork.id})
        artwork_url = '%s%s' % (self.live_server_url, artwork_path)
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)

        # Redirected to login page
        login_url = '%s%s?next=%s' % (self.live_server_url, reverse('login'), artwork_path)
        self.assertEqual(self.selenium.current_url, login_url)
    
        # Login as non-owner, and verify forbidden
        self.assertLogin(user='staff', next_path=artwork_path)
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

        # Logout again to go back to public view
        self.performLogout()

        # Create submission
        submission = Submission.objects.create(artwork=self.student_artwork, exhibition=self.exhibition, submitted_by=self.user)

        # Artwork and code are now shared with public
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        # Delete submission
        submission.delete()

        # Artwork and code are now hidden
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)

        # Redirected to login page
        login_url = '%s%s?next=%s' % (self.live_server_url, reverse('login'), artwork_path)
        self.assertEqual(self.selenium.current_url, login_url)
    
        # Login as non-owner, and verify forbidden
        self.assertLogin(user='staff', next_path=artwork_path)
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )


class SubmissionList_NoHTML5Iframe_IntegrationTests(NoHTML5SeleniumTestCase):

    '''Tests the artwork rendering in a browser that does not support HTML5 iframe srcdoc/sandbox'''

    def setUp(self):
        super(SubmissionList_NoHTML5Iframe_IntegrationTests, self).setUp()
        self.exhibition = Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.staff_user)
        self.artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        self.exhibition_path = reverse('exhibition-view', kwargs={'pk': self.exhibition.id})
        self.exhibition_url = '%s%s' % (self.live_server_url, self.exhibition_path)

    def test_artwork_compile_error(self):

        bad_artwork1 = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', author=self.user)
        good_artwork = Artwork.objects.create(title='Good test code1', code='// good code!', author=self.user)
        bad_artwork2 = Artwork.objects.create(title='Bad test code2', code='still bad code!', author=self.user)

        # Submit artwork to exhibition
        submission1 = Submission.objects.create(artwork=bad_artwork1, exhibition=self.exhibition, submitted_by=self.user)
        submission2 = Submission.objects.create(artwork=good_artwork, exhibition=self.exhibition, submitted_by=self.user)
        submission2 = Submission.objects.create(artwork=bad_artwork2, exhibition=self.exhibition, submitted_by=self.user)

        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )

        # The paused overlays should be hidden
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % bad_artwork1.id).is_displayed())
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % good_artwork.id).is_displayed())
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % bad_artwork2.id).is_displayed())

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


class SubmissionList_HTML5Iframe_IntegrationTests(SeleniumTestCase):

    '''Tests the artwork rendering in a browser that does support HTML5 iframe srcdoc/sandbox'''

    def setUp(self):
        super(SubmissionList_HTML5Iframe_IntegrationTests, self).setUp()
        self.exhibition = Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.staff_user)
        self.artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        self.exhibition_path = reverse('exhibition-view', kwargs={'pk': self.exhibition.id})
        self.exhibition_url = '%s%s' % (self.live_server_url, self.exhibition_path)

    def test_artwork_compile_error(self):

        bad_artwork1 = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', author=self.user)
        good_artwork = Artwork.objects.create(title='Good test code1', code='// good code!', author=self.user)
        bad_artwork2 = Artwork.objects.create(title='Bad test code2', code='still bad code!', author=self.user)

        # Submit artwork to exhibition
        submission1 = Submission.objects.create(artwork=bad_artwork1, exhibition=self.exhibition, submitted_by=self.user)
        submission2 = Submission.objects.create(artwork=good_artwork, exhibition=self.exhibition, submitted_by=self.user)
        submission2 = Submission.objects.create(artwork=bad_artwork2, exhibition=self.exhibition, submitted_by=self.user)

        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )

        # The paused overlays should be shown
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % bad_artwork1.id).is_displayed())
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % good_artwork.id).is_displayed())
        self.assertTrue(self.selenium.find_element_by_id('paused-%s' % bad_artwork2.id).is_displayed())

        # Push play-all to start all animations
        self.selenium.find_element_by_id('play-all').click()
        time.sleep(1)

        # The paused overlays should be hidden
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % bad_artwork1.id).is_displayed())
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % good_artwork.id).is_displayed())
        self.assertFalse(self.selenium.find_element_by_id('paused-%s' % bad_artwork2.id).is_displayed())

        # We should get 2 errors shown for the bad artworks
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % bad_artwork1.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % bad_artwork1.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % bad_artwork2.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % bad_artwork2.id)
        self.assertEqual(error.text, 'missing ; before statement');
        self.selenium.switch_to.default_content()

        # and no error shown for the good artwork
        iframe = self.selenium.find_element_by_css_selector("#iframe-%s iframe" % good_artwork.id)
        self.assertIsNotNone(iframe)
        self.selenium.switch_to.frame(iframe)
        error = self.selenium.find_element_by_id('error-%s' % good_artwork.id)
        self.assertEqual(error.text, '')
        self.selenium.switch_to.default_content()

        # But no errors in the console
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_submission_list_play_buttons(self):

        # Create 3 artworks, 2 with bad code, and share them
        artwork1 = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)
        artwork2 = Artwork.objects.create(title='Good test code1', code='// good code!', shared=1, author=self.user)
        artwork3 = Artwork.objects.create(title='Bad test code2', code='still bad code!', shared=1, author=self.user)

        # Submit artwork to exhibition
        submission1 = Submission.objects.create(artwork=artwork1, exhibition=self.exhibition, submitted_by=self.user)
        submission2 = Submission.objects.create(artwork=artwork2, exhibition=self.exhibition, submitted_by=self.user)
        submission2 = Submission.objects.create(artwork=artwork3, exhibition=self.exhibition, submitted_by=self.user)

        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
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

