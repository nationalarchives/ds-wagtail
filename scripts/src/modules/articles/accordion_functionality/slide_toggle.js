/* eslint-disable no-undef */
export default function slide_toggle(sectionContent) {
    if ($(sectionContent).css("display") === "none") {
        $(sectionContent).slideDown();
    } else {
        $(sectionContent).slideUp();
    }
}
