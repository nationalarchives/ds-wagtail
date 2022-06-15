export default function toggle_data_link_type(e, section_headings) {
    if(e.target.getAttribute("aria-expanded") === "false") {
        e.target.setAttribute("data_link_type", `Collapse header no. ${Array.prototype.indexOf.call(section_headings, e.target) + 1}`);
    }
    else {
        e.target.setAttribute("data_link_type", `Expand header no. ${Array.prototype.indexOf.call(section_headings, e.target) + 1}`);
    }

    return e.target.getAttribute("data_link_type");
}
