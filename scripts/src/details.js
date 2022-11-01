import scroll_to_bottom from "./modules/scroll_to_bottom";
import push_reference_and_series from "./modules/analytics/push_reference_and_series";
import add_unique_ids from "./modules/analytics/add_unique_ids";
import toggle_detailed_view from "./modules/records/toggle_detailed_view";

document.addEventListener("DOMContentLoaded", () => {

    const hierarchy_list = document.querySelector('.hierarchy-global__list');
    const hierarchy_list_current_item = document.querySelector(".hierarchy-global__list-item--current-item");

    scroll_to_bottom(hierarchy_list_current_item, hierarchy_list);
    push_reference_and_series();
    add_unique_ids();
    toggle_detailed_view();

});
