export default function toggle_aria_expanded(sectionContent) {
    $(sectionContent).attr("aria-expanded") === "true"
        ? $(sectionContent).attr("aria-expanded", "false")
        : $(sectionContent).attr("aria-expanded", "true");
}
