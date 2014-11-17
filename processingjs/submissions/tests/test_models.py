from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta

from uofa.test import UserSetUp
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

    def test_can_save_released_exhibition(self):

        exhibition = Exhibition(title='New Exhibition', description='description goes here', released_at=timezone.now())
        self.assertTrue(exhibition.released_yet)

        student_artwork = Artwork(title='New Artwork', code='// code goes here', author=self.user)
        staff_artwork = Artwork(title='New Artwork', code='// code goes here', author=self.staff_user)

        # student can submit own artwork, staff can submit anything
        submission = Submission(exhibition=exhibition, artwork=student_artwork)
        self.assertTrue(submission.can_save(self.user))
        self.assertTrue(submission.can_save(self.staff_user))
        self.assertTrue(submission.can_save(self.super_user))

        # students cannot submit other's artwork, but staff can
        submission = Submission(exhibition=exhibition, artwork=staff_artwork)
        self.assertFalse(submission.can_save(self.user))
        self.assertTrue(submission.can_save(self.staff_user))
        self.assertTrue(submission.can_save(self.super_user))

    def test_can_save_unreleased_exhibition(self):

        exhibition = Exhibition(
            title='New Exhibition', 
            description='description goes here', 
            released_at=timezone.now() + timedelta(hours=24))
        self.assertFalse(exhibition.released_yet)

        student_artwork = Artwork(title='New Artwork', code='// code goes here', author=self.user)
        staff_artwork = Artwork(title='New Artwork', code='// code goes here', author=self.staff_user)

        # student cannot submit to unreleased exhibitions, staff can submit anything
        submission = Submission(exhibition=exhibition, artwork=student_artwork)
        self.assertFalse(submission.can_save(self.user))
        self.assertTrue(submission.can_save(self.staff_user))
        self.assertTrue(submission.can_save(self.super_user))

        # students cannot submit other's artwork either, but staff can
        submission = Submission(exhibition=exhibition, artwork=staff_artwork)
        self.assertFalse(submission.can_save(self.user))
        self.assertTrue(submission.can_save(self.staff_user))
        self.assertTrue(submission.can_save(self.super_user))

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