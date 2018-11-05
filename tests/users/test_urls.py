from django.urls import reverse


def test_admin_urls_are_configured():
    """
    Test that the admin urls exist.
    """
    assert reverse("admin:index") == "/admin/", "admin urls are not configured"
