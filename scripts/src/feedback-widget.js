import FeedbackWidget from './modules/feedback-widget';

const feedbackWidget = document.querySelector('[data-feedback-widget]')

if (feedbackWidget) {
    new FeedbackWidget(feedbackWidget);
    // feedbackWidgetTracking();
}