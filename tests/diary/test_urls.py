from django.test import TestCase
from django.urls import resolve, reverse

from pepysdiary.diary import feeds, views


class DiaryURLsTestCase(TestCase):
    """Testing that the named URLs map the correct name to URL,
    and that the correct views are called.
    """

    def test_entry_detail_url(self):
        self.assertEqual(
            reverse(
                "entry_detail", kwargs={"year": "1660", "month": "01", "day": "01"}
            ),
            "/diary/1660/01/01/",
        )

    def test_entry_detail_view(self):
        self.assertEqual(
            resolve("/diary/1660/01/01/").func.view_class, views.EntryDetailView
        )

    def test_entry_month_archive_url(self):
        self.assertEqual(
            reverse("entry_month_archive", kwargs={"year": "1660", "month": "01"}),
            "/diary/1660/01/",
        )

    def test_entry_month_archive_view(self):
        self.assertEqual(
            resolve("/diary/1660/01/").func.view_class, views.EntryMonthArchiveView
        )

    def test_entry_archive_url(self):
        self.assertEqual(reverse("entry_archive"), "/diary/")

    def test_entry_archive_view(self):
        self.assertEqual(
            resolve("/diary/").func.view_class, views.EntryArchiveIndexView
        )

    def test_summary_year_archive_url(self):
        self.assertEqual(
            reverse("summary_year_archive", kwargs={"year": "1660"}),
            "/diary/summary/1660/",
        )

    def test_summary_year_archive_view(self):
        self.assertEqual(
            resolve("/diary/summary/1660/").func.view_class,
            views.SummaryYearArchiveView,
        )

    def test_entry_rss_url(self):
        self.assertEqual(reverse("entry_rss"), "/diary/rss/")

    def test_entry_rss_view(self):
        self.assertEqual(
            resolve("/diary/rss/").func.__class__.__name__,
            feeds.LatestEntriesFeed.__name__,
        )
