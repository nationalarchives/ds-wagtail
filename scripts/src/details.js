import push_reference_and_series from "./modules/analytics/push_reference_and_series";
import add_unique_ids from "./modules/analytics/add_unique_ids";
import toggle_detailed_view from "./modules/records/toggle_detailed_view";
import toggle_order_options from "./modules/records/toggle_order_options";

document.addEventListener("DOMContentLoaded", () => {

    push_reference_and_series();
    add_unique_ids();
    toggle_detailed_view();
});
