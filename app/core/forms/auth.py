from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import engines, loader
from django.urls import reverse
from wagtail.admin.forms.auth import PasswordResetForm


class HtmlPasswordResetForm(PasswordResetForm):
    html_email_template_name = (
        "wagtailadmin/account/password_reset/password_reset_email.html"
    )
    email_template_name = "wagtailadmin/account/password_reset/email_plain.txt"

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

        body = loader.render_to_string(email_template_name, context)

        mail = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name:
            # Pre-compute reset_url in Python (matching the original wagtail
            # email.txt approach) so the Jinja2 template doesn't need url_for.
            html_context = {**context, "reset_url": self._build_reset_url(context)}
            html_body = loader.render_to_string(html_email_template_name, html_context)
            mail.attach_alternative(html_body, "text/html")

        mail.send()

    def save(self, *args, **kwargs):
        kwargs["html_email_template_name"] = self.html_email_template_name
        kwargs["email_template_name"] = self.email_template_name
        return super().save(*args, **kwargs)


def send_template_email(
    to_email,
    subject,
    plain_tpl,
    html_tpl=None,
    ctx=None,
    execute=False,
):
    ctx = ctx or {}
    plain = ""
    html = None
    # Render plain text with Django loader to avoid Jinja parsing Django tags
    if plain_tpl:
        try:
            plain = loader.render_to_string(plain_tpl, ctx, using="django")
        except Exception:
            plain = ""

    # Prefer Jinja for HTML templates (if available), fall back to Django loader
    if html_tpl:
        try:
            jinja = engines["jinja2"]
            html = jinja.get_template(html_tpl).render(ctx)
        except Exception:
            try:
                html = loader.render_to_string(html_tpl, ctx, using="django")
            except Exception:
                html = None

    if execute:
        msg = EmailMultiAlternatives(
            subject, plain, settings.DEFAULT_FROM_EMAIL, [to_email]
        )
        if html:
            msg.attach_alternative(html, "text/html")
        msg.send()
        return {"sent": True, "subject": subject}

    return {"sent": False, "subject": subject, "reason": ctx.get("reason")}


def send_recovery_codes_email(user, reason="", execute=False):
    ctx = {"user": user, "reason": reason} if reason else {"user": user}
    subject = "The National Archives: Account Recovery Codes reset"
    plain_tpl = (
        "wagtailadmin/account/recovery_codes/recovery_codes_reset_email_plain.txt"
    )
    html_tpl = "wagtailadmin/account/recovery_codes/recovery_codes_reset_email.html"
    return send_template_email(
        user.email, subject, plain_tpl, html_tpl, ctx, execute=execute
    )
