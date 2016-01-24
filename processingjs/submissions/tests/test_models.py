from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from django_adelaidex.util.test import UserSetUp
from django_adelaidex.lti.models import Cohort
from submissions.models import Submission, SubmissionForm
from exhibitions.models import Exhibition
from artwork.models import Artwork
from votes.models import Vote


class SubmissionTests(UserSetUp, TestCase):
    """Submission model tests."""

    def test_str(self):
        
        exhibition = Exhibition(title='New Exhibition', description='description goes here')
        artwork = Artwork(title='New Artwork', code='// code goes here')

        submission = Submission(exhibition=exhibition, artwork=artwork)

        self.assertEquals(
            str(submission),
            'New Exhibition :: New Artwork'
        )

    def test_can_see(self):
        # Everyone can see submissions
        exhibition = Exhibition(title='New Exhibition', description='description goes here', released_at=timezone.now())
        student_artwork = Artwork(title='New Artwork', code='// code goes here', author=self.user)
        staff_artwork = Artwork(title='New Artwork', code='// code goes here', author=self.staff_user)
        submission = Submission(exhibition=exhibition, artwork=student_artwork)

        self.assertTrue(submission.can_see())
        self.assertTrue(submission.can_see(self.user))
        self.assertTrue(submission.can_see(self.staff_user))
        self.assertTrue(submission.can_see(self.super_user))

    def test_can_save_released_exhibition(self):

        exhibition = Exhibition(title='New Exhibition', description='description goes here', released_at=timezone.now())
        self.assertTrue(exhibition.released_yet)

        student_artwork = Artwork(title='New Artwork', code='// code goes here', author=self.user)
        staff_artwork = Artwork(title='New Artwork', code='// code goes here', author=self.staff_user)

        # only authors can submit artwork
        submission = Submission(exhibition=exhibition, artwork=student_artwork)
        self.assertTrue(submission.can_save(self.user))
        self.assertFalse(submission.can_save(self.staff_user))
        self.assertFalse(submission.can_save(self.super_user))

        submission = Submission(exhibition=exhibition, artwork=staff_artwork)
        self.assertFalse(submission.can_save(self.user))
        self.assertTrue(submission.can_save(self.staff_user))
        self.assertFalse(submission.can_save(self.super_user))

    def test_can_save_unreleased_exhibition(self):

        exhibition = Exhibition(
            title='New Exhibition', 
            description='description goes here', 
            released_at=timezone.now() + timedelta(hours=24))
        self.assertFalse(exhibition.released_yet)

        student_artwork = Artwork(title='New Artwork', code='// code goes here', author=self.user)
        staff_artwork = Artwork(title='New Artwork', code='// code goes here', author=self.staff_user)

        # students cannot submit to unreleased exhibitions
        submission = Submission(exhibition=exhibition, artwork=student_artwork)
        self.assertFalse(submission.can_save(self.user))
        self.assertFalse(submission.can_save(self.staff_user))
        self.assertFalse(submission.can_save(self.super_user))

        # but staff can
        submission = Submission(exhibition=exhibition, artwork=staff_artwork)
        self.assertFalse(submission.can_save(self.user))
        self.assertTrue(submission.can_save(self.staff_user))
        self.assertFalse(submission.can_save(self.super_user))

    def test_save_unique(self):

        exhibition = Exhibition(
            title='New Exhibition',
            description='description goes here',
            released_at=timezone.now(),
            author=self.user)
        exhibition.save()
        artwork = Artwork(title='New Artwork', code='// code goes here', author=self.user)
        artwork.save()
        submission1 = Submission(exhibition=exhibition, artwork=artwork, submitted_by=self.user)
        submission2 = Submission(exhibition=exhibition, artwork=artwork, submitted_by=self.user)

        # submissions must be unique
        self.assertEqual(submission1.save(), None)
        self.assertRaisesRegexp(
            IntegrityError,
            'columns exhibition_id, artwork_id are not unique',
            submission2.save)

    def test_save_shares_artwork(self):
        exhibition1 = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at=timezone.now(),
            author=self.user)
        artwork = Artwork.objects.create(title='New Artwork', code='// code goes here', author=self.user)
        self.assertEqual(artwork.shared, 0)

        # Artwork must be submitted to be shared
        submission1 = Submission.objects.create(exhibition=exhibition1, artwork=artwork, submitted_by=self.user)
        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 1)

        # Submitting artwork to more than one exhibition increments the shared counter
        exhibition2 = Exhibition.objects.create(
            title='Another Exhibition',
            description='description goes here',
            released_at=timezone.now(),
            author=self.user)
        submission2 = Submission.objects.create(exhibition=exhibition2, artwork=artwork, submitted_by=self.user)
        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 2)

    def test_delete_unshares_artwork(self):
        exhibition1 = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at=timezone.now(),
            author=self.user)
        artwork = Artwork.objects.create(title='New Artwork', code='// code goes here', author=self.user)
        self.assertEqual(artwork.shared, 0)

        submission1 = Submission.objects.create(exhibition=exhibition1, artwork=artwork, submitted_by=self.user)
        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 1)

        exhibition2 = Exhibition.objects.create(
            title='Another Exhibition',
            description='description goes here',
            released_at=timezone.now(),
            author=self.user)
        submission2 = Submission.objects.create(exhibition=exhibition2, artwork=artwork, submitted_by=self.user)
        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, submission2.id)

        submission1.delete()
        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 0)

        submission2.delete()
        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 0)

    def test_can_vote(self):
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.user)
        artwork = Artwork.objects.create(title='New Artwork', code='// code goes here', author=self.user)
        submission = Submission.objects.create(exhibition=exhibition, artwork=artwork, submitted_by=self.user)

        # public cannot vote
        self.assertFalse(submission.can_vote())

        # students can vote
        self.assertTrue(submission.can_vote(user=self.user))
        # unless they've already voted
        student_vote = Vote.objects.create(submission=submission, voted_by=self.user, status=Vote.THUMBS_UP)
        self.assertFalse(submission.can_vote(user=self.user))

        # staff can vote
        self.assertTrue(submission.can_vote(user=self.staff_user))
        # unless they've already voted
        staff_vote = Vote.objects.create(submission=submission, voted_by=self.staff_user, status=Vote.THUMBS_UP)
        self.assertFalse(submission.can_vote(user=self.staff_user))

        # super can vote
        self.assertTrue(submission.can_vote(user=self.super_user))
        # unless they've already voted
        super_vote = Vote.objects.create(submission=submission, voted_by=self.super_user, status=Vote.THUMBS_UP)
        self.assertFalse(submission.can_vote(user=self.super_user))

    def test_delete_votes(self):
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.user)
        artwork = Artwork.objects.create(title='New Artwork', code='// code goes here', author=self.user)
        submission = Submission.objects.create(exhibition=exhibition, artwork=artwork, submitted_by=self.user)
        student_vote = Vote.objects.create(submission=submission, status=Vote.THUMBS_UP, voted_by=self.user)
        staff_vote = Vote.objects.create(submission=submission, status=Vote.THUMBS_UP, voted_by=self.staff_user)

        self.assertEqual(Vote.objects.filter(submission=submission).count(), 2)
        submission.delete()
        self.assertEqual(Vote.objects.filter(submission=submission).count(), 0)

    def test_delete_votes_and_unshare(self):
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.user)
        artwork = Artwork.objects.create(title='New Artwork', code='// code goes here', author=self.user)
        submission = Submission.objects.create(exhibition=exhibition, artwork=artwork, submitted_by=self.user)
        student_vote = Vote.objects.create(submission=submission, status=Vote.THUMBS_UP, voted_by=self.user)
        staff_vote = Vote.objects.create(submission=submission, status=Vote.THUMBS_UP, voted_by=self.staff_user)

        artwork = Artwork.objects.get(pk=artwork.id)
        self.assertEqual(artwork.shared, submission.id)

        self.assertEqual(Vote.objects.filter(submission=submission).count(), 2)
        submission.delete()
        self.assertEqual(Vote.objects.filter(submission=submission).count(), 0)

        artwork = Artwork.objects.get(pk=artwork.id)
        self.assertEqual(artwork.shared, 0)

    def test_disqus_identifier(self):
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.user)
        artwork = Artwork.objects.create(title='New Artwork', code='// code goes here', author=self.user)
        submission = Submission.objects.create(exhibition=exhibition, artwork=artwork, submitted_by=self.user)

        # Ensure the disqus_identifier contains the artwork id, so that it
        # persists between submission attempts.
        self.assertIn('%s' % artwork.id, submission.disqus_identifier)

    def test_can_see_queryset(self):

        # Everyone can see submissions
        exhibition1 = Exhibition.objects.create(
            title='Exhibition One', 
            description='description goes here',
            author=self.user)
        artwork1 = Artwork.objects.create(
            title='New Artwork', 
            code='// code goes here', 
            author=self.user)
        submission1 = Submission.objects.create(
            exhibition=exhibition1, 
            artwork=artwork1, 
            submitted_by=self.user)

        exhibition2 = Exhibition.objects.create(
            title='Exhibition Two', 
            description='description goes here',
            author=self.user)
        artwork2 = Artwork.objects.create(
            title='New Artwork', 
            code='// code goes here', 
            author=self.user)
        submission2 = Submission.objects.create(
            exhibition=exhibition2, 
            artwork=artwork2, 
            submitted_by=self.user)

        # By default, all submissions are included in the can_see queryset
        submissions = Submission.can_see_queryset().all()
        self.assertEqual(len(submissions), 2)
        self.assertEqual(submissions[0], submission1)
        self.assertEqual(submissions[1], submission2)

        # Same for all users
        submissions = Submission.can_see_queryset(user=self.user).all()
        self.assertEqual(len(submissions), 2)
        self.assertEqual(submissions[0], submission1)
        self.assertEqual(submissions[1], submission2)

        submissions = Submission.can_see_queryset(user=self.staff_user).all()
        self.assertEqual(len(submissions), 2)
        self.assertEqual(submissions[0], submission1)
        self.assertEqual(submissions[1], submission2)

        # Unless you filter by exhibition
        submissions = Submission.can_see_queryset(exhibition=exhibition1).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission1)

        submissions = Submission.can_see_queryset(exhibition=exhibition1.id).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission1)

        submissions = Submission.can_see_queryset(exhibition=exhibition2).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission2)

        submissions = Submission.can_see_queryset(exhibition=exhibition2.id).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission2)


