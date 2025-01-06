/* eslint-disable no-undef */
export default function open_first_section(sectionHeadings, sectionContents) {
    const openSections = $(".section-separator__heading[aria-expanded='true']");
    if (openSections.length === 0) {
        $(sectionContents[0]).show();
        $(sectionHeadings[0]).attr("aria-expanded", "true");
    }
}
