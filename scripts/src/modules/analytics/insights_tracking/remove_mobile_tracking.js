export default function remove_mobile_tracking() {
    const insights_body = document.querySelector(".insights-container__main");
    const section_headings = document.querySelectorAll(".section-separator__heading");

    Array.prototype.forEach.call(section_headings, item => {
        item.removeAttribute("data_component_name");
        item.removeAttribute("data_link_type");
        item.removeAttribute("data_link");
    });

    insights_body.removeEventListener("click", e => {
        mobile_section_tracking(e);
    })
}