class SubmissionCohortTests(UserSetUp, TestCase):

    def setUp(self):
        super(SubmissionCohortTests, self).setUp()
        self.no_cohort_user = get_user_model().objects.create(username='no_cohort')
        self.no_cohort_user.cohort = None
        self.no_cohort_user.save()

        self.cohort1_user = get_user_model().objects.create(username='cohort1')
        self.cohort2_user = get_user_model().objects.create(username='cohort2')

        self.cohort1 = Cohort.objects.create(
            title='Cohort 1',
            oauth_key='abc',
            oauth_secret='abc',
            is_default=True,
        )
        self.cohort1_user.cohort = self.cohort1
        self.cohort1_user.save()

        self.cohort2 = Cohort.objects.create(
            title='Cohort 2',
            oauth_key='def',
            oauth_secret='def',
        )
        self.cohort2_user.cohort = self.cohort2
        self.cohort2_user.save()

    def test_can_see_queryset(self):

        exhibition0 = Exhibition.objects.create(
            title='Exhibition No Cohort', 
            description='description goes here',
            cohort=None,
            author=self.user)
        artwork0 = Artwork.objects.create(
            title='New Artwork', 
            code='// code goes here', 
            author=self.user)
        submission0 = Submission.objects.create(
            exhibition=exhibition0, 
            artwork=artwork0, 
            submitted_by=self.user)

        exhibition1 = Exhibition.objects.create(
            title='Exhibition One', 
            description='description goes here',
            cohort=self.cohort1,
            author=self.user)
        artwork1 = Artwork.objects.create(
            title='New Artwork', 
            code='// code goes here', 
            author=self.user)
        submission1 = Submission.objects.create(
            exhibition=exhibition1, 
            artwork=artwork1, 
            submitted_by=self.user)

        exhibition2 = Exhibition.objects.create(
            title='Exhibition Two', 
            description='description goes here',
            cohort=self.cohort2,
            author=self.user)
        artwork2 = Artwork.objects.create(
            title='New Artwork', 
            code='// code goes here', 
            author=self.user)
        submission2 = Submission.objects.create(
            exhibition=exhibition2, 
            artwork=artwork2, 
            submitted_by=self.user)


        # Everyone sees submissions in no-cohort and default exhibitions
        submissions = Submission.can_see_queryset().all()
        self.assertEqual(len(submissions), 2)
        self.assertEqual(submissions[0], submission0)
        self.assertEqual(submissions[1], submission1)

        # Users see no-cohort and exhibitions in their own cohort
        submissions = Submission.can_see_queryset(user=self.no_cohort_user).all()
        self.assertEqual(len(submissions), 2)
        self.assertEqual(submissions[0], submission0)
        self.assertEqual(submissions[1], submission1)

        submissions = Submission.can_see_queryset(user=self.cohort1_user).all()
        self.assertEqual(len(submissions), 2)
        self.assertEqual(submissions[0], submission0)
        self.assertEqual(submissions[1], submission1)

        submissions = Submission.can_see_queryset(user=self.cohort2_user).all()
        self.assertEqual(len(submissions), 2)
        self.assertEqual(submissions[0], submission0)
        self.assertEqual(submissions[1], submission2)

        # Unless you filter by exhibition
        submissions = Submission.can_see_queryset(exhibition=exhibition1).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission1)

        submissions = Submission.can_see_queryset(exhibition=exhibition1.id).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission1)

        submissions = Submission.can_see_queryset(exhibition=exhibition2).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission2)

        submissions = Submission.can_see_queryset(exhibition=exhibition2.id).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission2)

        # Test user+exhibition permutations
        submissions = Submission.can_see_queryset(user=self.no_cohort_user, exhibition=exhibition1).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission1)

        submissions = Submission.can_see_queryset(user=self.cohort1_user, exhibition=exhibition1).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission1)

        submissions = Submission.can_see_queryset(user=self.cohort2_user, exhibition=exhibition1).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission1)

        submissions = Submission.can_see_queryset(user=self.no_cohort_user, exhibition=exhibition2).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission2)

        submissions = Submission.can_see_queryset(user=self.cohort1_user, exhibition=exhibition2).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission2)

        submissions = Submission.can_see_queryset(user=self.cohort2_user, exhibition=exhibition2).all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0], submission2)


