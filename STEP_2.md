# Step 2 — Registration, login and private medical profiles

This feature is complete in the workspace. It uses the redesigned home page theme
and adds account screens only. Facilities/admin sample data remain the next feature;
stop here until you say **next**.

## Open these pages

- Register: **http://127.0.0.1:8000/accounts/register/**
- Login: **http://127.0.0.1:8000/accounts/login/**
- Your profile: **http://127.0.0.1:8000/accounts/profile/**
- Edit medical details: http://127.0.0.1:8000/accounts/profile/edit/
- Add a contact: http://127.0.0.1:8000/accounts/contacts/add/

The development server has been restarted and is running. You can use the links
now. I have not created an account, password or sample medical data in your actual
development database; create your own account through the registration page.

## What works

1. Register with first name, optional last name, username and matching strong
   passwords. Email is optional and unverified; sign-in uses your username.
2. Django validates the username/password, hashes the password, and saves the user
   and a blank medical profile in one database transaction. Registration signs you
   in and opens the medical-details form.
3. Save a blood group, allergy notes and medical-condition notes. Unknown/blank
   values are allowed where appropriate. Notes are limited to 2,000 characters
   per field. Blank means not recorded, not absence of allergies or conditions.
4. View the private medical ID layout and saved details. Information is marked
   self-reported. It is not a public medical ID or share link.
5. Add, edit and remove emergency contacts. Phone numbers accept spaces, hyphens
   and brackets, then are stored in compact form. Validation requires 7–15 digits
   with an optional +. It checks format, not whether a number exists.
6. Select a primary contact. Saving a new primary contact clears the previous
   primary inside the same transaction. You can have no primary contact, but not
   two. Deleting a primary contact does not automatically choose another person.
7. Sign out using a CSRF-protected POST button. A GET to the logout route returns
   405 and cannot sign you out.
8. Sign in again. Valid same-host next destinations are honoured; external redirects
   are rejected. Successful submissions use POST-Redirect-GET and show Django messages.

Adding a contact does not send messages or verify their number. SOS/ambulance/search
results remain explicitly labelled previews. No account REST endpoints, password
reset, email verification or new emergency workflows are introduced in this step.

## Exact PowerShell commands

From your VS Code terminal:

```powershell
Set-Location 'C:\Users\Ashish\OneDrive\Desktop\MEDTAP'
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py test accounts
```

Expected:

```text
System check identified no issues (0 silenced).
No changes detected
No migrations to apply.
Ran 34 tests ...
OK
```

This feature uses the models already migrated in Step 1, so it requires no new
migration or dependency. Tests create and destroy a separate test database.

If the development server is stopped, start it and keep that terminal open:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Do not start a second server on the same port. To use Django admin, create an admin
account separately if you have not already done so; ordinary registration does
not grant staff or superuser access:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

## If registration or login fails

A successful registration creates the account, signs you in, and redirects to Edit
medical details. If the registration form comes back with errors, no account was
created. Login will reject credentials for an account that does not exist.

The registration error summary now states **Your account hasn't been created** and
shows each exact field error. The page moves keyboard focus to that summary so it
is not hidden above the scroll position. Fix those errors and select Create account
again. Password requirements remain enabled; password inputs are deliberately
cleared on failed submissions. Share error messages for troubleshooting, never your
password. Login keeps its standard generic credentials error for privacy.

## Manual walkthrough

1. Open Register and enter fictional learning data. Choose your own password.
2. Expect a welcome message and the Edit medical details page.
3. Save Unknown/blank details, or fictional notes, and view your medical ID card.
4. Add a contact with an explicitly fake number such as `0000000000`. Ask a real
   person before using their actual details. Mark the first test contact Primary.
5. Add another fake contact and mark it Primary. Expect the previous badge to move.
6. Edit a contact. Then choose Remove: the first page asks for confirmation and
   still keeps the contact; only the confirmation POST removes it.
7. Sign out from the navbar. Try opening Profile: expect a redirect to Login.
8. Sign in with your username. Expect your private profile to load.
9. Open a private contact-edit URL from a different account. Expect 404, without
   showing the other account's contact details.

All pages retain the visible emergency disclaimer. Do not place test emergency
calls. Local learning should use fictional medical/contact data. Application
privacy checks are not encryption at rest; production data handling, retention,
HTTPS and authentication throttling must be addressed before real deployment.

## Files added and changed

```text
MEDTAP/
|-- accounts/
|   |-- forms.py
|   |-- services.py
|   |-- views.py
|   |-- urls.py
|   `-- tests.py
|-- config/settings.py
|-- static/css/theme.css
|-- templates/
|   |-- accounts/
|   |   |-- auth_form.html
|   |   |-- profile.html
|   |   |-- profile_form.html
|   |   |-- contact_form.html
|   |   `-- contact_confirm_delete.html
|   |-- core/home.html
|   `-- partials/
|       |-- form_errors.html
|       |-- form_fields.html
|       |-- navbar.html
|       `-- feature_preview.html
|-- README.md
`-- STEP_2.md
```

Existing models, migrations, secrets and installed dependencies are unchanged.
Earlier guides are snapshots of earlier steps; the full shared CSS/settings and
updated templates below represent the current code after Step 2.

## Viva explanations

- **Built-in auth forms:** RegistrationForm extends UserCreationForm and LoginForm
  extends AuthenticationForm. Django supplies password matching, username validation,
  password-strength checks, hashing and inactive-user rejection. We add styling and
  selected fields rather than implementing password handling ourselves.
- **Function-based views:** decorators consistently limit methods, protect private
  screens and prevent caching. Named app-level routes keep navigation independent
  of literal paths. LOGIN_URL tells login_required where to redirect.
- **Safe redirects:** url_has_allowed_host_and_scheme restricts next to the current
  host and requires HTTPS destinations for HTTPS requests. resolve_url accepts either
  a route name or a URL path for the fallback, matching Django's own auth views.
- **Atomic registration:** User and MedicalProfile are created in one transaction.
  A profile-creation failure rolls back the user, avoiding a half-created account.
  Account creation explicitly creates the profile; it does not depend on a signal.
- **Older admin users:** profiles created by registration exist immediately. An
  account created earlier through createsuperuser can have no profile. GET requests
  display an empty state; saving medical details creates its profile. A contact can
  be added after that profile exists.
- **ModelForm allowlists:** only declared medical/contact fields can be changed.
  user/profile ownership is assigned by the server from request.user, never from
  a submitted user ID, profile ID or URL-supplied patient ID.
- **Ownership:** contact lookups include profile__user=request.user. Guessing another
  person's contact ID gives 404. The profile route has no user ID and always loads
  the current account's data.
- **Primary-contact service:** the transaction locks the profile row on databases
  supporting select_for_update, clears the old flag, validates and saves the contact.
  A failure rolls back the entire switch. The existing conditional unique constraint
  provides database protection as well. SQLite does not provide PostgreSQL-style
  row locks, so concurrent production writes need a suitable database deployment.
- **Service reuse:** save_emergency_contact accepts validated data and a profile,
  not an HTTP request. A later REST serializer can reuse this operation. It also
  rejects an instance owned by a different profile.
- **Privacy:** login_required checks access; never_cache sets private/no-store cache
  headers. Django auto-escaping handles text output. Password widgets do not echo
  passwords back on validation errors. sensitive_post_parameters marks POST data
  for Django's production error-report filtering; production must use DEBUG=False.
- **CSRF and methods:** every modifying HTML form includes csrf_token. Middleware
  rejects missing tokens. Removal uses a confirmation GET plus a separate POST;
  logout is POST-only. Merely following a link cannot remove a contact or sign out.
- **Reusable UI:** shared form-field/error partials avoid repeating validation markup.
  Field labels, help/error IDs and ARIA references stay connected. Bootstrap messages
  provide success/error feedback; no inline custom styles are added.
- **Test isolation:** Django TestCase uses a separate database. Test names, emails,
  phone numbers and passwords are fictional. They are not seeded application data.

See the official [Django authentication guide](https://docs.djangoproject.com/en/6.1/topics/auth/default/)
and [ModelForm guide](https://docs.djangoproject.com/en/6.1/topics/forms/modelforms/)
for the underlying framework APIs. No account rate limiting or password-recovery
service is supplied by this implementation; those need explicit production work.

## Complete code, file by file

All following files are already saved. Blocks contain their complete current
contents, including shared files changed by the account feature.

### accounts/forms.py

Shared Bootstrap widget styling and validated registration/login/profile/contact forms.

```python
import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from common.validators import phone_validator

from .models import EmergencyContact, MedicalProfile, User


