[![PyPI version](https://badge.fury.io/py/djangocms-timed-publishing.svg)](http://badge.fury.io/py/djangocms-timed-publishing)
[![Coverage Status](https://codecov.io/gh/fsbraun/djangocms-timed-publishing/graph/badge.svg?token=EQeaSCSVkU)](https://codecov.io/gh/fsbraun/djangocms-timed-publishing)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/djangocms-timed-publishing)](https://pypi.org/project/djangocms-timed-publishing/)
[![PyPI - Django Versions](https://img.shields.io/pypi/frameworkversions/django/djangocms-timed-publishing)](https://www.djangoproject.com/)
[![PyPI - django CMS Versions](https://img.shields.io/pypi/frameworkversions/django-cms/djangocms-timed-publishing)](https://www.django-cms.org/)


# djangocms-timed-publishing
django CMS Timed Publishing extends django CMS Versioning to allow for planned or limited publication of content:

* New option to publish with beginning and end dates.
  By default this is done from the versioning menu and the "Publish" button does not change behavior.
  The menu brings up a modal allowing to select time limits for the visibility of the to-be-published version:

  Alternatively, with the setting `DJANGOCMS_TIMED_PUBLISHING_BUTTON = True`, the "Publish" button changes
  behavior and always opens the modal to ask for beginning and end dates.

  Publishing from the admin - be it the page tree or the version manager - is not affected.

* Technically, the time limits do not affect the published status but only the visibility. This means, dates on published
  versions cannot be changed any more. You need to create a new draft and publish that to make a change.

* Versioning menu shows pending or expired visibility dates. "pending" is a word for a published version that is
  not yet visible. "expired" is a word for a published version not visible any more:

* "View published" button for PageContents is only offered for pages which are currently visible
  (since otherwise they'll show a 404)

* Pending or expired aliases render empty.


![Timed Publishing](timed-publishing.jpg)

## Installation

1. Install the package using pip:

    ```bash
    pip install git+https://github.com/fsbraun/djangocms-timed-publishing
    ```

2. Add `"djangocms_timed_publishing"` after  `"djangocms_versioning"` to your `INSTALLED_APPS` in `settings.py`:

    ```python
    INSTALLED_APPS = [
         # ...
         "djangocms_versioning",
         "djangocms_timed_publishing",
         # ...
    ]
    ```

3. Run migrations:

    ```bash
    python manage.py migrate
    ```
