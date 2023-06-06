export default function scroll_to_active_heading(heading) {
    $("html, body").animate(
        {
            scrollTop: heading,
        },
        400
    );
}
