import set_data_link_type from "./set_mobile_data_link_type";
import set_mobile_tracking_attributes from "./set_mobile_tracking_attributes";
import push_to_data_layer from "../push_to_data_layer";

export default function mobile_tracking() {
    const insights_body = document.querySelector(".insights-container__main");
    const section_headings = document.querySelectorAll(".section-separator__heading");

    set_mobile_tracking_attributes(section_headings);

    insights_body.addEventListener("click", e => {
        if(e.target.className === "section-separator__heading"){ 
            set_mobile_tracking_attributes(section_headings);

            push_to_data_layer({
                "event": "Mobile nav",
                "data_component_name": e.target.getAttribute("data_component_name"),
                "data_link_type": set_data_link_type(e, section_headings),
                "data_link": e.target.getAttribute("data_link")
            })
        }
    })

    insights_body.addEventListener("keyup", e => {
        if(e.key === "Enter" && e.target.className === "section-separator__heading") {
            set_mobile_tracking_attributes(section_headings);

            push_to_data_layer({
                "event": "Mobile nav",
                "data_component_name": e.target.getAttribute("data_component_name"),
                "data_link_type": set_data_link_type(e, section_headings),
                "data_link": e.target.getAttribute("data_link")
            })
        }
    })
}
