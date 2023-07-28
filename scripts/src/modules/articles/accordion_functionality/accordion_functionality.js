import scroll_to_active_heading from "./scroll_to_active_heading";
import slide_toggle from "./slide_toggle";
import toggle_aria_expanded from "./toggle_aria_expanded";

export default function accordion_functionality(
    currentHeading,
    sectionHeadings,
    sectionContents,
    headingPositions,
) {
    const id = currentHeading.id;

    // Find the section that matches the heading that was clicked on.
    sectionContents.each(function (index) {
        // If it matches, expand the section.
        if ($(this).attr("data-controlled-by") === id) {
            const imageBlock = $(this).closest(
                '[data-module="data-imageblock"]',
            )[0];
            const imageBlockButton = $(
                currentHeading.closest('[data-module="data-imageblock"]'),
            )[0];
            if (imageBlock === imageBlockButton && !$(this).is(":animated")) {
                slide_toggle($(this));
                scroll_to_active_heading(headingPositions[index]);
                toggle_aria_expanded($(sectionHeadings[index]));
            }
        }
        // Otherwise, collapse all other sections. This functionality is required because a different section may be expanded
        // and it should collapse when a new section is opened.
        else if ($(this).css("display") === "block") {
            $(this).slideUp();
            $(sectionHeadings[index]).attr("aria-expanded", "false");
        }
    });
}
