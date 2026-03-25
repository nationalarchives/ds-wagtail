import importlib
import logging

from django.core.mail import EmailMultiAlternatives
from django.template import engines, loader
from wagtail.admin.forms.auth import PasswordResetForm

logger = logging.getLogger(__name__)


def _parse_inline_style(style_text):
    styles = {}
    for declaration in style_text.split(";"):
        if ":" not in declaration:
            continue
        property_name, value = declaration.split(":", 1)
        property_name = property_name.strip().lower()
        value = value.strip()
        if property_name and value:
            styles[property_name] = value
    return styles


def _merge_inline_style(existing_style, fallback_style):
    merged_styles = _parse_inline_style(existing_style)
    for property_name, value in _parse_inline_style(fallback_style).items():
        merged_styles.setdefault(property_name, value)
    return "; ".join(
        f"{property_name}: {value}" for property_name, value in merged_styles.items()
    )


def _append_style_by_xpath(document, xpath, fallback_style):
    for element in document.xpath(xpath):
        existing_style = element.get("style", "")
        element.set("style", _merge_inline_style(existing_style, fallback_style))


def _apply_email_fallback_styles(html_body):
    """
    Add conservative inline fallback styles for email clients that ignore
    modern CSS features such as custom properties and advanced selectors.
    """
    try:
        lxml_html = importlib.import_module("lxml.html")
        document = lxml_html.fromstring(html_body)

        _append_style_by_xpath(
            document,
            "//body",
            "margin: 0; padding: 0; background-color: #f4f4f4; color: #343338; "
            "font-family: Arial, sans-serif; font-size: 19px; line-height: 1.6",
        )
        _append_style_by_xpath(
            document,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' tna-template__main ')]",
            "width: 600px; max-width: 100%; margin: 32px auto; background-color: #ffffff; "
            "border: 1px solid #d9d9d6",
        )
        _append_style_by_xpath(
            document,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' tna-email-header ')]",
            "background-color: #1e1e1e; color: #ffffff; padding: 16px 24px",
        )
        _append_style_by_xpath(
            document,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' tna-template__content ')]",
            "padding: 24px; color: #343338; font-family: Arial, sans-serif; "
            "font-size: 19px; line-height: 1.6",
        )
        _append_style_by_xpath(
            document,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' tna-panel ')]",
            "background-color: #00623b; color: #ffffff; text-align: center; padding: 24px",
        )
        _append_style_by_xpath(
            document,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' tna-panel__heading ')]",
            "margin: 0; color: #ffffff; font-size: 32px; line-height: 1.2",
        )
        _append_style_by_xpath(
            document,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' tna-panel__content ')]",
            "margin-top: 12px; color: #ffffff; font-size: 18px",
        )
        _append_style_by_xpath(
            document,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' tna-button-group ')]",
            "margin-top: 24px; text-align: left",
        )
        _append_style_by_xpath(
            document,
            "//a[contains(concat(' ', normalize-space(@class), ' '), ' tna-button ')]",
            "display: inline-block; background-color: #111111; color: #ffffff; "
            "text-decoration: none; padding: 10px 16px; border: 2px solid #111111; "
            "font-weight: 700; font-size: 18px; line-height: 1.4",
        )
        _append_style_by_xpath(
            document,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' tna-template__content ')]//p",
            "margin: 16px 0",
        )
        _append_style_by_xpath(
            document,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' tna-email-footer ')]",
            "background-color: #1e1e1e; color: #ffffff; padding: 24px; font-size: 16px",
        )
        _append_style_by_xpath(
            document,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' tna-email-footer ')]//a",
            "color: #ffffff",
        )

        return lxml_html.tostring(document, encoding="unicode", method="html")
    except Exception:
        logger.exception(
            "Failed to apply fallback inline email styles; using premailer output"
        )
        return html_body


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
                html_body = _apply_email_fallback_styles(html_body)
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
