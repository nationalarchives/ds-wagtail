import add_data_link from "./modules/analytics/add_data_link";
import push_to_data_layer from "./modules/analytics/push_to_data_layer";
import calc_scroll_percent_increment from "./modules/analytics/scroll_tracking/calc_scroll_percent_increment";
import update_scroll_obj from "./modules/analytics/scroll_tracking/update_scroll_obj";
import get_scroll_percentage from "./modules/analytics/scroll_tracking/get_scroll_percentage";

document.addEventListener("DOMContentLoaded", () => {
    add_data_link(".image-browse__listing a");

    let scrollObj = {
        event: "image-viewer-browse",
        highestScrollPercentage: get_scroll_percentage(),
    };

    document.addEventListener("scroll", () => {
        const percentageIncrement = calc_scroll_percent_increment();
        scrollObj = update_scroll_obj(percentageIncrement, scrollObj);
    });

    window.addEventListener("beforeunload", () => {
        push_to_data_layer(scrollObj);
    });
});
