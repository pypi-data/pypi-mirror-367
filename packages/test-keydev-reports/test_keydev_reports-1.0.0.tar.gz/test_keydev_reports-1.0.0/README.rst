=====
KEY_DEV-REPORTS
=====

KEY_DEV-REPORTS is a Django app to create reports.

Quick start
-----------

1. Add "keydev_reports" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "keydev_reports",
    ]

2. Run ``python manage.py migrate`` to create the keydev_reports models.

3. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a ReportTemplate model (you'll need the Admin app enabled).
