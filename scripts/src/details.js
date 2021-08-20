import manage_details_element from './modules/manage_details_element';
import scroll_to_bottom from "./modules/scroll_to_bottom";
import push_reference_and_series from "./modules/analytics/push_reference_and_series";
import add_unique_ids from "./modules/analytics/add_unique_ids";

document.addEventListener("DOMContentLoaded", () => {

    const hierarchy_list = document.querySelector('.hierarchy-global__list');

    manage_details_element();
    scroll_to_bottom(hierarchy_list);
    push_reference_and_series();
    add_unique_ids();

    const summary_element = document.querySelector('#js-hierarchy-global summary');

    summary_element.addEventListener('click', e => {

        if (window.innerWidth < 1200) {
            return;
        }
        e.preventDefault();
    });

});

window.addEventListener("resize", () => {
    manage_details_element();
});
