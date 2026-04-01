from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import engines, loader
from django.urls import reverse
from wagtail.admin.forms.auth import PasswordResetForm


class HtmlPasswordResetForm(PasswordResetForm):
    html_email_template_name = (
        "jinja2/wagtailadmin/account/password_reset/email_safe.html"
    )
    email_template_name = "wagtailadmin/account/password_reset/email_plain.txt"

    # fallback to django templating if template isn't in jinja2 directory
    def _render_email_template(self, template_name, context):
        if template_name and template_name.startswith("jinja2/"):
            # I dislike this removal of "jinja2/" but changing the dirs for jinja
            # in TEMPLATES, production.py to include "/jinja2" is the only way to
            # get both django and jinja working
            return (
                engines["jinja2"]
                .get_template(template_name.replace("jinja2/", ""))
                .render(context)
            )
        return loader.render_to_string(template_name, context)

    def _build_reset_url(self, context):
        """Build the full password reset URL from context, mirroring the approach
        used in the original wagtail email.txt (base_url_setting + {% url %})."""
        reset_path = reverse(
            "wagtailadmin_password_reset_confirm",
            kwargs={"uidb64": context["uid"], "token": context["token"]},
        )
        base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", None) or (
            f"{context.get('protocol', 'https')}://{context.get('domain', '')}"
        )
        return base_url.rstrip("/") + reset_path

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
        encoding="utf-8",
    ):
        subject = "The National Archives: Password Reset"

        body = self._render_email_template(email_template_name, context)

        mail = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name:
            # Pre-compute reset_url in Python (matching the original wagtail
            # email.txt approach) so the Jinja2 template doesn't need url_for.
            html_context = {**context, "reset_url": self._build_reset_url(context)}
            html_body = self._render_email_template(
                html_email_template_name, html_context
            )
            mail.attach_alternative(html_body, "text/html")

        mail.send()

    # overwrite the save method to pass the html_email_template_name to send_mail
    def save(self, *args, **kwargs):
        kwargs["html_email_template_name"] = self.html_email_template_name
        kwargs["email_template_name"] = self.email_template_name
        return super().save(*args, **kwargs)
