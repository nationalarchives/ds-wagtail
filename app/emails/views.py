from types import SimpleNamespace

from django.conf import settings
from django.http import HttpResponse
from django.template import engines
from django.urls import reverse


def email(request):
    page = SimpleNamespace(
        get_admin_display_title=lambda: "Demo approved page",
        full_url=f"{request.scheme}://{request.get_host()}/demo/approved-page/",
        id=666,
    )
    revision = SimpleNamespace(content_object=page)
    task = SimpleNamespace(name="TaskName", id=999)
    editor = SimpleNamespace(
        get_full_name=lambda: "FullName",
        get_username=lambda: "GotUsername",
    )
    requested_by = SimpleNamespace(
        get_full_name=lambda: "Requester Name",
        get_username=lambda: "requester_username",
    )
    task_state = SimpleNamespace(
        finished_by=SimpleNamespace(
            get_full_name=lambda: "Rejector Name",
            get_username=lambda: "rejector_username",
        )
    )

    uid = "Mg"
    token = "set-password-preview-token"
    reset_path = reverse(
        "wagtailadmin_password_reset_confirm",
        kwargs={"uidb64": uid, "token": token},
    )
    base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", None) or (
        f"{request.scheme}://{request.get_host()}"
    )
    context = {
        "uid": uid,
        "token": token,
        "reset_url": base_url.rstrip("/") + reset_path,
        "protocol": request.scheme,
        "domain": request.get_host(),
        "revision": revision,
        "page": page,
        "task": task,
        "editor": editor,
        "requested_by": requested_by,
        "task_state": task_state,
        "workflow": SimpleNamespace(name="Example Workflow"),
        "comment": "This page needs more work.",
        "new_comments": [
            SimpleNamespace(text="New: This section needs clarity"),
            SimpleNamespace(text="New: Please add more details"),
        ],
        "resolved_comments": [
            SimpleNamespace(text="Resolved: Added clarification"),
        ],
        "deleted_comments": [
            SimpleNamespace(text="Removed outdated section"),
        ],
        "replied_comments": [
            SimpleNamespace(
                comment=SimpleNamespace(text="Initial feedback comment"),
                replies=[
                    SimpleNamespace(text="Reply to feedback"),
                    SimpleNamespace(text="Another reply"),
                ],
            )
        ],
        "user": SimpleNamespace(
            USERNAME_FIELD="username",
            get_username=lambda: "MyUsername",
        ),
    }

    template = engines["jinja2"].get_template(
        # "wagtailadmin/account/password_reset/password_reset_email.html"
        # "wagtailadmin/account/password_reset/email_unsafe_jinja.html"
        "wagtailadmin/notifications/approved.html"
        # "wagtailadmin/notifications/rejected.html"
        # "wagtailadmin/notifications/task_state_approved.html"
        # "wagtailadmin/notifications/task_state_rejected.html"
        # "wagtailadmin/notifications/task_state_submitted.html"
        # "wagtailadmin/notifications/updated_comments.html"
        # "wagtailadmin/notifications/workflow_state_approved.html"
        # "wagtailadmin/notifications/workflow_state_rejected.html"
        # "wagtailadmin/notifications/workflow_state_submitted.html"
    )
    return HttpResponse(template.render(context, request=request))
