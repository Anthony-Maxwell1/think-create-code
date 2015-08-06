from django.test import TestCase
from django.db import IntegrityError

from django_adelaidex.test import UserSetUp
from votes.models import Vote
from submissions.models import Submission
from exhibitions.models import Exhibition
from artwork.models import Artwork

class VoteTests(UserSetUp, TestCase):
    """Vote model tests."""

    def setUp(self):
        super(VoteTests, self).setUp()

        self.exhibition = Exhibition.objects.create(title='New Exhibition', description='description goes here', author=self.user)
        self.artwork = Artwork.objects.create(title='New Artwork', code='// code goes here', author=self.user)
        self.submission = Submission.objects.create(exhibition=self.exhibition, artwork=self.artwork, submitted_by=self.user)
        self.vote = Vote(submission=self.submission, status=Vote.THUMBS_UP, voted_by=self.user)

    def test_str(self):
        self.assertEquals(
            str(self.vote),
            'New Exhibition :: New Artwork :: Thumbs Up'
        )

    def test_str_unset(self):
        unset_vote = Vote()
        self.assertEquals(
            str(unset_vote),
            'unset :: none'
        )

    def test_thumbs_up_score(self):

        self.assertEqual(self.submission.score, 0)

        # Creating a thumbs up vote increments submission.score
        self.vote.save()
        self.submission = Submission.objects.get(id=self.submission.id)
        self.assertEqual(self.submission.score, 1)

        # Editing a thumbs up vote does not change submission.score
        self.vote.voted_by = self.staff_user
        self.vote.save()
        self.submission = Submission.objects.get(id=self.submission.id)
        self.assertEqual(self.submission.score, 1)

        # Deleting a thumbs up vote decrements submission.score
        self.vote.delete()
        self.submission = Submission.objects.get(id=self.submission.id)
        self.assertEqual(self.submission.score, 0)

    def test_save_unique(self):

        # one vote per submission per user
        self.assertEqual(self.vote.save(), None)

        vote2 = Vote(submission=self.submission, voted_by=self.user, status=Vote.THUMBS_UP)
        self.assertRaisesRegexp(
            IntegrityError,
            'columns submission_id, voted_by_id are not unique',
            vote2.save)

    def test_can_delete(self):

        self.vote.save()

        # public cannot delete a vote
        self.assertFalse(self.vote.can_delete())

        # voter can delete own vote
        self.assertTrue(self.vote.can_delete(user=self.user))

        # other users cannot delete another user's vote
        self.assertFalse(self.vote.can_delete(user=self.staff_user))
        self.assertFalse(self.vote.can_delete(user=self.super_user))

    def test_can_delete_queryset(self):

        exhibition1 = Exhibition.objects.create(title='Student Exhibition', description='description goes here', author=self.user)
        submission1 = Submission.objects.create(exhibition=exhibition1, artwork=self.artwork, submitted_by=self.user)

        exhibition2 = Exhibition.objects.create(title='Staff Exhibition', description='description goes here', author=self.user)
        submission2 = Submission.objects.create(exhibition=exhibition2, artwork=self.artwork, submitted_by=self.staff_user)

        student_vote1 = Vote.objects.create(submission=submission1, status=Vote.THUMBS_UP, voted_by=self.user)
        staff_vote1   = Vote.objects.create(submission=submission1, status=Vote.THUMBS_UP, voted_by=self.staff_user)
        super_vote1   = Vote.objects.create(submission=submission1, status=Vote.THUMBS_UP, voted_by=self.super_user)

        student_vote2 = Vote.objects.create(submission=submission2, status=Vote.THUMBS_UP, voted_by=self.user)
        staff_vote2   = Vote.objects.create(submission=submission2, status=Vote.THUMBS_UP, voted_by=self.staff_user)
        super_vote2   = Vote.objects.create(submission=submission2, status=Vote.THUMBS_UP, voted_by=self.super_user)

        # public can't delete any votes
        public_qs = Vote.can_delete_queryset()
        self.assertEquals(0, len(public_qs.all()))

        # students can delete own votes
        student_qs = Vote.can_delete_queryset(user=self.user)
        self.assertEquals(2, len(student_qs.all()))
        self.assertTrue(student_qs.all()[0].can_delete(user=self.user))
        self.assertTrue(student_qs.all()[1].can_delete(user=self.user))

        student_sub1_qs = Vote.can_delete_queryset(user=self.user, submission=submission1)
        self.assertEquals(1, len(student_sub1_qs.all()))
        self.assertEquals(student_vote1.id, student_sub1_qs.all()[0].id)
        self.assertTrue(student_sub1_qs.all()[0].can_delete(user=self.user))

        student_sub2_qs = Vote.can_delete_queryset(user=self.user, submission=submission2)
        self.assertEquals(1, len(student_sub2_qs.all()))
        self.assertEquals(student_vote2.id, student_sub2_qs.all()[0].id)
        self.assertTrue(student_sub2_qs.all()[0].can_delete(user=self.user))

        student_subs_qs = Vote.can_delete_queryset(user=self.user, submission=[submission1.id, submission2.id])
        self.assertEquals(2, len(student_subs_qs.all()))
        self.assertEquals(student_vote1.id, student_subs_qs.all()[0].id)
        self.assertEquals(student_vote2.id, student_subs_qs.all()[1].id)
        self.assertTrue(student_subs_qs.all()[0].can_delete(user=self.user))
        self.assertTrue(student_subs_qs.all()[1].can_delete(user=self.user))

        student_exh1_qs = Vote.can_delete_queryset(user=self.user, exhibition=exhibition1)
        self.assertEquals(1, len(student_exh1_qs.all()))
        self.assertEquals(student_vote1.id, student_exh1_qs.all()[0].id)
        self.assertTrue(student_qs.all()[0].can_delete(user=self.user))

        student_exh2_qs = Vote.can_delete_queryset(user=self.user, exhibition=exhibition2)
        self.assertEquals(1, len(student_exh2_qs.all()))
        self.assertEquals(student_vote2.id, student_exh2_qs.all()[0].id)
        self.assertTrue(student_exh2_qs.all()[0].can_delete(user=self.user))

        # staff can delete own votes
        staff_qs = Vote.can_delete_queryset(user=self.staff_user)
        self.assertEquals(2, len(staff_qs.all()))
        self.assertTrue(staff_qs.all()[0].can_delete(user=self.staff_user))
        self.assertTrue(staff_qs.all()[1].can_delete(user=self.staff_user))

        staff_sub1_qs = Vote.can_delete_queryset(user=self.staff_user, submission=submission1)
        self.assertEquals(1, len(staff_sub1_qs.all()))
        self.assertEquals(staff_vote1.id, staff_sub1_qs.all()[0].id)
        self.assertTrue(staff_sub1_qs.all()[0].can_delete(user=self.staff_user))

        staff_sub2_qs = Vote.can_delete_queryset(user=self.staff_user, submission=submission2)
        self.assertEquals(1, len(staff_sub2_qs.all()))
        self.assertEquals(staff_vote2.id, staff_sub2_qs.all()[0].id)
        self.assertTrue(staff_sub2_qs.all()[0].can_delete(user=self.staff_user))

        staff_subs_qs = Vote.can_delete_queryset(user=self.staff_user, submission=[submission1.id, submission2.id])
        self.assertEquals(2, len(staff_subs_qs.all()))
        self.assertEquals(staff_vote1.id, staff_subs_qs.all()[0].id)
        self.assertEquals(staff_vote2.id, staff_subs_qs.all()[1].id)
        self.assertTrue(staff_subs_qs.all()[0].can_delete(user=self.staff_user))
        self.assertTrue(staff_subs_qs.all()[1].can_delete(user=self.staff_user))

        staff_exh1_qs = Vote.can_delete_queryset(user=self.staff_user, exhibition=exhibition1)
        self.assertEquals(1, len(staff_exh1_qs.all()))
        self.assertEquals(staff_vote1.id, staff_exh1_qs.all()[0].id)
        self.assertTrue(staff_exh1_qs.all()[0].can_delete(user=self.staff_user))

        staff_exh2_qs = Vote.can_delete_queryset(user=self.staff_user, exhibition=exhibition2)
        self.assertEquals(1, len(staff_exh2_qs.all()))
        self.assertEquals(staff_vote2.id, staff_exh2_qs.all()[0].id)
        self.assertTrue(staff_exh2_qs.all()[0].can_delete(user=self.staff_user))

        # superusers can delete own votes
        super_qs = Vote.can_delete_queryset(user=self.super_user)
        self.assertEquals(2, len(super_qs.all()))
        self.assertTrue(super_qs.all()[0].can_delete(user=self.super_user))
        self.assertTrue(super_qs.all()[1].can_delete(user=self.super_user))

        super_sub1_qs = Vote.can_delete_queryset(user=self.super_user, submission=submission1)
        self.assertEquals(1, len(super_sub1_qs.all()))
        self.assertEquals(super_vote1.id, super_sub1_qs.all()[0].id)
        self.assertTrue(super_sub1_qs.all()[0].can_delete(user=self.super_user))

        super_sub2_qs = Vote.can_delete_queryset(user=self.super_user, submission=submission2)
        self.assertEquals(1, len(super_sub2_qs.all()))
        self.assertEquals(super_vote2.id, super_sub2_qs.all()[0].id)
        self.assertTrue(super_sub2_qs.all()[0].can_delete(user=self.super_user))

        super_subs_qs = Vote.can_delete_queryset(user=self.super_user, submission=[submission1.id, submission2.id])
        self.assertEquals(2, len(super_subs_qs.all()))
        self.assertEquals(super_vote1.id, super_subs_qs.all()[0].id)
        self.assertEquals(super_vote2.id, super_subs_qs.all()[1].id)
        self.assertTrue(super_subs_qs.all()[0].can_delete(user=self.super_user))
        self.assertTrue(super_subs_qs.all()[1].can_delete(user=self.super_user))

        super_exh1_qs = Vote.can_delete_queryset(user=self.super_user, exhibition=exhibition1)
        self.assertEquals(1, len(super_exh1_qs.all()))
        self.assertEquals(super_vote1.id, super_exh1_qs.all()[0].id)
        self.assertTrue(super_exh1_qs.all()[0].can_delete(user=self.super_user))

        super_exh2_qs = Vote.can_delete_queryset(user=self.super_user, exhibition=exhibition2)
        self.assertEquals(1, len(super_exh2_qs.all()))
        self.assertEquals(super_vote2.id, super_exh2_qs.all()[0].id)
        self.assertTrue(super_exh2_qs.all()[0].can_delete(user=self.super_user))
