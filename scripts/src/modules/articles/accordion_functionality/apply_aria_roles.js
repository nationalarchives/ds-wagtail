/* eslint-disable no-undef */
export default function apply_aria_roles(sectionHeadings, sectionContents) {
    sectionHeadings.each(function (index) {
        // Set aria attributes and roles.
        $(this).attr("role", "button");
        $(this).attr("tabindex", "0");
        $(this).attr("aria-controls", sectionContents[index].id);
        $(sectionContents[index]).attr("aria-labelledby", this.id);

        // Initialise aria-expanded.
        if ($(sectionContents[index]).css("display") === "block") {
            $(this).attr("aria-expanded", "true");
        } else {
            $(this).attr("aria-expanded", "false");
        }
    });
}
