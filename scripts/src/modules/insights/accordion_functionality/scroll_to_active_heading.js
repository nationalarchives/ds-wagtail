import convert_px_property_to_number from "./convert_px_property_to_number";

export default function scroll_to_active_heading(sectionHeadings, currentHeading) {
    let position;

    if(sectionHeadings[0] === currentHeading) {
        position = $(currentHeading).offset().top;
    }
    else {
        // The previous heading is used to determine the scrollTop position.
        const prevHeading = sectionHeadings[sectionHeadings.index(currentHeading) - 1];

        // When using the css() method to get margin and padding properties, a string is returned e.g. 32px. Therefore, the
        // numeric value needs to be extracted for use in the calculations below.
        const sectionHeadingPadding = convert_px_property_to_number($(prevHeading).css("padding-top")) + convert_px_property_to_number($(prevHeading).css("padding-bottom"));
        const sectionHeadingMargin = convert_px_property_to_number($(prevHeading).css("margin-top")) + convert_px_property_to_number($(prevHeading).css("margin-bottom"));
        const totalSectionHeadingHeight = $(prevHeading).height() + sectionHeadingPadding + sectionHeadingMargin;
        
        // This accounts for the height of the element and also any padding/margin that has been applied.
        position = $(prevHeading).offset().top + totalSectionHeadingHeight;
    }

    // Scroll to the expanded section's heading when clicked, keeping it at the top of the viewport.
    $('html, body').animate({
        scrollTop: position
    }, 400);
}