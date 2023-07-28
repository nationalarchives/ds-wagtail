import push_to_data_layer from "./push_to_data_layer";

const push_reference_and_series = () => {
    const hierarchy_items = document.getElementsByClassName(
            "hierarchy-global__list-item",
        ),
        record_reference = document.getElementById(
            "analytics-record-reference",
        );

    try {
        if (hierarchy_items && hierarchy_items.length < 3) {
            push_to_data_layer({
                event: "reference",
                reference: `${record_reference.innerText}`,
                series: "Above series level",
            });
        }

        if (hierarchy_items && hierarchy_items.length >= 3) {
            const series_title =
                    hierarchy_items[2].querySelector("[data-link]").innerText,
                series_reference = hierarchy_items[2].querySelector(
                    ".hierarchy-global__reference",
                ).innerText;

            push_to_data_layer({
                event: "reference",
                reference: `${record_reference.innerText}`,
                series: `${series_reference} - ${series_title}`,
            });
        }
    } catch (e) {
        console.error(`Error push_series_from_hierarchy module: ${e}`);
    }
};

export default push_reference_and_series;
