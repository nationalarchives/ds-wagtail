export default function slide_toggle(sectionHeadingPosition, sectionContent) {
    if($(sectionContent).css("display") === "none") {
        $(sectionContent).slideDown();
    }
    else {
        $(sectionContent).slideUp();
    }

    // Scroll to the expanded section's heading when clicked, keeping it at the top of the viewport.
    $('html, body').animate({
        scrollTop: sectionHeadingPosition - 5
    }, 400);
}