class BootstrapFormMixin:
    """Share widget styling without repeating it in every form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                css_class = "form-select"
            else:
                css_class = "form-control"
            field.widget.attrs["class"] = css_class


class RegistrationForm(BootstrapFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150, label="First name")
    last_name = forms.CharField(max_length=150, required=False, label="Last name")
    email = forms.EmailField(
        required=False,
        help_text="Optional. Login uses your username. Email is not verified in this demo.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, autocomplete in {
            "first_name": "given-name", "last_name": "family-name",
            "username": "username", "email": "email",
            "password1": "new-password", "password2": "new-password",
        }.items():
            self.fields[name].widget.attrs["autocomplete"] = autocomplete
        self.fields["username"].widget.attrs["autocapitalize"] = "none"


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "autocomplete": "username", "autocapitalize": "none",
        })
        self.fields["password"].widget.attrs["autocomplete"] = "current-password"


class MedicalProfileForm(BootstrapFormMixin, forms.ModelForm):
    allergies = forms.CharField(
        required=False, max_length=2000,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Record known allergies in your own words. Blank means not recorded.",
    )
    medical_conditions = forms.CharField(
        required=False, max_length=2000,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Include details you want to keep in your profile. Up to 2,000 characters.",
    )

    class Meta:
        model = MedicalProfile
        fields = ("blood_group", "allergies", "medical_conditions")
        help_texts = {"blood_group": "Choose Unknown if you do not know your blood group."}


class EmergencyContactForm(BootstrapFormMixin, forms.ModelForm):
    phone = forms.CharField(
        max_length=32,
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
        help_text="7–15 digits with an optional country prefix (+). Spaces, hyphens and brackets are accepted.",
    )

    class Meta:
        model = EmergencyContact
        fields = ("name", "relationship", "phone", "is_primary")
        labels = {"is_primary": "Make this my primary emergency contact"}
        help_texts = {"is_primary": "This replaces your current primary contact, if you have one."}

    def __init__(self, *args, profile, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.profile = profile
        self.fields["name"].widget.attrs["autocomplete"] = "name"

    def clean_phone(self):
        phone = re.sub(r"[\s()\-]", "", self.cleaned_data["phone"])
        phone_validator(phone)
        return phone
```

### accounts/services.py

One transaction-safe operation for owned contact updates and primary-contact switching.

```python
from django.db import transaction
from django.utils import timezone

from .models import EmergencyContact, MedicalProfile


@transaction.atomic
def save_emergency_contact(*, profile, data, contact=None):
    """Save one owned contact and switch the primary contact atomically."""
    profile = MedicalProfile.objects.select_for_update().get(pk=profile.pk)
    if contact is None:
        contact = EmergencyContact(profile=profile)
    elif contact.profile_id != profile.pk:
        raise ValueError("The contact must belong to this profile.")

    if data["is_primary"]:
        profile.emergency_contacts.filter(is_primary=True).exclude(pk=contact.pk).update(
            is_primary=False, updated_at=timezone.now(),
        )
    for field in ("name", "relationship", "phone", "is_primary"):
        setattr(contact, field, data[field])
    contact.full_clean()
    contact.save()
    return contact
```

### accounts/views.py

Function-based authentication, private profile and contact CRUD views with safe redirects.

```python
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import EmergencyContactForm, LoginForm, MedicalProfileForm, RegistrationForm
from .models import EmergencyContact, MedicalProfile
from .services import save_emergency_contact


def _safe_next(request):
    candidate = (
        request.POST.get("next", "") if request.method == "POST"
        else request.GET.get("next", "")
    )
    if url_has_allowed_host_and_scheme(
        candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ):
        return candidate
    return resolve_url(settings.LOGIN_REDIRECT_URL)


@sensitive_post_parameters()
@never_cache
@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    form = RegistrationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save()
            MedicalProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, "Your account is ready. Add your medical details when you're ready.")
        return redirect("accounts:profile_edit")
    return render(request, "accounts/auth_form.html", {
        "form": form, "is_registration": True,
    })


@sensitive_post_parameters()
@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(_safe_next(request))
    form = LoginForm(request=request, data=request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Welcome back. You're signed in.")
        return redirect(_safe_next(request))
    return render(request, "accounts/auth_form.html", {
        "form": form, "is_registration": False, "next": _safe_next(request),
    })


@never_cache
@require_POST
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You've been signed out.")
    return redirect("core:home")


@never_cache
@login_required
@require_GET
def profile_detail(request):
    profile = MedicalProfile.objects.filter(user=request.user).first()
    contacts = profile.emergency_contacts.all() if profile else []
    return render(request, "accounts/profile.html", {"profile": profile, "contacts": contacts})


@sensitive_post_parameters()
@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    profile = MedicalProfile.objects.filter(user=request.user).first()
    form = MedicalProfileForm(
        request.POST if request.method == "POST" else None,
        instance=profile or MedicalProfile(user=request.user),
    )
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            # get_or_create also handles existing admin accounts without a profile.
            profile, _ = MedicalProfile.objects.get_or_create(user=request.user)
            for field in ("blood_group", "allergies", "medical_conditions"):
                setattr(profile, field, form.cleaned_data[field])
            profile.save()
        messages.success(request, "Your medical profile has been saved.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile_form.html", {"form": form})


@sensitive_post_parameters()
@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def contact_add(request):
    profile = MedicalProfile.objects.filter(user=request.user).first()
    if profile is None:
        messages.info(request, "Save your medical profile before adding a contact.")
        return redirect("accounts:profile_edit")
    form = EmergencyContactForm(
        request.POST if request.method == "POST" else None, profile=profile,
    )
    if request.method == "POST" and form.is_valid():
        save_emergency_contact(profile=profile, data=form.cleaned_data)
        messages.success(request, "Emergency contact added.")
        return redirect("accounts:profile")
    return render(request, "accounts/contact_form.html", {"form": form, "is_edit": False})


@sensitive_post_parameters()
@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def contact_edit(request, pk):
    contact = get_object_or_404(EmergencyContact, pk=pk, profile__user=request.user)
    form = EmergencyContactForm(
        request.POST if request.method == "POST" else None,
        instance=contact, profile=contact.profile,
    )
    if request.method == "POST" and form.is_valid():
        save_emergency_contact(profile=contact.profile, data=form.cleaned_data, contact=contact)
        messages.success(request, "Emergency contact updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/contact_form.html", {"form": form, "is_edit": True})


@sensitive_post_parameters()
@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def contact_delete(request, pk):
    contact = get_object_or_404(EmergencyContact, pk=pk, profile__user=request.user)
    if request.method == "POST":
        contact.delete()
        messages.success(request, "Emergency contact removed.")
        return redirect("accounts:profile")
    return render(request, "accounts/contact_confirm_delete.html", {"contact": contact})
```

### accounts/urls.py

Namespaced URLs for the account feature.

```python
from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_detail, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("contacts/add/", views.contact_add, name="contact_add"),
    path("contacts/<int:pk>/edit/", views.contact_edit, name="contact_edit"),
    path("contacts/<int:pk>/remove/", views.contact_delete, name="contact_delete"),
]
```

### config/settings.py

Complete current settings; LOGIN_URL and LOGIN_REDIRECT_URL are the additions in this step.

```python
from pathlib import Path

from decouple import AutoConfig, Csv

BASE_DIR = Path(__file__).resolve().parent.parent
env = AutoConfig(search_path=str(BASE_DIR))

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
    "facilities.apps.FacilitiesConfig",
    "emergency.apps.EmergencyConfig",
    "firstaid.apps.FirstaidConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:profile"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
```

### templates/partials/form_errors.html

An error summary with links to invalid fields; all error text is escaped.

```html
{% if form.errors %}
<div class="form-error-summary" id="form-error-summary" role="alert" tabindex="-1" aria-labelledby="form-error-heading">
  <h2 id="form-error-heading">{{ error_heading|default:'Please check your details' }}</h2>
  {% if error_intro %}<p>{{ error_intro }}</p>{% endif %}
  <ul>
    {% for error in form.non_field_errors %}<li>{{ error }}</li>{% endfor %}
    {% for field in form %}{% for error in field.errors %}<li><a href="#{{ field.id_for_label }}">{{ field.label }}: {{ error }}</a></li>{% endfor %}{% endfor %}
  </ul>
</div>
{% endif %}
```

### templates/partials/form_fields.html

Shared labelled fields, checkbox targets, help text and validation errors.

```html
{% for field in form %}
<div class="field-wrapper">
  {% if field.field.widget.input_type == 'checkbox' %}
  <label class="checkbox-label" for="{{ field.id_for_label }}">{{ field }} <span>{{ field.label }}</span></label>
  {% else %}
  <label class="form-label" for="{{ field.id_for_label }}">{{ field.label }}{% if field.field.required %}<span class="required-marker" aria-hidden="true"> *</span>{% else %}<span class="optional-label"> (optional)</span>{% endif %}</label>
  {{ field }}
  {% endif %}
  {% if field.help_text %}<div class="field-help" id="{{ field.auto_id }}_helptext">{{ field.help_text }}</div>{% endif %}
  {% if field.errors %}<ul class="field-errors" id="{{ field.auto_id }}_error">{% for error in field.errors %}<li>{{ error }}</li>{% endfor %}</ul>{% endif %}
</div>
{% endfor %}
```

### templates/accounts/auth_form.html

One themed template for registration and login with CSRF and password-manager attributes.

```html
{% extends 'base.html' %}
{% block title %}{% if is_registration %}Create your account{% else %}Login{% endif %} | MEDTAP{% endblock %}
{% block content %}
<section class="account-section">
  <div class="container">
    <div class="auth-layout">
      <div class="auth-intro">
        <p class="eyebrow">Your care, together</p>
        <h1>{% if is_registration %}A little prepared.<br>A little more at ease.{% else %}Welcome back.<br>Your care starts here.{% endif %}</h1>
        <p>Keep your medical details and the people you count on in one place.</p>
        <div class="auth-benefits">
          <div>{% include 'partials/icon.html' with name='person-vcard' only %}<span>A medical profile for your blood group, allergies and conditions.</span></div>
          <div>{% include 'partials/icon.html' with name='people' only %}<span>Emergency contacts you can keep up to date.</span></div>
          <div>{% include 'partials/icon.html' with name='lock' only %}<span>Profile pages that require you to sign in.</span></div>
        </div>
        <p class="auth-reminder">This app does not replace calling 112 in a real emergency.</p>
      </div>
      <div class="account-panel">
        <p class="eyebrow">{% if is_registration %}Get started{% else %}Your account{% endif %}</p>
        <h2>{% if is_registration %}Create your account{% else %}Sign in to MEDTAP{% endif %}</h2>
        <p class="text-muted mb-4">{% if is_registration %}Start with an account. Add medical details whenever you're ready.{% else %}Use your username and password to continue.{% endif %}</p>
        {% if is_registration %}
        {% include 'partials/form_errors.html' with error_heading="Your account hasn't been created" error_intro='Fix the errors below, then select Create account again.' %}
        {% else %}
        {% include 'partials/form_errors.html' with error_heading="We couldn't sign you in" %}
        {% endif %}
        <form method="post" action="{% if is_registration %}{% url 'accounts:register' %}{% else %}{% url 'accounts:login' %}{% endif %}">
          {% csrf_token %}
          {% if not is_registration %}<input type="hidden" name="next" value="{{ next }}">{% endif %}
          {% include 'partials/form_fields.html' %}
          <button class="btn btn-primary w-100" type="submit">{% if is_registration %}Create account{% else %}Sign in{% endif %} {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</button>
        </form>
        <p class="auth-switch">{% if is_registration %}Already have an account? <a href="{% url 'accounts:login' %}">Sign in</a>{% else %}New to MEDTAP? <a href="{% url 'accounts:register' %}">Create an account</a>{% endif %}</p>
      </div>
    </div>
  </div>
</section>
{% endblock %}
```

### templates/accounts/profile.html

Private medical ID, self-reported medical details and owned emergency-contact actions.

```html
{% extends 'base.html' %}
{% block title %}Your medical profile | MEDTAP{% endblock %}
{% block content %}
<section class="account-section">
  <div class="container">
    <div class="profile-page-heading">
      <div><p class="eyebrow">Your health, in one place</p><h1>Your medical profile.</h1><p class="text-muted mb-0">Your details and emergency contacts, kept up to date by you.</p></div>
      <a class="btn btn-primary" href="{% url 'accounts:profile_edit' %}">{% include 'partials/icon.html' with name='pencil' class_name='icon-sm' only %} Edit medical details</a>
    </div>
    <div class="profile-layout">
      <div>
        <section class="medical-id" aria-labelledby="medical-id-heading">
          <div class="medical-id-top"><span>{% include 'partials/icon.html' with name='heart-pulse' only %} MEDTAP</span><span class="privacy-label">{% include 'partials/icon.html' with name='lock' class_name='icon-sm' only %} Private profile</span></div>
          <h2 id="medical-id-heading">{{ user.get_full_name|default:user.username }}</h2>
          <p class="medical-id-username">@{{ user.username }}</p>
          <div class="blood-group-row"><div><p class="medical-id-label">Blood group</p><p class="blood-group-value">{% if profile %}{{ profile.get_blood_group_display }}{% else %}Unknown{% endif %}</p></div><span class="self-reported">Self-reported</span></div>
          <p class="medical-id-caption">These details are provided by you and have not been medically verified.</p>
        </section>
        <p class="profile-privacy-note">{% include 'partials/icon.html' with name='lock' class_name='icon-sm' only %} Sign-in is required to view this profile. It is not a public medical ID or share link.</p>
      </div>
      <div class="profile-details">
        <section class="account-panel" aria-labelledby="health-details-heading">
          <h2 id="health-details-heading">Medical details</h2>
          {% if not profile %}<p class="text-muted">You haven't saved a medical profile yet. Select Edit medical details to get started.</p>{% endif %}
          <div class="medical-detail"><h3>Allergies</h3><p>{{ profile.allergies|default:'Not recorded'|linebreaksbr }}</p></div>
          <div class="medical-detail"><h3>Medical conditions</h3><p>{{ profile.medical_conditions|default:'Not recorded'|linebreaksbr }}</p></div>
          <p class="field-help mb-0">“Not recorded” means no information has been entered.</p>
        </section>
        <section class="account-panel" aria-labelledby="contacts-heading">
          <div class="panel-title-row"><h2 id="contacts-heading">Emergency contacts</h2><a class="btn btn-outline-primary" href="{% url 'accounts:contact_add' %}">{% include 'partials/icon.html' with name='plus-lg' class_name='icon-sm' only %} Add contact</a></div>
          {% for contact in contacts %}
          <article class="contact-item">
            <div class="contact-heading"><h3>{{ contact.name }}</h3>{% if contact.is_primary %}<span class="primary-label">Primary</span>{% endif %}</div>
            <p class="contact-relationship">{{ contact.relationship }}</p>
            <p class="contact-phone">{{ contact.phone }}</p>
            <div class="contact-actions">
              <a class="btn btn-outline-primary" href="tel:{{ contact.phone }}" aria-label="Call {{ contact.name }}">{% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call</a>
              <a class="btn btn-outline-primary" href="{% url 'accounts:contact_edit' contact.pk %}" aria-label="Edit contact {{ contact.name }}">Edit</a>
              <a class="btn btn-outline-primary" href="{% url 'accounts:contact_delete' contact.pk %}" aria-label="Remove contact {{ contact.name }}">Remove</a>
            </div>
          </article>
          {% empty %}
          <div class="empty-contacts"><span class="action-icon">{% include 'partials/icon.html' with name='people' only %}</span><h3>Keep your people close.</h3><p>Add someone you would want to reach in an emergency. Adding a contact does not send them a message.</p></div>
          {% endfor %}
        </section>
      </div>
    </div>
  </div>
</section>
{% endblock %}
```

### templates/accounts/profile_form.html

Blood group and medical-note editing with a validation summary.

```html
{% extends 'base.html' %}
{% block title %}Edit medical details | MEDTAP{% endblock %}
{% block content %}
<section class="account-section">
  <div class="container">
    <div class="account-form-shell">
      <a class="back-link" href="{% url 'accounts:profile' %}">{% include 'partials/icon.html' with name='arrow-left' class_name='icon-sm' only %} Back to your profile</a>
      <div class="account-panel">
        <p class="eyebrow">Your medical profile</p><h1>Edit medical details.</h1>
        <p class="text-muted">Share what you know. Choose Unknown or leave a field blank if a detail is not recorded.</p>
        {% include 'partials/form_errors.html' %}
        <form method="post" action="{% url 'accounts:profile_edit' %}">
          {% csrf_token %}
          {% include 'partials/form_fields.html' %}
          <div class="account-form-actions"><button class="btn btn-primary" type="submit">Save medical details</button><a class="btn btn-outline-primary" href="{% url 'accounts:profile' %}">Cancel</a></div>
        </form>
      </div>
    </div>
  </div>
</section>
{% endblock %}
```

### templates/accounts/contact_form.html

Add/edit contact form with phone validation and optional primary selection.

```html
{% extends 'base.html' %}
{% block title %}{% if is_edit %}Edit{% else %}Add{% endif %} emergency contact | MEDTAP{% endblock %}
{% block content %}
<section class="account-section">
  <div class="container">
    <div class="account-form-shell">
      <a class="back-link" href="{% url 'accounts:profile' %}">{% include 'partials/icon.html' with name='arrow-left' class_name='icon-sm' only %} Back to your profile</a>
      <div class="account-panel">
        <p class="eyebrow">Keep your people close</p><h1>{% if is_edit %}Edit{% else %}Add{% endif %} emergency contact.</h1>
        <p class="text-muted">Ask this person before adding their number. This form saves their details to your profile.</p>
        {% include 'partials/form_errors.html' %}
        <form method="post">
          {% csrf_token %}
          {% include 'partials/form_fields.html' %}
          <div class="account-form-actions"><button class="btn btn-primary" type="submit">{% if is_edit %}Save changes{% else %}Add contact{% endif %}</button><a class="btn btn-outline-primary" href="{% url 'accounts:profile' %}">Cancel</a></div>
        </form>
      </div>
    </div>
  </div>
</section>
{% endblock %}
```

### templates/accounts/contact_confirm_delete.html

A read-only confirmation page; only the POST form removes the owned contact.

```html
{% extends 'base.html' %}
{% block title %}Remove emergency contact | MEDTAP{% endblock %}
{% block content %}
<section class="account-section">
  <div class="container">
    <div class="account-form-shell">
      <div class="account-panel">
        <p class="eyebrow">Your emergency contacts</p><h1>Remove this contact?</h1>
        <p>This removes <strong>{{ contact.name }}</strong> ({{ contact.phone }}) from your saved emergency contacts.</p>
        {% if contact.is_primary %}<p class="text-muted">This is your primary contact. You can choose a different primary contact from your remaining contacts.</p>{% endif %}
        <form method="post" action="{% url 'accounts:contact_delete' contact.pk %}">
          {% csrf_token %}
          <div class="account-form-actions"><button class="btn btn-primary" type="submit">Remove contact</button><a class="btn btn-outline-primary" href="{% url 'accounts:profile' %}">Keep contact</a></div>
        </form>
      </div>
    </div>
  </div>
</section>
{% endblock %}
```

### templates/partials/navbar.html

Real Login link for visitors, and My profile plus POST Sign out for signed-in users.

```html
<header class="site-header">
  <nav class="navbar navbar-expand-lg" aria-label="Main navigation">
    <div class="container">
      <a class="navbar-brand" href="{% url 'core:home' %}" aria-label="MEDTAP home">
        <span class="brand-mark">{% include 'partials/icon.html' with name='heart-pulse' only %}</span>
        <span class="brand-word">medtap<span class="brand-dot">.</span></span>
      </a>
      <span class="preview-label me-auto d-lg-none">Preview</span>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#main-navigation" aria-controls="main-navigation" aria-expanded="false" aria-label="Toggle navigation">
        {% include 'partials/icon.html' with name='list' class_name='icon-lg' only %}
      </button>
      <div class="collapse navbar-collapse" id="main-navigation">
        <ul class="navbar-nav">
          <li class="nav-item"><a class="nav-link{% if request.resolver_match.view_name == 'core:home' %} active{% endif %}" {% if request.resolver_match.view_name == 'core:home' %}aria-current="page"{% endif %} href="{% url 'core:home' %}">Home</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'core:home' %}#find-care">Find Hospitals</a></li>
          <li class="nav-item"><button class="nav-link" type="button" data-bs-toggle="modal" data-bs-target="#feature-preview" data-preview-title="First-aid guides" data-preview-description="First-aid guides are not available in this preview. In a medical emergency, call 112 and follow the dispatcher's instructions.">First Aid</button></li>
          <li class="nav-item"><a class="nav-link" href="#emergency-numbers">Helplines</a></li>
        </ul>
        <div class="navbar-actions">
          {% if not user.is_authenticated %}<span class="preview-label d-none d-lg-inline">Project preview</span>{% endif %}
          {% if user.is_authenticated %}
          <a class="btn btn-outline-primary" href="{% url 'accounts:profile' %}">My profile</a>
          <form method="post" action="{% url 'accounts:logout' %}" class="logout-form">{% csrf_token %}<button class="btn btn-outline-primary" type="submit">Sign out</button></form>
          {% else %}
          <a class="btn btn-outline-primary" href="{% url 'accounts:login' %}">Login</a>
          {% endif %}
          <a class="btn btn-primary d-none d-lg-inline-flex" href="tel:112">
            {% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112
          </a>
        </div>
      </div>
    </div>
  </nav>
</header>
```

### templates/partials/feature_preview.html

The existing preview dialog now uses a Close label that also makes sense on account pages.

```html
<div class="modal fade" id="feature-preview" tabindex="-1" aria-labelledby="preview-title" aria-describedby="preview-description">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h2 class="modal-title" id="preview-title">Coming soon</h2>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close dialog"></button>
      </div>
      <div class="modal-body">
        <p id="preview-description">This feature is not available in this preview.</p>
        <p class="critical-note mb-0" id="preview-critical-note" hidden>No request has been sent. No ambulance has been booked. In a real emergency, call 112.</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline-primary" type="button" data-bs-dismiss="modal">Close</button>
        <a class="btn btn-emergency" href="tel:112" id="preview-call" hidden>{% include 'partials/icon.html' with name='telephone' only %} Call 112</a>
      </div>
    </div>
  </div>
</div>
```

### templates/core/home.html

The account invitation now links to the working registration/profile feature.

```html
{% extends 'base.html' %}
{% load static %}
{% block title %}MEDTAP | The right care, a little closer{% endblock %}
{% block content %}
<section class="hero-section" aria-labelledby="hero-heading">
  <div class="hero-shell">
    <div class="hero-grid">
      <div class="hero-copy">
        <p class="hero-kicker">{% include 'partials/icon.html' with name='heart-pulse' class_name='icon-sm' only %} Healthcare, with a human touch</p>
        <h1 class="hero-title" id="hero-heading">The right care.<br>A little <span>closer.</span></h1>
        <p class="hero-description">Find your way to nearby hospitals, essential resources, and the people you count on. A clearer next step, when it matters most.</p>
        <section class="search-panel" id="find-care" aria-labelledby="search-heading">
          <h2 id="search-heading">Find nearby hospitals</h2>
          <form action="{% url 'core:home' %}#find-care" method="get" id="care-search-form" role="search" aria-label="Hospital search preview">
            <label class="visually-hidden" for="care-query">{{ search_form.q.label }}</label>
            <div class="search-controls">
              <div class="query-field">
                {% include 'partials/icon.html' with name='search' class_name='icon-sm' only %}
                {{ search_form.q }}
              </div>
              <button type="submit" class="btn btn-primary">Find care {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</button>
            </div>
            <button type="button" class="location-button" id="location-button" aria-describedby="location-feedback">
              <span id="location-idle">{% include 'partials/icon.html' with name='geo-alt' class_name='icon-sm' only %}</span>
              <span class="spinner-border spinner-border-sm" id="location-spinner" aria-hidden="true" hidden></span>
              <span id="location-button-label">Use my location</span>
            </button>
            <p class="search-hint" id="search-hint">Search preview. Results and maps are coming soon.</p>
            <div id="search-errors" class="form-errors" role="alert">{% for error in search_form.q.errors %}<p class="mt-2 mb-0">{{ error }}</p>{% endfor %}</div>
          </form>
          <p class="location-feedback" id="location-feedback" role="status" aria-live="polite" aria-atomic="true"></p>
          <div class="search-feedback" id="search-feedback" role="status" aria-live="polite" aria-atomic="true"{% if not search_preview %} hidden{% endif %}>Hospital results are not available in this preview. Nothing has been sent to a healthcare facility. For immediate emergency help, call 112.</div>
          <noscript><p class="search-hint">The location button needs JavaScript. You can still enter an area or call 112 directly.</p></noscript>
        </section>
        <div class="hero-details">
          <span>{% include 'partials/icon.html' with name='geo-alt' class_name='icon-sm' only %} Location stays in this tab</span>
          <span>{% include 'partials/icon.html' with name='phone' class_name='icon-sm' only %} Made for your phone</span>
        </div>
      </div>
      <figure class="hero-art">
        <img class="hero-photo" src="{% static 'img/care-professional-v2.png' %}" width="1122" height="1402" fetchpriority="high" alt="Illustrative portrait of a healthcare professional in blue scrubs in a bright hospital corridor.">
        <div class="hero-note">
          <span class="hero-note-icon">{% include 'partials/icon.html' with name='heart-pulse' only %}</span>
          <div><strong>People first.<br>Every step of the way.</strong><p>A clearer path to the care around you.</p></div>
        </div>
        <figcaption class="image-caption">AI-generated illustration &middot; Not a listed provider</figcaption>
      </figure>
    </div>
  </div>
</section>
<section class="emergency-section" aria-labelledby="urgent-heading">
  <div class="container">
    <div class="emergency-band">
      {% include 'partials/sos_button.html' with describedby='sos-preview-note' only %}
      <div class="emergency-copy">
        <h2 id="urgent-heading">When it's urgent, start here.</h2>
        <p id="sos-preview-note">Call 112 for immediate emergency help. SOS sharing and ambulance booking are previews only.</p>
      </div>
      <a href="tel:112" class="btn btn-primary">{% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112 directly {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</a>
    </div>
  </div>
</section>
<section class="quick-actions-section" id="quick-actions" aria-labelledby="quick-actions-heading">
  <div class="container">
    <div class="section-heading">
      <div><p class="eyebrow">Your care, connected</p><h2 id="quick-actions-heading">What do you need today?</h2></div>
      <p>Essential resources.<br>One place to start.</p>
    </div>
    <div class="care-grid">
      {% for card in quick_actions %}{% include 'partials/action_card.html' with card=card only %}{% endfor %}
    </div>
  </div>
</section>
<section class="how-section" aria-labelledby="how-heading">
  <div class="container">
    <div class="how-panel">
      <div class="how-intro">
        <p class="eyebrow">A calmer way forward</p>
        <h2 id="how-heading">For the moments<br>that matter.</h2>
        <p>Knowing where to start can make a difficult moment feel less overwhelming. We're building MEDTAP with that simple idea in mind.</p>
      </div>
      <div class="how-steps">
        <div class="simple-step"><span class="step-number" aria-hidden="true">01</span><div><h3>Call for urgent help</h3><p>Use the Call 112 shortcut to reach emergency services directly.</p></div></div>
        <div class="simple-step"><span class="step-number" aria-hidden="true">02</span><div><h3>Know what's around you</h3><p>Nearby facility search and maps are coming soon.</p></div></div>
        <div class="simple-step"><span class="step-number" aria-hidden="true">03</span><div><h3>Keep your people close</h3><p>Save medical details and emergency contacts in your private account.</p><a class="back-link" href="{% if user.is_authenticated %}{% url 'accounts:profile' %}{% else %}{% url 'accounts:register' %}{% endif %}">{% if user.is_authenticated %}View your profile{% else %}Create your account{% endif %} {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</a></div></div>
      </div>
    </div>
  </div>
</section>
{% endblock %}
{% block extra_js %}<script src="{% static 'js/home.js' %}" defer></script>{% endblock %}
```

### static/css/theme.css

Complete theme, including account-page styles near the end. The redesigned home styling remains.

```css
/* MEDTAP redesign: an original Django implementation inspired by Mediso on Framer. */
:root {
  --primary: #0077B6;
  --primary-dark: #023E8A;
  --accent: #2A9D8F;
  --emergency: #D62828;
  --bg: #F5F9FC;
  --text: #1F2933;
  --ink: #15333F;
  --muted: #526375;
  --accent-dark: #17665D;
  --surface: #FFFFFF;
  --hero-bg: #EDF5F6;
  --blue-soft: #EAF4FB;
  --teal-soft: #EAF6F3;
  --border: #D8E3E7;
  --radius: 1.5rem;
  --shadow: 0 16px 48px rgb(21 51 63 / 9%);
  --bs-body-font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  --bs-body-font-size: 1rem;
  --bs-body-line-height: 1.65;
  --bs-body-color: var(--text);
  --bs-body-bg: var(--surface);
  --bs-link-color: var(--primary-dark);
  --bs-link-hover-color: var(--ink);
}
html { scroll-behavior: smooth; scroll-padding-top: 7rem; }
body { min-width: 320px; }
body, button, input, select, textarea { font-family: var(--bs-body-font-family); }
h1, h2, h3, h4 { color: var(--ink); font-weight: 500; line-height: 1.15; }
a { text-underline-offset: .2em; }
button, input, select, .btn { font-size: 1rem; }
button, .btn, .form-control, .form-select { min-height: 44px; }
[hidden] { display: none !important; }
:focus-visible { outline: 3px solid var(--primary-dark) !important; outline-offset: 4px; }
.form-control:focus { border-color: var(--primary-dark); box-shadow: 0 0 0 3px rgb(2 62 138 / 15%); }
.container { max-width: 1240px; }
.icon { display: inline-block; width: 1.25rem; height: 1.25rem; fill: currentColor; flex-shrink: 0; vertical-align: -.18em; }
.icon-sm { width: 1rem; height: 1rem; }
.icon-lg { width: 1.75rem; height: 1.75rem; }
.skip-link { position: fixed; top: -6rem; left: 1rem; z-index: 2000; padding: .8rem 1.2rem; border-radius: .6rem; background: var(--primary-dark); color: white; }
.skip-link:focus { top: 1rem; color: white; }
.text-muted { color: var(--muted) !important; }
.eyebrow { margin-bottom: .85rem; color: var(--accent-dark); font-size: .75rem; font-weight: 600; letter-spacing: .13em; text-transform: uppercase; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: .6rem; border-radius: 999px; padding: .8rem 1.35rem; font-weight: 500; }
.btn-primary {
  --bs-btn-color: #fff;
  --bs-btn-bg: var(--primary-dark);
  --bs-btn-border-color: var(--primary-dark);
  --bs-btn-hover-color: #fff;
  --bs-btn-hover-bg: #032F67;
  --bs-btn-hover-border-color: #032F67;
  --bs-btn-active-color: #fff;
  --bs-btn-active-bg: #032F67;
  --bs-btn-active-border-color: #032F67;
}
.btn-outline-primary {
  --bs-btn-color: var(--primary-dark);
  --bs-btn-border-color: var(--border);
  --bs-btn-hover-color: var(--primary-dark);
  --bs-btn-hover-bg: var(--blue-soft);
  --bs-btn-hover-border-color: var(--primary-dark);
  --bs-btn-active-color: var(--primary-dark);
  --bs-btn-active-bg: var(--blue-soft);
  --bs-btn-active-border-color: var(--primary-dark);
}
.btn-emergency { background: var(--emergency); border: 1px solid var(--emergency); color: white; }
.btn-emergency:hover, .btn-emergency:active { background: #AF2020; border-color: #AF2020; color: white; }
.btn-close { box-sizing: border-box; width: 44px; height: 44px; min-width: 44px; min-height: 44px; background-size: .8rem; opacity: .8; }
.site-header { position: sticky; top: 0; z-index: 1020; background: rgb(255 255 255 / 98%); border-bottom: 1px solid #EAF0F2; }
.site-header .navbar { min-height: 94px; }
.navbar-brand { display: inline-flex; align-items: center; gap: .65rem; min-height: 44px; margin-right: 1.5rem; padding-block: .35rem; color: var(--ink); text-decoration: none; }
.brand-mark { display: inline-flex; align-items: center; justify-content: center; width: 39px; height: 39px; border-radius: 50%; color: white; background: var(--primary-dark); }
.brand-word { font-size: 1.65rem; font-weight: 700; line-height: 1.1; letter-spacing: -.065em; }
.brand-dot { color: var(--accent-dark); }
.preview-label { margin-left: .35rem; border: 1px solid var(--border); border-radius: 999px; padding: .15rem .5rem; color: var(--muted); font-size: .65rem; font-weight: 500; letter-spacing: .02em; }
.navbar .nav-link { display: inline-flex; align-items: center; min-height: 44px; padding: .6rem .85rem !important; color: var(--muted); font-size: .88rem; font-weight: 500; background: none; border: 0; border-radius: 999px; text-decoration: none; }
.navbar .nav-link:hover, .navbar .nav-link.active { color: var(--primary-dark); }
.navbar .nav-link.active::after { content: ""; width: 4px; height: 4px; border-radius: 50%; background: var(--primary-dark); margin-left: .4rem; }
.navbar-toggler { min-width: 44px; border-color: var(--border); color: var(--ink); border-radius: 50%; }
.navbar-actions { display: flex; align-items: center; gap: .6rem; }
.navbar-actions .btn { font-size: .85rem; padding: .65rem 1.15rem; }
.site-main { min-height: 50vh; }
.message-container { padding-top: 1.25rem; }
.alert { border-radius: .8rem; }
.alert-danger { color: #831818; background: #FFF1F1; border-color: #EAB4B4; }
.alert-info { color: var(--primary-dark); background: var(--blue-soft); border-color: var(--border); }
.alert-success { color: var(--accent-dark); background: var(--teal-soft); border-color: #B8DCD3; }
.hero-section { padding: 1.5rem 1.5rem 0; }
.hero-shell { max-width: 1360px; margin: auto; padding: 3rem; border-radius: 1.8rem; background: var(--hero-bg); }
.hero-grid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 3.25rem; align-items: center; }
.hero-copy { min-width: 0; }
.hero-kicker { display: inline-flex; align-items: center; gap: .55rem; padding: .4rem .8rem; margin-bottom: 1.4rem; border: 1px solid #C8DAD8; border-radius: 999px; color: var(--accent-dark); background: #F6FBF9; font-size: .75rem; font-weight: 500; }
.hero-title { margin: 0 0 1.4rem; font-size: clamp(2.75rem, 4.8vw, 4.5rem); font-weight: 500; letter-spacing: -.07em; line-height: 1.04; }
.hero-title span { color: var(--primary-dark); }
.hero-description { max-width: 29rem; margin-bottom: 1.8rem; font-size: 1rem; color: var(--muted); line-height: 1.75; }
.hero-art { position: relative; margin: 0; min-width: 0; padding-bottom: .9rem; }
.hero-photo { display: block; width: 100%; height: 560px; object-fit: cover; object-position: 50% 35%; border-radius: 1.25rem; background: #DCE9EC; }
.hero-note { position: absolute; left: -1.3rem; bottom: 3.1rem; display: flex; align-items: center; gap: .85rem; width: min(310px, 90%); padding: 1.1rem; border: 1px solid rgb(255 255 255 / 80%); border-radius: 1rem; box-shadow: var(--shadow); background: white; }
.hero-note-icon { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 46px; height: 46px; border-radius: .85rem; color: var(--primary-dark); background: var(--blue-soft); }
.hero-note strong { display: block; font-size: .9rem; font-weight: 600; line-height: 1.4; color: var(--ink); }
.hero-note p { margin: .25rem 0 0; color: var(--muted); font-size: .75rem; line-height: 1.5; }
.image-caption { position: absolute; right: .2rem; bottom: -.65rem; margin: 0; color: var(--muted); font-size: .65rem; }
.search-panel { padding: 1.2rem; border: 1px solid #D5E2E4; border-radius: 1.1rem; background: var(--surface); box-shadow: 0 6px 18px rgb(21 51 63 / 3%); }
.search-panel h2 { font-size: 1rem; font-weight: 600; margin: 0 0 .8rem; letter-spacing: -.02em; }
.search-controls { display: flex; align-items: stretch; gap: .55rem; }
.query-field { display: flex; align-items: center; flex: 1; min-width: 0; gap: .25rem; border: 1px solid #7A9099; border-radius: 999px; padding-left: .8rem; color: var(--muted); background: #FAFCFC; }
.query-field:focus-within { border-color: var(--primary-dark); box-shadow: 0 0 0 2px rgb(2 62 138 / 15%); }
.query-field .form-control { min-width: 0; min-height: 50px; padding: .65rem .65rem .65rem .3rem; border: 0; border-radius: 999px; background: transparent; color: var(--text); font-size: 1rem; box-shadow: none; }
.query-field .form-control:focus-visible { outline-offset: 0; }
.query-field .form-control::placeholder { color: var(--muted); opacity: 1; font-size: .85rem; }
.search-controls .btn { padding-inline: 1rem; font-size: .85rem; white-space: nowrap; }
.location-button { display: inline-flex; align-items: center; gap: .45rem; margin-top: .4rem; padding: .4rem 0; min-height: 44px; color: var(--primary-dark); border: 0; background: transparent; font-size: .8rem; text-align: left; }
.location-button:hover { text-decoration: underline; text-underline-offset: .2em; }
.location-button:disabled { opacity: .8; }
.search-hint { margin: .1rem 0 0; color: var(--muted); font-size: .73rem; line-height: 1.6; }
.location-feedback { margin: .6rem 0 0; color: var(--primary-dark); font-size: .85rem; }
.location-feedback:empty { display: none; }
.search-feedback { margin-top: .8rem; padding: .85rem; border: 1px solid var(--border); border-radius: .7rem; color: var(--primary-dark); background: var(--blue-soft); font-size: .9rem; }
.form-errors { color: var(--primary-dark); font-size: .9rem; }
.hero-details { display: flex; align-items: center; flex-wrap: wrap; gap: .75rem 1rem; color: var(--muted); font-size: .73rem; margin-top: 1.1rem; }
.hero-details span { display: inline-flex; align-items: center; gap: .4rem; }
.hero-details .icon { color: var(--accent-dark); }
.emergency-section { padding: 1.5rem 0 0; }
.emergency-band { display: flex; align-items: center; gap: 1.5rem; border: 1px solid #E9D4D1; border-radius: 1.25rem; padding: 1.3rem 1.6rem; background: #FFFAF9; }
.sos-button { display: flex; flex-shrink: 0; flex-direction: column; justify-content: center; align-items: center; gap: 0; width: 88px; height: 88px; min-height: 88px; padding: 0; color: white; background: var(--emergency); border: 5px solid white; border-radius: 50%; animation: sos-pulse 3.2s ease-out infinite; }
.sos-button:hover { color: white; background: #AF2020; }
.sos-button strong { font-size: 1.45rem; font-weight: 700; line-height: 1.2; letter-spacing: .03em; }
.sos-button span { font-size: .65rem; }
.emergency-copy { flex: 1; min-width: 0; }
.emergency-copy h2 { font-size: 1.3rem; letter-spacing: -.035em; margin: 0 0 .35rem; }
.emergency-copy p { margin: 0; max-width: 41rem; color: var(--muted); font-size: 1rem; }
.emergency-band > .btn { flex-shrink: 0; }
.quick-actions-section { padding: 5.5rem 0; }
.section-heading { display: flex; align-items: end; justify-content: space-between; gap: 2rem; margin-bottom: 2rem; }
.section-heading h2 { margin: 0; font-size: clamp(2rem, 3.1vw, 2.75rem); letter-spacing: -.055em; }
.section-heading > p { max-width: 17rem; margin: 0 0 .2rem; color: var(--muted); font-size: 1rem; }
.care-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
.action-card { display: flex; flex-direction: column; align-items: flex-start; width: 100%; height: 100%; min-width: 0; min-height: 225px; padding: 1.7rem; border: 1px solid var(--border); border-radius: 1.1rem; background: white; color: var(--text); text-align: left; text-decoration: none; transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease; }
.action-card:hover { color: var(--text); border-color: #99BEC6; box-shadow: 0 10px 30px rgb(21 51 63 / 6%); transform: translateY(-3px); }
.action-card-top { display: flex; align-items: center; justify-content: space-between; width: 100%; margin-bottom: 1.6rem; }
.action-icon { display: inline-flex; align-items: center; justify-content: center; width: 50px; height: 50px; color: var(--primary-dark); background: var(--blue-soft); border-radius: 50%; }
.action-icon-teal { color: var(--accent-dark); background: var(--teal-soft); }
.action-arrow { display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; color: var(--ink); border: 1px solid var(--border); border-radius: 50%; }
.action-title { font-size: 1.2rem; line-height: 1.3; font-weight: 500; letter-spacing: -.03em; color: var(--ink); }
.action-description { display: block; margin-top: .55rem; font-size: 1rem; line-height: 1.6; color: var(--muted); }
.action-status { display: inline-flex; align-items: center; gap: .4rem; font-size: .7rem; color: var(--muted); margin-top: 1rem; }
.action-status::before { content: ""; width: 5px; height: 5px; border-radius: 50%; background: #7A8B95; }
.action-status-ready { color: var(--accent-dark); }
.action-status-ready::before { background: var(--accent-dark); }
.how-section { padding: 0 0 5.5rem; }
.how-panel { display: grid; grid-template-columns: 1fr 1.15fr; gap: 4rem; padding: 3rem; border-radius: 1.5rem; background: var(--hero-bg); }
.how-intro h2 { font-size: clamp(2rem, 3vw, 2.65rem); letter-spacing: -.055em; }
.how-intro > p:last-child { max-width: 24rem; margin: 1rem 0 0; color: var(--muted); font-size: 1rem; }
.simple-step { display: flex; align-items: start; gap: 1.1rem; padding: 1.15rem 0; border-bottom: 1px solid #CEDFE2; }
.simple-step:first-child { padding-top: .25rem; }
.simple-step:last-child { border-bottom: 0; padding-bottom: 0; }
.step-number { color: var(--accent-dark); font-size: .8rem; line-height: 1.6; padding-top: .15rem; }
.simple-step h3 { font-size: 1.05rem; font-weight: 500; margin: 0 0 .35rem; }
.simple-step p { font-size: 1rem; color: var(--muted); margin: 0; }
.site-footer { background: #102F40; color: white; padding: 3.5rem 0 1.4rem; }
.site-footer .navbar-brand { color: white; }
.site-footer .brand-mark { background: white; color: #102F40; }
.site-footer .brand-dot { color: #9ED4C5; }
.footer-description { max-width: 23rem; margin-top: 1.2rem; color: #C0D2DF; font-size: .9rem; }
.footer-label { color: #C0D2DF; font-size: .72rem; font-weight: 500; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .8rem; }
.footer-call { display: inline-flex; align-items: center; gap: .75rem; min-height: 44px; color: white; font-size: 2.8rem; font-weight: 500; letter-spacing: -.04em; text-decoration: none; }
.footer-call:hover { color: #C9E6F5; }
.site-footer .text-muted { color: #C0D2DF !important; }
.site-footer :focus-visible { outline-color: white !important; }
.footer-disclaimer { max-width: 30rem; color: #E2ECF1; font-size: 1rem; }
.footer-disclaimer strong { display: block; color: white; font-weight: 500; margin-bottom: .6rem; }
.footer-bottom { display: flex; justify-content: space-between; flex-wrap: wrap; gap: .75rem; margin-top: 2.5rem; padding-top: 1.2rem; border-top: 1px solid #3A5361; color: #C0D2DF; font-size: .75rem; }
.mobile-emergency-bar { display: none; }
.modal-content { border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); }
.modal-header { padding: 1.2rem 1.4rem; border-color: var(--border); }
.modal-title { font-size: 1.2rem; font-weight: 500; }
.modal-body, .modal-footer { padding: 1.2rem 1.4rem; }
.modal-footer { border-color: var(--border); }
.critical-note { padding: .85rem; border-left: 3px solid var(--emergency); border-radius: .3rem; color: #831818; background: #FFF1F1; }
@keyframes sos-pulse {
  0%, 75%, 100% { box-shadow: 0 0 0 1px #E5C1BC, 0 0 0 6px rgb(214 40 40 / 4%); }
  40% { box-shadow: 0 0 0 1px #E5C1BC, 0 0 0 13px rgb(214 40 40 / 0%); }
}
@media (min-width: 992px) {
  .navbar-collapse { justify-content: flex-end; gap: 1.5rem; }
  .navbar-nav { gap: .15rem; }
}
@media (max-width: 1199.98px) {
  .hero-shell { padding: 2rem; }
  .hero-grid { gap: 2rem; }
  .hero-photo { height: 530px; }
  .hero-title { font-size: 3.5rem; }
  .navbar .nav-link { padding-inline: .65rem !important; }
  .navbar-collapse { gap: .7rem; }
}
@media (max-width: 991.98px) {
  body { padding-bottom: calc(82px + env(safe-area-inset-bottom)); }
  .site-header .navbar { min-height: 78px; }
  .navbar-collapse { padding-block: .75rem; }
  .navbar .nav-link { width: 100%; padding-inline: .85rem !important; }
  .navbar-actions { padding-top: .75rem; }
  .hero-grid { grid-template-columns: 1fr 1fr; gap: 1.5rem; }
  .hero-shell { padding: 2rem; }
  .hero-title { font-size: 2.8rem; }
  .hero-photo { height: 520px; }
  .hero-description { font-size: 1rem; }
  .search-controls { flex-direction: column; }
  .search-controls > .btn { min-height: 46px; }
  .hero-note { left: -.75rem; bottom: 3rem; padding: .8rem; gap: .6rem; }
  .hero-note-icon { width: 38px; height: 38px; }
  .hero-note strong { font-size: .8rem; }
  .hero-note p { font-size: .7rem; }
  .emergency-band { flex-wrap: wrap; gap: 1.2rem; }
  .emergency-copy { flex-basis: calc(100% - 110px); }
  .emergency-band > .btn:not(.sos-button) { margin-left: 110px; }
  .quick-actions-section { padding-block: 4rem; }
  .care-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .how-panel { gap: 2rem; padding: 2rem; }
  .how-section { padding-bottom: 4rem; }
  .mobile-emergency-bar { position: fixed; display: flex; justify-content: space-between; align-items: center; gap: .75rem; left: 0; right: 0; bottom: 0; z-index: 1030; padding: .6rem 1.25rem calc(.6rem + env(safe-area-inset-bottom)); border-top: 1px solid var(--border); background: white; box-shadow: 0 -4px 18px rgb(21 51 63 / 6%); }
  .mobile-emergency-bar p { font-size: .75rem; color: var(--muted); margin: 0; line-height: 1.4; }
  .mobile-emergency-bar strong { display: block; color: var(--text); font-weight: 600; }
  .mobile-bar-actions { display: flex; align-items: center; gap: .6rem; }
  .mobile-bar-actions > .btn { padding: .7rem 1rem; font-size: .85rem; }
  .sos-button-compact { min-height: 48px; height: 48px; width: 48px; border: 0; animation: none; }
  .sos-button-compact strong { font-size: .85rem; }
  .sos-button-compact span { font-size: .5rem; }
}
@media (max-width: 767.98px) {
  .hero-section { padding: .75rem .75rem 0; }
  .hero-shell { padding: 2rem 1.5rem 1.5rem; }
  .hero-grid { grid-template-columns: 1fr; gap: 1.75rem; }
  .hero-title { font-size: clamp(2.75rem, 8vw, 3.8rem); }
  .hero-description { max-width: 31rem; }
  .search-controls { flex-direction: row; }
  .hero-photo { height: 350px; object-position: 50% 32%; }
  .hero-note { left: .8rem; bottom: 2.5rem; width: 280px; }
  .hero-note strong { font-size: .85rem; }
  .hero-art { padding-bottom: 1.1rem; }
  .image-caption { right: .1rem; bottom: -.1rem; }
  .section-heading { flex-direction: column; align-items: start; gap: 1rem; }
  .section-heading > p { max-width: none; }
  .how-panel { grid-template-columns: 1fr; gap: 1.75rem; }
}
@media (max-width: 575.98px) {
  .container { padding-inline: 1.25rem; }
  .site-header .navbar { min-height: 74px; }
  .brand-word { font-size: 1.5rem; }
  .brand-mark { width: 36px; height: 36px; }
  .preview-label { font-size: .6rem; }
  .hero-shell { border-radius: 1.25rem; padding: 1.6rem 1.15rem 1.25rem; }
  .hero-kicker { margin-bottom: 1.2rem; font-size: .7rem; }
  .hero-title { font-size: clamp(2.6rem, 10.5vw, 3.5rem); margin-bottom: 1.1rem; }
  .hero-description { margin-bottom: 1.4rem; }
  .search-panel { padding: 1rem; }
  .search-controls { flex-direction: column; }
  .hero-photo { height: 300px; border-radius: 1rem; }
  .hero-note { width: 245px; max-width: calc(100% - 1.6rem); }
  .hero-details { gap: .55rem; font-size: .7rem; }
  .emergency-section { padding-top: 1.1rem; }
  .emergency-band { padding: 1.2rem; gap: 1rem; }
  .emergency-copy { flex-basis: calc(100% - 92px); }
  .emergency-copy h2 { font-size: 1.1rem; }
  .emergency-copy p { font-size: .9rem; }
  .emergency-band > .sos-button { width: 72px; height: 72px; min-height: 72px; }
  .emergency-band > .sos-button strong { font-size: 1.2rem; }
  .emergency-band > .btn:not(.sos-button) { margin-left: 0; width: 100%; }
  .quick-actions-section { padding-block: 3rem; }
  .section-heading { margin-bottom: 1.5rem; }
  .care-grid { gap: .65rem; }
  .action-card { padding: 1rem; min-height: 235px; border-radius: .85rem; }
  .action-card-top { margin-bottom: 1.2rem; }
  .action-icon { width: 42px; height: 42px; }
  .action-arrow { width: 27px; height: 27px; }
  .action-arrow .icon { width: .8rem; height: .8rem; }
  .action-title { font-size: 1rem; }
  .action-description { font-size: 1rem; line-height: 1.5; }
  .action-status { font-size: .65rem; }
  .how-panel { padding: 1.5rem; border-radius: 1.1rem; }
  .how-section { padding-bottom: 3rem; }
  .site-footer { padding-top: 2.5rem; }
  .footer-bottom { margin-top: 1.5rem; }
  .mobile-emergency-bar { padding-inline: 1rem; }
  .mobile-emergency-bar p { font-size: .65rem; }
  .mobile-bar-actions { gap: .45rem; }
}
/* Accounts: shared forms and a private medical ID, using the existing theme. */
.account-section { padding: 3rem 0 4.5rem; }
.auth-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; align-items: start; }
.auth-intro { padding: 2.7rem; border-radius: var(--radius); background: var(--hero-bg); }
.auth-intro h1 { font-size: clamp(2rem, 3.2vw, 3rem); letter-spacing: -.055em; margin-bottom: 1.4rem; }
.auth-intro > p { font-size: 1rem; color: var(--muted); }
.auth-intro > .eyebrow { color: var(--accent-dark); font-size: .75rem; }
.auth-benefits { display: grid; gap: 1.2rem; margin-top: 2rem; }
.auth-benefits > div { display: flex; align-items: start; gap: .8rem; color: var(--muted); font-size: 1rem; }
.auth-benefits .icon { margin-top: .2rem; color: var(--accent-dark); }
.auth-intro .auth-reminder { border-top: 1px solid #CADCE0; padding-top: 1.3rem; margin: 2rem 0 0; }
.account-panel { padding: 2rem; min-width: 0; border: 1px solid var(--border); border-radius: 1.2rem; background: white; }
.account-panel > h1 { font-size: clamp(1.8rem, 3vw, 2.4rem); letter-spacing: -.045em; }
.account-panel > h2, .panel-title-row > h2 { font-size: 1.5rem; letter-spacing: -.035em; margin-bottom: 1rem; }
.field-wrapper { margin-bottom: 1.35rem; min-width: 0; }
.field-wrapper .form-label { display: block; font-weight: 500; font-size: .9rem; margin-bottom: .5rem; }
.field-wrapper .form-control, .field-wrapper .form-select { min-height: 48px; padding: .7rem .85rem; border: 1px solid #7A9099; border-radius: .6rem; background-color: #FCFDFD; font-size: 1rem; }
.field-wrapper textarea.form-control { resize: vertical; }
.field-wrapper [aria-invalid='true'] { border: 2px solid var(--primary-dark); }
.field-help { margin-top: .45rem; color: var(--muted); font-size: .8rem; line-height: 1.6; }
.field-help ul { margin: .25rem 0 0; padding-left: 1.2rem; }
.field-errors { margin: .45rem 0 0; padding-left: 1.2rem; color: var(--primary-dark); font-size: .9rem; }
.required-marker { color: var(--primary-dark); }
.optional-label { color: var(--muted); font-weight: 400; font-size: .8rem; }
.checkbox-label { display: flex; min-height: 44px; align-items: center; gap: .8rem; cursor: pointer; }
.checkbox-label .form-check-input { width: 1.2rem; height: 1.2rem; margin: 0; float: none; flex-shrink: 0; border-color: #6B818A; }
.checkbox-label .form-check-input:checked { background-color: var(--primary-dark); border-color: var(--primary-dark); }
.form-error-summary { padding: 1rem 1.2rem; margin-bottom: 1.5rem; border: 2px solid var(--primary-dark); border-radius: .7rem; background: var(--blue-soft); color: var(--primary-dark); }
.form-error-summary h2 { font-size: 1.1rem; font-weight: 600; margin-bottom: .5rem; }
.form-error-summary ul { margin: .4rem 0; padding-left: 1.2rem; }
.form-error-summary a { display: flex; align-items: center; min-height: 44px; color: var(--primary-dark); font-size: .9rem; }
.auth-switch { margin: 1.4rem 0 0; font-size: .9rem; color: var(--muted); }
.auth-switch a { display: inline-flex; align-items: center; min-height: 44px; font-weight: 500; }
.account-form-shell { max-width: 740px; margin: 0 auto; }
.back-link { display: inline-flex; align-items: center; gap: .5rem; min-height: 44px; margin-bottom: .8rem; color: var(--primary-dark); font-size: .9rem; }
.account-form-actions { display: flex; flex-wrap: wrap; align-items: center; gap: .75rem; margin-top: 1.6rem; }
.profile-page-heading { display: flex; align-items: end; justify-content: space-between; flex-wrap: wrap; gap: 1.5rem; margin-bottom: 2rem; }
.profile-page-heading h1 { font-size: clamp(2rem, 3.5vw, 3rem); letter-spacing: -.055em; }
.profile-layout { display: grid; grid-template-columns: .9fr 1.3fr; gap: 2rem; align-items: start; }
.medical-id { background: var(--hero-bg); border: 1px solid #C6D9DB; border-radius: 1.4rem; padding: 2rem; overflow-wrap: anywhere; }
.medical-id-top { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 1rem; align-items: center; margin-bottom: 2rem; }
.medical-id-top > span:first-child { color: var(--primary-dark); font-weight: 600; display: inline-flex; gap: .5rem; align-items: center; font-size: .85rem; }
.privacy-label { display: inline-flex; align-items: center; gap: .35rem; color: var(--accent-dark); font-size: .7rem; }
.medical-id h2 { font-size: 1.8rem; letter-spacing: -.045em; margin-bottom: .25rem; }
.medical-id-username { font-size: .85rem; color: var(--muted); }
.blood-group-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; padding-block: 1.2rem; margin-top: 1.8rem; border-block: 1px solid #C6D9DB; }
.medical-id-label { font-size: .8rem; color: var(--muted); margin-bottom: .35rem; }
.blood-group-value { font-size: 2rem; font-weight: 500; color: var(--primary-dark); margin: 0; line-height: 1.3; }
.self-reported, .primary-label { display: inline-flex; font-size: .7rem; padding: .25rem .6rem; border-radius: 999px; color: var(--accent-dark); background: #F5FCF9; border: 1px solid #B7D2C9; }
.medical-id-caption { font-size: .8rem; color: var(--muted); margin: 1.2rem 0 0; }
.profile-privacy-note { margin: 1.1rem .3rem 0; color: var(--muted); font-size: .8rem; }
.profile-details { display: grid; gap: 1.5rem; min-width: 0; }
.medical-detail { padding-block: 1.1rem; border-bottom: 1px solid var(--border); }
.medical-detail h3 { font-size: .85rem; color: var(--muted); font-weight: 500; }
.medical-detail p { margin-bottom: 0; font-size: 1rem; overflow-wrap: anywhere; }
.panel-title-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: .75rem; margin-bottom: .5rem; }
.panel-title-row > h2 { margin: 0; }
.panel-title-row > .btn { font-size: .8rem; padding-inline: .9rem; }
.contact-item { padding-top: 1.5rem; margin-top: 1.5rem; border-top: 1px solid var(--border); overflow-wrap: anywhere; }
.contact-heading { display: flex; flex-wrap: wrap; align-items: center; gap: .6rem; }
.contact-heading h3 { font-size: 1.1rem; font-weight: 500; margin: 0; }
.contact-relationship { color: var(--muted); font-size: .85rem; margin: .3rem 0; }
.contact-phone { margin-bottom: .75rem; font-size: 1rem; }
.contact-actions { display: flex; flex-wrap: wrap; gap: .5rem; }
.contact-actions .btn { font-size: .8rem; padding: .6rem .9rem; }
.empty-contacts { padding: 2rem 0 .5rem; }
.empty-contacts h3 { font-size: 1.2rem; margin-top: 1rem; }
.empty-contacts p { color: var(--muted); font-size: 1rem; margin-bottom: 0; }
.logout-form { margin: 0; }
.navbar-actions { flex-wrap: wrap; }
@media (max-width: 991.98px) {
  .auth-layout { gap: 1.5rem; }
  .auth-intro, .account-panel { padding: 1.5rem; }
  .profile-layout { grid-template-columns: 1fr 1.3fr; gap: 1.3rem; }
  .medical-id { padding: 1.5rem; }
}
@media (max-width: 767.98px) {
  .account-section { padding: 1.75rem 0 3rem; }
  .auth-layout, .profile-layout { grid-template-columns: 1fr; }
  .auth-benefits { display: none; }
  .auth-intro h1 { font-size: 2rem; }
  .auth-intro .auth-reminder { margin-top: 1rem; padding-top: 1rem; }
  .profile-page-heading { align-items: start; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

### accounts/tests.py

34 meaningful account, privacy, ownership, CSRF, validation, workflow and redirect tests.

```python
from unittest.mock import patch

from django.contrib.auth import SESSION_KEY
from django.core.exceptions import ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import EmergencyContact, MedicalProfile, User
from .services import save_emergency_contact

# Fictional test credentials/data; the test runner uses a separate test database.
TEST_PASSWORD = "Harbor!River92-Train"


def registration_data(**changes):
    data = {
        "first_name": "Fictional", "last_name": "Student", "username": "new-student",
        "email": "student@example.invalid", "password1": TEST_PASSWORD,
        "password2": TEST_PASSWORD,
    }
    data.update(changes)
    return data


def contact_data(**changes):
    data = {
        "name": "Fictional Contact", "relationship": "Sibling", "phone": "0000000000",
    }
    data.update(changes)
    return data


class RegistrationTests(TestCase):
    def test_public_auth_pages_render_and_are_not_cached(self):
        for name in ("accounts:register", "accounts:login"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "csrfmiddlewaretoken")
            self.assertIn("no-store", response["Cache-Control"])

    def test_registration_creates_profile_hashes_password_and_logs_in(self):
        response = self.client.post(reverse("accounts:register"), registration_data(
            is_staff="on", is_superuser="on",
        ))
        self.assertRedirects(response, reverse("accounts:profile_edit"), fetch_redirect_response=False)
        user = User.objects.get(username="new-student")
        self.assertTrue(user.check_password(TEST_PASSWORD))
        self.assertNotEqual(user.password, TEST_PASSWORD)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(MedicalProfile.objects.get(user=user).blood_group, "unknown")
        self.assertEqual(self.client.session[SESSION_KEY], str(user.pk))

    def test_registered_user_can_sign_out_and_sign_back_in_with_same_credentials(self):
        data = registration_data()
        response = self.client.post(reverse("accounts:register"), data)
        self.assertRedirects(response, reverse("accounts:profile_edit"), fetch_redirect_response=False)
        user = User.objects.get(username=data["username"])
        self.client.post(reverse("accounts:logout"))
        self.assertNotIn(SESSION_KEY, self.client.session)
        response = self.client.post(reverse("accounts:login"), {
            "username": data["username"], "password": data["password1"],
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        self.assertEqual(self.client.session[SESSION_KEY], str(user.pk))

    def test_duplicate_username_is_rejected_without_showing_password(self):
        User.objects.create_user(username="new-student")
        response = self.client.post(reverse("accounts:register"), registration_data())
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.context["form"].errors)
        self.assertNotContains(response, TEST_PASSWORD)
        self.assertEqual(User.objects.count(), 1)

    def test_weak_or_mismatched_passwords_are_rejected(self):
        for changes in (
            {"password1": "12345678", "password2": "12345678"},
            {"password2": "A-different-password-93!"},
        ):
            response = self.client.post(reverse("accounts:register"), registration_data(**changes))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        self.assertFalse(User.objects.exists())

    def test_registration_summary_explains_failure_and_links_exact_field_errors(self):
        response = self.client.post(reverse("accounts:register"), registration_data(
            password1="12345678", password2="12345678",
        ))
        self.assertContains(response, "Your account hasn't been created")
        self.assertContains(response, 'id="form-error-summary"')
        self.assertContains(response, 'href="#id_password2"')
        self.assertContains(response, "This password is too common.", count=2)
        self.assertFalse(User.objects.exists())

    def test_invalid_email_is_rejected_but_blank_email_is_optional(self):
        response = self.client.post(reverse("accounts:register"), registration_data(email="invalid"))
        self.assertIn("email", response.context["form"].errors)
        response = self.client.post(reverse("accounts:register"), registration_data(email=""))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.get(username="new-student").email, "")

    def test_profile_creation_failure_rolls_back_user_creation(self):
        with patch("accounts.views.MedicalProfile.objects.create", side_effect=RuntimeError("Test failure")):
            with self.assertRaises(RuntimeError):
                self.client.post(reverse("accounts:register"), registration_data())
        self.assertFalse(User.objects.exists())
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_csrf_is_required_and_valid_token_allows_registration(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("accounts:register"), registration_data())
        self.assertEqual(response.status_code, 403)
        client.get(reverse("accounts:register"))
        token = client.cookies["csrftoken"].value
        response = client.post(reverse("accounts:register"), registration_data(csrfmiddlewaretoken=token))
        self.assertEqual(response.status_code, 302)
        self.assertIn(SESSION_KEY, client.session)


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="fictional-student", password=TEST_PASSWORD)

    def credentials(self, **extra):
        return {"username": self.user.username, "password": TEST_PASSWORD, **extra}

    def test_login_redirects_to_profile(self):
        response = self.client.post(reverse("accounts:login"), self.credentials())
        self.assertRedirects(response, reverse("accounts:profile"), fetch_redirect_response=False)
        self.assertEqual(self.client.session[SESSION_KEY], str(self.user.pk))

    def test_invalid_credentials_do_not_log_in_or_echo_password(self):
        response = self.client.post(reverse("accounts:login"), self.credentials(password="wrong-password"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertNotContains(response, "wrong-password")

    def test_inactive_user_cannot_log_in(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        response = self.client.post(reverse("accounts:login"), self.credentials())
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_safe_local_next_is_preserved(self):
        destination = reverse("accounts:profile_edit")
        response = self.client.get(reverse("accounts:login"), {"next": destination})
        self.assertEqual(response.context["next"], destination)
        response = self.client.post(reverse("accounts:login"), self.credentials(next=destination))
        self.assertRedirects(response, destination, fetch_redirect_response=False)

    @override_settings(LOGIN_REDIRECT_URL="/accounts/profile/")
    def test_default_destination_accepts_a_url_path_as_well_as_a_route_name(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["next"], "/accounts/profile/")

    def test_https_login_rejects_an_http_redirect(self):
        response = self.client.post(
            reverse("accounts:login"), self.credentials(next="http://testserver/accounts/profile/edit/"),
            secure=True,
        )
        self.assertRedirects(response, reverse("accounts:profile"), fetch_redirect_response=False)

    def test_external_and_protocol_relative_next_are_rejected(self):
        for destination in ("https://attacker.example/", "//attacker.example/", "///attacker.example/", "javascript:alert(1)"):
            client = Client()
            response = client.post(reverse("accounts:login"), self.credentials(next=destination))
            self.assertRedirects(response, reverse("accounts:profile"), fetch_redirect_response=False)

    def test_logout_is_post_only_and_flushes_session(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        self.assertIn(SESSION_KEY, self.client.session)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("core:home"))
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_logout_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(reverse("accounts:logout")).status_code, 403)
        self.assertIn(SESSION_KEY, client.session)
        client.get(reverse("accounts:profile"))
        token = client.cookies["csrftoken"].value
        response = client.post(reverse("accounts:logout"), {"csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(SESSION_KEY, client.session)

    def test_signed_in_users_are_redirected_away_from_auth_pages(self):
        self.client.force_login(self.user)
        for name in ("accounts:login", "accounts:register"):
            self.assertRedirects(self.client.get(reverse(name)), reverse("accounts:profile"))


class OwnedProfileTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="fictional-owner", first_name="Fictional")
        cls.other = User.objects.create_user(username="other-student")
        cls.profile = MedicalProfile.objects.create(user=cls.user)
        cls.other_profile = MedicalProfile.objects.create(user=cls.other, allergies="OTHER PRIVATE NOTE")
        cls.foreign_contact = EmergencyContact.objects.create(
            profile=cls.other_profile, name="Other Private Contact", relationship="Friend", phone="0000000001",
        )

    def setUp(self):
        self.client.force_login(self.user)


class ProfileTests(OwnedProfileTestCase):
    def test_anonymous_users_must_log_in(self):
        client = Client()
        for name, args in (
            ("accounts:profile", []), ("accounts:profile_edit", []),
            ("accounts:contact_add", []), ("accounts:contact_edit", [self.foreign_contact.pk]),
            ("accounts:contact_delete", [self.foreign_contact.pk]),
        ):
            destination = reverse(name, args=args)
            response = client.get(destination)
            self.assertRedirects(response, reverse("accounts:login") + "?next=" + destination)

    def test_profile_only_displays_owned_data_and_is_not_cached(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertContains(response, "Fictional")
        self.assertNotContains(response, "OTHER PRIVATE NOTE")
        self.assertNotContains(response, "Other Private Contact")
        self.assertIn("no-store", response["Cache-Control"])

    def test_profile_update_ignores_forged_ownership_fields(self):
        response = self.client.post(reverse("accounts:profile_edit"), {
            "blood_group": "AB+", "allergies": "Fictional allergy", "medical_conditions": "Fictional condition",
            "user": self.other.pk, "id": self.other_profile.pk,
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        self.profile.refresh_from_db()
        self.other_profile.refresh_from_db()
        self.assertEqual(self.profile.blood_group, "AB+")
        self.assertEqual(self.profile.user_id, self.user.pk)
        self.assertEqual(self.other_profile.allergies, "OTHER PRIVATE NOTE")

    def test_invalid_blood_group_and_oversized_notes_do_not_save(self):
        response = self.client.post(reverse("accounts:profile_edit"), {
            "blood_group": "Z+", "allergies": "x" * 2001, "medical_conditions": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("blood_group", response.context["form"].errors)
        self.assertIn("allergies", response.context["form"].errors)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.allergies, "")

    def test_medical_text_is_escaped(self):
        self.profile.allergies = '<script>alert("fictional")</script>'
        self.profile.save()
        response = self.client.get(reverse("accounts:profile"))
        self.assertNotContains(response, '<script>alert("fictional")</script>')
        self.assertContains(response, "&lt;script&gt;")

    def test_existing_account_without_profile_gets_one_only_on_save(self):
        self.profile.delete()
        self.assertEqual(self.client.get(reverse("accounts:profile")).status_code, 200)
        self.assertEqual(self.client.get(reverse("accounts:profile_edit")).status_code, 200)
        self.assertFalse(MedicalProfile.objects.filter(user=self.user).exists())
        self.assertRedirects(self.client.get(reverse("accounts:contact_add")), reverse("accounts:profile_edit"))
        response = self.client.post(reverse("accounts:profile_edit"), {
            "blood_group": "unknown", "allergies": "", "medical_conditions": "",
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        self.assertEqual(MedicalProfile.objects.filter(user=self.user).count(), 1)


class ContactTests(OwnedProfileTestCase):
    def test_add_normalises_phone_and_ignores_forged_profile(self):
        response = self.client.post(reverse("accounts:contact_add"), contact_data(
            phone="(00000) 00000", profile=self.other_profile.pk,
        ))
        self.assertRedirects(response, reverse("accounts:profile"))
        contact = self.profile.emergency_contacts.get()
        self.assertEqual(contact.phone, "0000000000")
        self.assertFalse(contact.is_primary)

    def test_invalid_phone_and_blank_name_are_rejected(self):
        response = self.client.post(reverse("accounts:contact_add"), contact_data(name="  ", phone="abc"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("phone", response.context["form"].errors)
        self.assertIn("name", response.context["form"].errors)
        self.assertFalse(self.profile.emergency_contacts.exists())

    def test_new_primary_contact_replaces_old_primary(self):
        old = EmergencyContact.objects.create(profile=self.profile, is_primary=True, **contact_data())
        response = self.client.post(reverse("accounts:contact_add"), contact_data(name="New Fictional Contact", is_primary="on"))
        self.assertRedirects(response, reverse("accounts:profile"))
        old.refresh_from_db()
        self.assertFalse(old.is_primary)
        self.assertEqual(self.profile.emergency_contacts.filter(is_primary=True).get().name, "New Fictional Contact")

    def test_editing_contact_can_switch_primary(self):
        old = EmergencyContact.objects.create(profile=self.profile, is_primary=True, **contact_data())
        target = EmergencyContact.objects.create(profile=self.profile, **contact_data(name="Second Fictional Contact"))
        response = self.client.post(reverse("accounts:contact_edit", args=[target.pk]), contact_data(
            name="Updated Fictional Contact", is_primary="on",
        ))
        self.assertRedirects(response, reverse("accounts:profile"))
        old.refresh_from_db()
        target.refresh_from_db()
        self.assertFalse(old.is_primary)
        self.assertTrue(target.is_primary)
        self.assertEqual(target.name, "Updated Fictional Contact")

    def test_foreign_contacts_cannot_be_read_edited_or_deleted(self):
        for route in ("accounts:contact_edit", "accounts:contact_delete"):
            url = reverse(route, args=[self.foreign_contact.pk])
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, contact_data()).status_code, 404)
        self.foreign_contact.refresh_from_db()
        self.assertEqual(self.foreign_contact.name, "Other Private Contact")

    def test_remove_get_only_confirms_and_post_deletes(self):
        contact = EmergencyContact.objects.create(profile=self.profile, **contact_data())
        url = reverse("accounts:contact_delete", args=[contact.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(EmergencyContact.objects.filter(pk=contact.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("accounts:profile"))
        self.assertFalse(EmergencyContact.objects.filter(pk=contact.pk).exists())

    def test_contact_mutations_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        contact = EmergencyContact.objects.create(profile=self.profile, **contact_data())
        for url in (
            reverse("accounts:contact_add"), reverse("accounts:contact_edit", args=[contact.pk]),
            reverse("accounts:contact_delete", args=[contact.pk]), reverse("accounts:profile_edit"),
        ):
            self.assertEqual(client.post(url, contact_data()).status_code, 403)
        self.assertEqual(self.profile.emergency_contacts.count(), 1)

    def test_failed_save_rolls_back_primary_switch(self):
        old = EmergencyContact.objects.create(profile=self.profile, is_primary=True, **contact_data())
        with self.assertRaises(ValidationError):
            save_emergency_contact(profile=self.profile, data=contact_data(phone="invalid", is_primary=True))
        old.refresh_from_db()
        self.assertTrue(old.is_primary)
        self.assertEqual(self.profile.emergency_contacts.count(), 1)

    def test_service_rejects_a_contact_from_another_profile(self):
        with self.assertRaises(ValueError):
            save_emergency_contact(profile=self.profile, contact=self.foreign_contact, data=contact_data(is_primary=False))
```

### static/js/site.js

Focuses a failed form's full error summary and retains the existing preview-dialog behaviour.

```javascript
"use strict";

// A failed form POST may otherwise restore the scroll position near Submit,
// hiding validation errors above the fold. Focus the complete error summary.
const formErrorSummary = document.getElementById("form-error-summary");
if (formErrorSummary) {
  formErrorSummary.focus();
}

// Bootstrap manages focus trapping, Escape, dismissal, and focus return for dialogs.
const previewModal = document.getElementById("feature-preview");
if (previewModal) {
  previewModal.addEventListener("show.bs.modal", (event) => {
    const trigger = event.relatedTarget;
    const critical = trigger?.dataset.previewCritical === "true";
    document.getElementById("preview-title").textContent = trigger?.dataset.previewTitle || "Coming soon";
    document.getElementById("preview-description").textContent = trigger?.dataset.previewDescription || "This feature is not available in this preview.";
    document.getElementById("preview-critical-note").hidden = !critical;
    document.getElementById("preview-call").hidden = !critical;
  });
}
```

## Verification completed

- All 34 permanent account tests pass.
- Django checks pass; makemigrations reports no model changes.
- The live home, registration, login and stylesheet URLs return HTTP 200.
- Anonymous live profile requests redirect to Login with a safe next destination.
- Temporary-database markup checks cover all seven account pages: no duplicate IDs,
  valid labels/help/error ARIA targets, CSRF in every POST form, existing icon IDs,
  and no inline styles/events. Invalid form error targets also exist.
- Tests cover password hashing, weak/mismatched passwords, duplicate usernames,
  optional/invalid email, rollback, inactive users, logout method/CSRF, private data
  isolation, forged ownership, escaping, existing users without profiles, contact
  CRUD, phone normalisation, primary switching and rollback, and safe redirects.

Browser screenshot/real viewport verification is unavailable in this environment.
The HTTP, template and behaviour checks above do not replace visual and keyboard
review in your browser. At phone width, check the menu, profile layout, form errors
and fixed emergency bar after a Ctrl+F5 refresh.

Stop here. Say **next** for Step 3: facilities management in Django admin and an
explicitly FAKE sample-data management command.