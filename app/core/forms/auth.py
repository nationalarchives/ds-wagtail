import importlib
import logging

from django.core.mail import EmailMultiAlternatives
from django.template import engines, loader
from wagtail.admin.forms.auth import PasswordResetForm


logger = logging.getLogger(__name__)


class HtmlPasswordResetForm(PasswordResetForm):
    html_email_template_name = "jinja2/wagtailadmin/account/password_reset/email.html"
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
        subject = self._render_email_template(subject_template_name, context)
        subject = "".join(subject.splitlines())

        body = self._render_email_template(email_template_name, context)

        mail = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name:
            html_body = self._render_email_template(html_email_template_name, context)
            try:
                premailer_transform = importlib.import_module("premailer").transform
                html_body = premailer_transform(
                    html_body,
                    allow_network=False,
                    allow_loading_external_files=False,
                    disable_validation=True,
                )
            except Exception:
                logger.exception(
                    "Failed to inline password reset email CSS; using original HTML"
                )
            mail.attach_alternative(html_body, "text/html")

        mail.send()

    # overwrite the save method to pass the html_email_template_name to send_mail
    def save(self, *args, **kwargs):
        kwargs["html_email_template_name"] = self.html_email_template_name
        kwargs["email_template_name"] = self.email_template_name
        return super().save(*args, **kwargs)
