from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Django admin + backend API
    path("admin/", admin.site.urls),
    path("djangoapp/", include("djangoapp.urls")),

    # Django-rendered templates
    path("about/", TemplateView.as_view(template_name="About.html")),
    path("contact/", TemplateView.as_view(template_name="Contact.html")),

    # React frontend routes
    path("login/", TemplateView.as_view(template_name="index.html")),
    path("register/", TemplateView.as_view(template_name="index.html")),
    path("dealers/", TemplateView.as_view(template_name="index.html")),
    path("dealer/<int:dealer_id>/", TemplateView.as_view(template_name="index.html")),
    path("postreview/<int:dealer_id>/", TemplateView.as_view(template_name="index.html")),

    # Django home page
    path("", TemplateView.as_view(template_name="Home.html")),
]

# Serve static + media in development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Catch-all: send any other route to React index.html (SPA support)
urlpatterns += [
    re_path(r"^(?!admin|djangoapp|about|contact).*", TemplateView.as_view(template_name="index.html")),
]
