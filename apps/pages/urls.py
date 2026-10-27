from django.urls import path

from apps.pages import newsletter, tools, views

urlpatterns = [
    path("tools/", tools.tools_index, name="tools"),
    path(
        "tools/compare-github-repositories/",
        tools.compare_repositories,
        name="compare_repositories",
    ),
    path("newsletter/", newsletter.subscribe, name="newsletter"),
    path("newsletter/thanks/", newsletter.thanks, name="newsletter_thanks"),
    path("", views.LandingPageView.as_view(), name="landing"),
    path("privacy-policy", views.PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("terms-of-service", views.TermsOfServiceView.as_view(), name="terms_of_service"),
]
