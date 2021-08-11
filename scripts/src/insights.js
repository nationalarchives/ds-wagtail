import add_analytics_data_card_position from './modules/analytics/card_position'
import audio_tracking from "./modules/analytics/audio_tracking"
import video_tracking from "./modules/analytics/video_tracking"

add_analytics_data_card_position('.record-embed-no-image');
add_analytics_data_card_position('.card-group-secondary-nav');

document.addEventListener('DOMContentLoaded', () => {
    audio_tracking();
    video_tracking();
});
