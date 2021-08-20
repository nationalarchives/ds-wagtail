import add_analytics_data_card_position from './modules/analytics/card_position'
import audio_tracking from "./modules/analytics/audio_tracking"
import video_tracking from "./modules/analytics/video_tracking"
import add_unique_ids from "./modules/analytics/add_unique_ids";

document.addEventListener('DOMContentLoaded', () => {
    add_analytics_data_card_position('.record-embed-no-image');
    add_analytics_data_card_position('.card-group-secondary-nav');

    audio_tracking();
    video_tracking();
    add_unique_ids();
});
