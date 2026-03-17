from wagtail.admin.forms.auth import PasswordResetForm


class HtmlPasswordResetForm(PasswordResetForm):
    html_email_template_name = "wagtailadmin/account/password_reset/email.html"
    email_template_name = "wagtailadmin/account/password_reset/email_plain.txt"

    def save(self, *args, **kwargs):
        kwargs["html_email_template_name"] = (
            kwargs.get("html_email_template_name") or self.html_email_template_name
        )
        kwargs["email_template_name"] = (
            kwargs.get("email_template_name") or self.email_template_name
        )
        return super().save(*args, **kwargs)
