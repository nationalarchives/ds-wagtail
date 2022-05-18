import convert_px_property_to_number from "./convert_px_property_to_number";

export default function slide_toggle(sectionHeadings, currentHeading, sectionContent) {
    let position;

    if($(sectionContent).css("display") === "none") {
        $(sectionContent).slideDown();
    }
    else {
        $(sectionContent).slideUp();
    }

    if(sectionHeadings[0] === currentHeading) {
        position = $(currentHeading).offset().top;
    }
    else {
        // When using the css() method to get margin and padding properties, a string is returned e.g. 32px. Therefore, the
        // numeric value needs to be extracted for use in the calculations below.
        const sectionHeadingPadding = convert_px_property_to_number($(sectionHeadings[sectionHeadings.index(currentHeading) - 1]).css("padding-top")) + convert_px_property_to_number($(sectionHeadings[sectionHeadings.index(currentHeading) - 1]).css("padding-bottom"));
        const sectionHeadingMargin = convert_px_property_to_number($(sectionHeadings[sectionHeadings.index(currentHeading) - 1]).css("margin-top")) + convert_px_property_to_number($(sectionHeadings[sectionHeadings.index(currentHeading) - 1]).css("margin-bottom"));
        const totalSectionHeadingHeight = $(sectionHeadings[sectionHeadings.index(currentHeading) - 1]).height() + sectionHeadingPadding + sectionHeadingMargin;
        
        // This accounts for the height of the element and also any padding/margin that has been applied.
        position = $(sectionHeadings[sectionHeadings.index(currentHeading) - 1]).offset().top + totalSectionHeadingHeight;
    }

    // Scroll to the expanded section's heading when clicked, keeping it at the top of the viewport.
    $('html, body').animate({
        scrollTop: position
    }, 400);
}
