export default function remove_mobile_tracking() {
    const insights_body = document.querySelector(".insights-container__main");
    const section_headings = document.querySelectorAll(".section-separator__heading");

    Array.prototype.forEach.call(section_headings, item => {
        item.removeAttribute("data-component-name");
        item.removeAttribute("data-link-type");
        item.removeAttribute("data-position");
        item.removeAttribute("data-link");
    });

    insights_body.removeEventListener("click", e => {
        mobile_section_tracking(e);
    })
}
