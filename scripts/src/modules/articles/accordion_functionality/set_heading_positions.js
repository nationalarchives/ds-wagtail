/* eslint-disable no-undef */
// This function calculates the position of each heading. In order to prevent expanded sections from causing the heading
// position being calculated too far down the page, the top position of the first heading is taken as the first index.
// The height of subsequent headings is calculated by adding its height to the previous index.
export default function set_heading_positions(sectionHeadings) {
    const positions = [];

    sectionHeadings.each(function (index) {
        if ($(this).attr("id") === $(sectionHeadings[0]).attr("id")) {
            positions.push($(this).offset().top);
        } else {
            const prevHeading = sectionHeadings[index - 1];

            // This accounts for any padding, margin, and borders that have been applied to the heading in order to correctly
            // calculate its height.
            const position =
                positions[index - 1] + $(prevHeading).outerHeight(true);
            positions.push(position);
        }
    });

    return positions;
}
