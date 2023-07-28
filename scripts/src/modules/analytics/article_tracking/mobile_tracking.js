import set_data_link_type from "./set_mobile_data_link_type";
import set_mobile_tracking_attributes from "./set_mobile_tracking_attributes";
import push_to_data_layer from "../push_to_data_layer";

export default function mobile_tracking() {
    const article_body = document.querySelector(".article-container__main");
    const section_headings = document.querySelectorAll(
        ".section-separator__heading",
    );

    set_mobile_tracking_attributes(section_headings);

    article_body.addEventListener("click", (e) => {
        if (e.target.className === "section-separator__heading") {
            set_mobile_tracking_attributes(section_headings);

            push_to_data_layer({
                event: "Mobile nav",
                "data-component-name": e.target.getAttribute(
                    "data-component-name",
                ),
                "data-link-type": set_data_link_type(e),
                "data-link": e.target.getAttribute("data-link"),
                "data-position": e.target.getAttribute("data-position"),
            });
        }
    });

    article_body.addEventListener("keyup", (e) => {
        if (
            e.key === "Enter" &&
            e.target.className === "section-separator__heading"
        ) {
            set_mobile_tracking_attributes(section_headings);

            push_to_data_layer({
                event: "Mobile nav",
                "data-component-name": e.target.getAttribute(
                    "data-component-name",
                ),
                "data-link-type": set_data_link_type(e),
                "data-link": e.target.getAttribute("data-link"),
                "data-position": e.target.getAttribute("data-position"),
            });
        }
    });
}
