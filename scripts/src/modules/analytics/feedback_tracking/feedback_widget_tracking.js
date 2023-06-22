import push_to_data_layer from "../push_to_data_layer";

const pushFeedbackForm = () => {
    // get filters after DOM has loaded and they have rendered on page
    window.addEventListener('load', () => {
        const feedbackForm = document.querySelector('[data-feedback-form]');

        if (feedbackForm !== null) {
            pushFeedbackData(feedbackForm);
        }
    });
}

const pushFeedbackData = () => {
    // get feedback form
    const feedbackForm = document.querySelector('[data-feedback-form]');
    const feedbackFormHeading = feedbackForm.querySelector('legend');
    const feedbackFormComment = document.querySelector('[data-feedback-form-comment]');
    const feedbackResponseButtons = feedbackForm.querySelectorAll('[data-feedback-response-button]');

    let feedbackFormCommentTextarea = feedbackFormComment.querySelector('#id_comment');
    let heading = feedbackFormHeading.innerText;

    feedbackResponseButtons.forEach((response) => {
        response.addEventListener('click', () => {
            let sentiment = response.getAttribute('data-option-sentiment');

            switch (sentiment) {
                case '-2':
                    sentiment = "Very Negative";
                    break;
                case '-1':
                    sentiment = "Negative";
                    break;
                case '0':
                    sentiment = "Neutral";
                    break;
                case '1':
                    sentiment = "Positive";
                    break;
                case '2':
                    sentiment = "Very positive";
                    break;
            }

            feedbackFormComment.setAttribute('data-sentiment', sentiment);
        });
    });

        

    feedbackFormComment.addEventListener('submit', (e) => {
        e.preventDefault();

        let value = feedbackFormComment.getAttribute('data-sentiment');

        if (feedbackFormCommentTextarea.value !== '') {
            let formData = {
                'event': 'feedback-form',
                'data-text-field': 'Comment',
                'data-link-type': 'Form',
                'data-component-name': heading,
                'data-option-value': value || '',
            };

            console.log(formData);
            // push_to_data_layer(formData);
        } else {
            let formData = {
                'event': 'feedback-form',
                'data-text-field': 'No comment',
                'data-link-type': 'Form',
                'data-component-name': heading,
                'data-option-value': value || '',
            };

            console.log(formData);
            // push_to_data_layer(formData);
        }
    });
}

export default pushFeedbackForm;