class SubmissionModelFormTests(UserSetUp, TestCase):
    """model.SubmissionForm tests."""

    def setUp(self):
        super(SubmissionModelFormTests, self).setUp()

        self.exhibition = Exhibition.objects.create(
                title='New Exhibition',
                description='description goes here',
                author=self.user)
        self.exhibition.save()
        self.artwork = Artwork.objects.create(
                title='New Artwork',
                code='// code goes here',
                author=self.user)
        self.artwork.save()

    def test_login(self):
        form_data = {
            'artwork': self.artwork.id,
            'exhibition': self.exhibition.id,
        }

        # Form requires logged-in user
        form = SubmissionForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertRaises(IntegrityError, form.save)

    def test_validation(self):

        form_data = {
            'artwork': self.artwork.id,
            'exhibition': self.exhibition.id,
        }

        form = SubmissionForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.artwork.id, form_data['artwork'])
        self.assertEqual(form.instance.exhibition.id, form_data['exhibition'])

        # Have to set the author before we can save
        form.instance.submitted_by = self.user
        form.save()

        self.assertEqual(
            '%s' % Submission.objects.get(id=form.instance.id),
            '%s :: %s' % (self.exhibition.title, self.artwork.title)
        )

    def test_artwork_required(self):
        form_data = {
            'artwork': self.artwork.id,
        }

        form = SubmissionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertRaisesRegexp(
            ValueError,
            'The Submission could not be created because the data didn\'t validate.',
            form.save)

    def test_exhibition_required(self):
        form_data = {
            'exhibition': self.exhibition.id,
        }

        form = SubmissionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertRaisesRegexp(
            ValueError,
            'The Submission could not be created because the data didn\'t validate.',
            form.save)
