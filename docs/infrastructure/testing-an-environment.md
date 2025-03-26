# Testing an environment

You can confirm most aspects of the configuration by following these steps:

## 1. Initial setup

Access the environment via SSH and run the following management commands:

1. `python manage.py migrate` (may indicate database connection issues that need addressing)
2. `python manage.py collectstatic` (may indicate file-system permission issues that need addressing)
3. `python manage.py update_index` (may indicate search-backend issues that need addressing)
4. `python manage.py createsuperuser` (remember your username and password for use in later steps)

Now, in your browser, visit: `/admin/`

When you see the login form, enter the credentials you set for your superuser and submit the form. (a failure here may indicate an issue with the app's `SESSION_ENGINE` config).

## 2. Add/update an image

1. Select the **Images** option from the Wagtail sidebar.
2. Click the **Add image** button at the top of the page and follow the upload instructions.
3. From the listing, click on the uploaded image to edit it, and adjust the focal point.
4. If configured correctly, when you return to the list, you should see a freshly-generated thumbnail representation. The fact that you were able to save the image is evidence that the search backend is configured correctly.

## 3. Trigger a password reset

1. Sign out using the menu in the **bottom left** of the Wagtail UI.
2. From the login page, click the **Forgotton it?** link next to the password input.
3. Enter the email address you set in the `createsuperuser` step above and request a password reset link.
4. If email is configured correctly, you'll receive the email.
