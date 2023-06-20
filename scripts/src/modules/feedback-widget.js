class FeedbackWidget {
    static selector() {
        return '[data-feedback-widget]';
    }

    constructor(node) {
        this.widget = node;
        this.feedbackHeading = this.widget.querySelector(
            '[data-feedback-heading]',
        );
        this.yesForm = this.widget.querySelector('[data-yes-form]');
        this.noForm = this.widget.querySelector('[data-no-form]');
        this.feedbackForms = this.widget.querySelector(
            '[data-feedback-buttons]',
        );
        this.extraFeedbackBlocks = this.widget.querySelectorAll(
            '[data-extra-feedback-block]',
        );
        this.feedbackId = null;
        this.feedbackSignature = null;
        this.bindEvents();
    }

    sendFormData(url, data, cb) {
        fetch(url, {
            method: 'POST',
            body: data,
            headers: {
                Accept: 'application/json',
            },
        }).then((response) => {
            if (response.ok) {
                response.json().then((jsonData) => {
                    cb(jsonData);
                });
            } else {
                this.feedbackForms.setAttribute('hidden', '');
                this.extraFeedbackBlocks.forEach((block) => {
                    block.setAttribute('hidden', '');
                });
                this.feedbackHeading.innerText =
                    'Something went wrong submitting your feedback. Please refresh the page and try again.';
                this.feedbackHeading.setAttribute('aria-live', 'polite');
            }
        });
    }

    setFeedbackFormClasses() {
        this.feedbackForms.setAttribute('hidden', '');
    }

    showFeedbackForm(block) {
        this.feedbackHeading.innerText = '';
        this.setFeedbackFormClasses();
        block.removeAttribute('hidden');
    }

    hideFeedbackForm(block) {
        block.setAttribute('hidden', '');
        this.feedbackHeading.innerText = 'Thank you for your feedback';
        this.feedbackHeading.setAttribute('aria-live', 'polite');
    }

    transitionToFeedbackForm(data, form) {
        this.feedbackId = data.feedback_id;
        this.feedbackSignature = data.signature;
        this.showFeedbackForm(
            this.widget.querySelector(`[data-extra-feedback-block="${form}"]`),
        );
        this.widget
            .querySelector(`button[value="${form}"]`)
            .setAttribute('aria-pressed', 'true');
    }

    bindEvents() {
        this.yesForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const formData = new FormData(this.yesForm);
            const form = 'yes';
            formData.set('form_prefix', form);
            this.sendFormData(this.yesForm.action, formData, (data) =>
                this.transitionToFeedbackForm(data, form),
            );
            this.setAttribute('aria-pressed', 'true');
        });

        this.noForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const formData = new FormData(this.noForm);
            const form = 'no';
            formData.set('form_prefix', form);
            this.sendFormData(this.noForm.action, formData, (data) =>
                this.transitionToFeedbackForm(data, form),
            );
            this.setAttribute('aria-pressed', 'true');
        });

        this.extraFeedbackBlocks.forEach((block) => {
            const form = block.querySelector('form');
            form.addEventListener('submit', (event) => {
                event.preventDefault();
                const formData = new FormData(form);
                formData.set('id', this.feedbackId);
                formData.set('signature', this.feedbackSignature);
                this.sendFormData(form.action, formData, () =>
                    this.hideFeedbackForm(block),
                );
            });
        });
        this.extraFeedbackBlocks.forEach((block) => {
            const closeButton = block.querySelector('[data-close-form]');
            closeButton.addEventListener('click', () => {
                this.hideFeedbackForm(block);
            });
        });
    }
}

export default FeedbackWidget;