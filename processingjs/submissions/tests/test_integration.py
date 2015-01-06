from django.core.urlresolvers import reverse
from selenium.common.exceptions import NoSuchElementException
import time

from artwork.models import Artwork
from exhibitions.models import Exhibition
from submissions.models import Submission
from votes.models import Vote
from uofa.test import SeleniumTestCase, NoHTML5SeleniumTestCase, wait_for_page_load


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

        # One vote section per submission
        self.selenium.get(self.exhibition_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork-votes')),
            1
        )

        # No like/unlike links shown to public
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('a.post-vote')),
            0
        )

        # No votes, so no vote text shown
        self.assertNotRegexpMatches(self.selenium.page_source, r'0 votes')

        # Create a staff vote
        Vote.objects.create(submission=submission, status=Vote.THUMBS_UP, voted_by=self.staff_user)

        # Ensure it's counted
        self.selenium.get(self.exhibition_url)
        self.assertRegexpMatches(self.selenium.page_source, r'1 vote')

        # Can login via 'vote' link
        vote_link = self.selenium.find_element_by_link_text('vote')
        self.assertIsNotNone(vote_link)

        # Login as student user
        with wait_for_page_load(self.selenium):
            vote_link.click()
        self.assertLogin(user='student', next_path=self.exhibition_path)

        # Ensure we're back on the view page
        self.assertEqual(self.selenium.current_url, self.exhibition_url)

        # Can see staff vote
        artwork_score = self.selenium.find_element_by_css_selector('.artwork-score')
        self.assertEquals(artwork_score.text, '1')

        # Logged-in user can like this submission
        like_button = self.selenium.find_element_by_css_selector('a.like')
        self.assertIsNotNone(like_button)
        like_button.click()
        time.sleep(5)   # wait for vote to be counted
        self.assertEquals(artwork_score.text, '2')

        # And we can unlike it too
        unlike_button = self.selenium.find_element_by_css_selector('a.unlike')
        self.assertIsNotNone(unlike_button)
        unlike_button.click()
        time.sleep(5)   # wait for vote to be removed
        self.assertEquals(artwork_score.text, '1')


