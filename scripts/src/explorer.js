import add_analytics_data_card_position from './modules/analytics/card_position'
import add_unique_ids from "./modules/analytics/add_unique_ids";

add_analytics_data_card_position('.card-group-promo--green');
add_analytics_data_card_position('.card-group-secondary-nav__link');
add_analytics_data_card_position('.card-group-record-summary');
add_analytics_data_card_position('.card-group--list-style-none');
add_analytics_data_card_position('.card-group--no-flex');
add_analytics_data_card_position('.card-group-promo__card');
add_analytics_data_card_position('.card-group-promo__card-heading a');

document.addEventListener("DOMContentLoaded", () => {
   add_unique_ids();
});
