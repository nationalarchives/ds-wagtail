import add_analytics_data_card_position from "./modules/analytics/card_position";

document.addEventListener("DOMContentLoaded", () => {
    add_analytics_data_card_position(".card-group-secondary-nav > a");
    add_analytics_data_card_position(".card-group-secondary-nav__body > a");
    add_analytics_data_card_position(".card-group-secondary-nav__heading > a");
});
