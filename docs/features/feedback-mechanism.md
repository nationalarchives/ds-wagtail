# Feedback mechanism

All of the code for the feedback mechanism can be found in the `etna.feedback` app in the project.

## How feedback prompts are defined

Feedback prompts are defined in Wagtail via the `FeedbackPrompt` model. The model has three main sets of fields:

- Basic text fields for customising the intro and thank you text.
- A custom `StreamField` block for defining the available 'response options'.
- Fields for controlling which paths/urls the prompt should appear on.

## How feedback prompts are displayed

Feedback prompts are found and displayed on pages using the `etna.feedback.templatetags.feeback_tags.render_feedback_prompt` template tag. The purpose of the tag is to:

1. Using the path of the page, find the relevant `FeedbackPrompt` instance for the current `request`.
2. Use the prompt to generate a Django form (of type `etna.feedback.forms.FeedbackForm`) with the correct labels/options in place, and some initial field values set.
3. Render the form to a template, so that users can interact with it.

The HTML for separate 'comment' form is also included in the template, but requires updating (via JS) before it can be used.

## How feedback responses are collected

When a user submits a feedback form, the submission is posted to `FeedbackSubmitView`. The purpose of the view is to:

1. Using data from the submit URL (`prompt_id` and `prompt_revision`), find the relevant `FeedbackPrompt` instance for the request, and ensure we are using the same revision that was used to generate the form that the user submitted.
2. Use the prompt to generate a Django form (exactly like the `render_feedback_prompt` tag does).
3. Use the form to validate the submission.

Then, if the submission was **valid**:

4. Save a `FeedbackSubmission` instance to the database to represent it.
5. Redirect to the `FeedbackSuccessView` or, if the request was submitted via AJAX, render a `JSONResponse` with some useful values in the response.

Or, if the submission was **invalid** for some reason:

Render a `JSONResponse` with a 400 (Bad Request) status code, including the validation error details from the form.

### What validation takes place?

For a thorough understanding of the validation that is applied to submissions, you should review the `FeedbackForm` code. A few of the key things that are checked are:

1. That the URL value is from the same domain as the view processing the submission (or another domain that has been explicitly configured).
2. That the URL/domain can be mapped to a Wagtail `Site` object
3. That the `response` field value matches the `id` of one of the options defined on the `FeedbackPrompt`
4. That the `page_id` and `page_revision` values match up to an existing revision for an existing page.

## How comments are collected (JS-enabled)

After submitting their initial feedback response, most users (those with Javascript enabled) will be presented with a second form to allow them to post a comment.

The comment form that appears in prompts is hidden from all users initially, then modified and shown depending on the `JsonResponse` received from  `FeedbackSubmitView`. The response data is used in the following ways:

    `comment_prompt_text`:
        Used to populate the `label` text for the `comment` field. If the value is blank or missing, it is assumed that comments are not desired for the selected response option, and only the success message is displayed.
    `id`:
        Used to populate a hidden `submission` input value.
    `signature`:
        Used to populate a hidden `signature` input value.

## How comments are collected (no-JS)

After submitting their initial feedback response, no-JS users will be taken to a thank you page, where a second form allows them to add a supporting comment to their feedback.

Unlike the comment form included in prompt output across the site, this version comes prepopulated with valid `submission` and `signature` values, allowing it to be posted without any further tinkering. While convenient for the user, it should this approach leaves these forms a little more open to abuse (by spammers), and so we are more dependant on infrastructure-level security measures here.

If the user chooses to submit the form, they are redirected to a new success page.

## Comment validation and procesing

Comment form data is posted to a view that validates the following things:

1. That `submission` and `signature` values are present.
2. That `submission` matches the ID of a `FeedbackSubmission` instance that doesn't yet have a comment stored for it.
3. That `signature` matches the supplied `submission` value.

'signatures' are deterministic hashes, created from the `public_id` value of a `FeedbackSubmission` instance, and the `SECRET_KEY` value set for the environment (which will always be kept private).

Because the value is deterministic, the `FeedbackCommentForm` can regenerate the hash from the submitted `submission` value, then compare that to the value that was submitted. If the values match, the comment is considered 'safe' and added to the `FeedbackSumission` instance.

### Versioning of prompts

Because feedback prompts are converted to forms and shown on most pages, having a single version of that `FeedbackPrompt` instance is tricky, because it's quite possible for changes to be saved to the database between the time the form is rendered and when it is proccessed.

This is why the `FeedbackPrompt` model is revisible (has drafts and revisions in Wagtail). With the `prompt_id` and `prompt_revision` both included in submission URLs, we can recreate the `FeedbackPrompt` exactly as it was when the form was rendered to the user, and from that, can recreate a `FeedbackForm` instance that can be used for validation.

### Do we store any personal data?

If the user is signed in, we store the ID of the current Django user with the submission, which can be used to put a name to it. However, most feedback is submitted by unauthenticated users; In which case, only details about the submission itself are stored (the url they were on, the answers they gave, and when it was received). We do not save IP addresses or any other identifiable information.

## Accessing and exporting submission data

Any saved submissions are made available within the Wagtail admin via a custom report view (specifically `etna.feedback.views.FeedbackSubmissionReportView`), which can only be accessed by superusers.

The fields that appear in the Wagtail UI here are controlled by the `list_display` attribute on the view class.

The filters that appear in the Wagtail UI here are defined by the `FeedbackSubmissionFilterSet` class in the same module.

Report views include a 'Download XLSX' / 'Download CSV' option in the top of the UI to allow admins to export data for further analysis. This report is no exception, and the columns that appear in the generated file are controlled by the `list_export` attribute on the view class.