class SubmissionCreateIntegrationTests(SeleniumTestCase):
    """Artwork view includes Submission create."""

    def setUp(self):
        super(SubmissionCreateIntegrationTests, self).setUp()
        self.exhibition = Exhibition(title='New Exhibition', description='goes here', author=self.staff_user)
        self.student_artwork = Artwork.objects.create(title='Student Art', code='// code goes here', author=self.user)
        self.staff_artwork = Artwork.objects.create(title='Staff Art', code='// code goes here', author=self.staff_user)

    def test_no_submit_link_public(self):
        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_artwork.id}))
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SUBMIT')
        )

    def test_no_submit_link_student(self):
        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.staff_artwork.id}))
        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.staff_artwork.id)),
            1
        )

        # no submit link for unowned artwork
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SUBMIT')
        )

        # save the exhibition, and submit link still doesn't appear
        self.exhibition.save()
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SUBMIT')
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
            self.selenium.find_element_by_link_text, ('SUBMIT')
        )

        # save the exhibition, and submit link appears
        self.exhibition.save()
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_link_text('SUBMIT')
        )

    def test_submit_link_staff(self):
        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_artwork.id}))
        self.performLogin(user='staff')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        # no submit link until exhibition available
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SUBMIT')
        )

        # save the exhibition, and submit link appears
        self.exhibition.save()
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_link_text('SUBMIT')
        )

    def test_submit_link_super(self):
        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': self.student_artwork.id}))
        self.performLogin(user='super')
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )
        # no submit link until exhibition available
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('SUBMIT')
        )

        # save the exhibition, and submit link appears
        self.exhibition.save()
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_link_text('SUBMIT')
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
        self.selenium.find_element_by_link_text('SUBMIT').click()
        time.sleep(3)

        # submit the artwork to the exhibition
        self.selenium.find_element_by_css_selector('#exhibition-%s' % self.exhibition.id).click()
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Should redirect to exhibition view
        self.assertEqual(self.selenium.current_url, exhibition_url)

        # And my submission should be in the list
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
        self.selenium.find_element_by_link_text('SUBMIT').click()
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
        self.selenium.find_element_by_link_text('SUBMIT').click()
        time.sleep(3)

        # submit the artwork to the exhibition (without selecting an exhibition)
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Should see artwork submit page
        submission_url = '%s%s' % (self.live_server_url, reverse('artwork-submit', kwargs={'artwork': self.student_artwork.id}))
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

        # Show see the exhibition view page
        self.assertEqual(self.selenium.current_url, exhibition_url)
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
        self.selenium.find_element_by_link_text('SUBMIT').click()
        time.sleep(3)

        # submit the artwork to the exhibition (without selecting an exhibition)
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Should see artwork submit page
        submission_url = '%s%s' % (self.live_server_url, reverse('artwork-submit', kwargs={'artwork': self.student_artwork.id}))
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
        self.selenium.find_element_by_link_text('SUBMIT').click()
        time.sleep(3)

        # submit the artwork to the exhibition (without selecting an exhibition)
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Should see artwork submit page
        submission_url = '%s%s' % (self.live_server_url, reverse('artwork-submit', kwargs={'artwork': self.student_artwork.id}))
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
        exhibition_options = self.selenium.find_elements_by_tag_name('option')
        self.assertEqual(3, len(exhibition_options))
        self.assertEqual('', exhibition_options[0].get_attribute('value'))
        self.assertEqual(self.exhibition.id, long(exhibition_options[1].get_attribute('value')))
        self.assertEqual(exhibition2.id, long(exhibition_options[2].get_attribute('value')))

        # Select exhibition2
        exhibition_options[2].click()

        # Click Save button
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Show see the exhibition view page
        self.assertEqual(self.selenium.current_url, exhibition2_url)
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
        self.selenium.find_element_by_link_text('SUBMIT').click()
        time.sleep(3)

        # Should be a crsf hidden, two radio inputs, and one hidden artwork input
        inputs = self.selenium.find_elements_by_tag_name('input')
        self.assertEqual(4, len(inputs))
        self.assertEqual('hidden', inputs[0].get_attribute('type'))
        self.assertEqual('csrfmiddlewaretoken', inputs[0].get_attribute('name'))

        self.assertEqual('hidden', inputs[1].get_attribute('type'))
        self.assertEqual('artwork', inputs[1].get_attribute('name'))
        self.assertEqual(self.student_artwork.id, long(inputs[1].get_attribute('value')))

        self.assertEqual('radio', inputs[2].get_attribute('type'))
        self.assertEqual('exhibition', inputs[2].get_attribute('name'))
        self.assertEqual(exhibition2.id, long(inputs[2].get_attribute('value')))

        self.assertEqual('radio', inputs[3].get_attribute('type'))
        self.assertEqual('exhibition', inputs[3].get_attribute('name'))
        self.assertEqual(self.exhibition.id, long(inputs[3].get_attribute('value')))


        # submit the artwork to the first exhibition
        inputs[3].click()
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_submission').click()

        # Show see the artwork on the exhibition view page
        self.assertEqual(self.selenium.current_url, exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)
        )

        # Go back to the artwork submit modal
        with wait_for_page_load(self.selenium):
            self.selenium.get(artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        self.selenium.find_element_by_link_text('SUBMIT').click()
        time.sleep(3)

        # Should be crsf hidden, only one radio inputs, and one hidden artwork input
        inputs = self.selenium.find_elements_by_tag_name('input')
        self.assertEqual(3, len(inputs))
        self.assertEqual('hidden', inputs[0].get_attribute('type'))
        self.assertEqual('csrfmiddlewaretoken', inputs[0].get_attribute('name'))

        self.assertEqual('hidden', inputs[1].get_attribute('type'))
        self.assertEqual('artwork', inputs[1].get_attribute('name'))
        self.assertEqual(self.student_artwork.id, long(inputs[1].get_attribute('value')))

        self.assertEqual('radio', inputs[2].get_attribute('type'))
        self.assertEqual('exhibition', inputs[2].get_attribute('name'))
        self.assertEqual(exhibition2.id, long(inputs[2].get_attribute('value')))

        # First exhibition is shown as submitted
        self.assertRegexpMatches(self.selenium.page_source, r'Submitted to ')
        self.assertEqual(
            self.selenium.find_element_by_link_text(self.exhibition.title).get_attribute('href'),
            exhibition_url
        )
        # with an unsubmit link
        self.assertIsNotNone(
            self.selenium.find_element_by_link_text('unsubmit')
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

    def test_unsubmit_link_student_own(self):

        self.performLogin(user='student')

        # Confirm my submission is on the exhibition page
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-%s' % self.student_artwork.id),
        )

        # View the artwork to get to the submit link
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.artwork_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('artwork-%s' % self.student_artwork.id)),
            1
        )

        # Click submit link to show the modal
        self.selenium.find_element_by_link_text('SUBMIT').click()
        time.sleep(3)

        # Should be no input elements, form not shown if no exhibitions to submit ti
        inputs = self.selenium.find_elements_by_tag_name('input')
        self.assertEqual(0, len(inputs))

        # First exhibition is shown as submitted
        self.assertRegexpMatches(self.selenium.page_source, r'Submitted to ')
        self.assertEqual(
            self.selenium.find_element_by_link_text(self.exhibition.title).get_attribute('href'),
            self.exhibition_url
        )

        # with an unsubmit link
        unsubmit = self.selenium.find_element_by_link_text('unsubmit')
        self.assertEqual(self.delete_url, unsubmit.get_attribute('href'))

        # Click unsubmit
        with wait_for_page_load(self.selenium):
            unsubmit.click()

        self.assertEqual(self.selenium.current_url, self.delete_url)
        self.assertRegexpMatches(self.selenium.page_source, r'Are you sure you want to delete this submission')

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
        self.assertRegexpMatches(self.selenium.page_source, r'Are you sure you want to delete this submission')

        # Cancel delete
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('submission_do_not_delete').click()

        # Back on Artwork view page
        self.assertEqual(self.selenium.current_url, self.artwork_url)

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

        # Go to delete submission page - should allow
        self.selenium.get(self.delete_url)
        self.assertRegexpMatches(self.selenium.page_source, r'Are you sure you want to delete this submission')

        # Confirm delete
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('submission_delete').click()

        # Back on Artwork view page
        self.assertEqual(self.selenium.current_url, self.artwork_url)

        # Confirm submission was removed from the exhibition
        self.selenium.get(self.exhibition_url)
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('artwork-%s' % self.student_artwork.id)
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
        self.assertRegexpMatches(self.selenium.page_source, r'Are you sure you want to delete this submission')

        # Confirm delete
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('submission_delete').click()

        # Back on Artwork view page
        self.assertEqual(self.selenium.current_url, self.artwork_url)

        # Confirm submission was removed from the exhibition
        self.selenium.get(self.exhibition_url)
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('artwork-%s' % self.student_artwork.id)
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
        self.assertRegexpMatches(self.selenium.page_source, r'Are you sure you want to delete this submission')

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
        self.assertRegexpMatches(self.selenium.page_source, r'Are you sure you want to delete this submission')

        # Cancel delete
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('submission_do_not_delete').click()

        # Back on Artwork view page
        self.assertEqual(self.selenium.current_url, self.artwork_url)

        # Confirm my submission is still on the exhibition page
        with wait_for_page_load(self.selenium):
            self.selenium.get(self.exhibition_url)
        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-%s' % self.student_artwork.id),
        )

        # Confirm that votes were not deleted
        submission_votes = Vote.objects.filter(submission=self.submission)
        self.assertEqual(submission_votes.count(), 2)

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

        # We should get no errors in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

        # We should be able to see the HTML5 support warning text
        upgradeBrowser = self.selenium.find_element_by_css_selector('.artwork h4')
        self.assertEqual(
            upgradeBrowser.text,
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

        # We should get 2 errors in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]['message'], 'SyntaxError: missing ; before statement')
        self.assertEqual(errors[1]['message'], 'SyntaxError: missing ; before statement')

        # TODO: we're inferring that the 2nd "good" artwork did get rendered,
        # by assuring that the error from the  1st "bad" artwork did not halt
        # processing, since the 3rd bad artwork threw an error too.
        # Not sure how else to test this?

