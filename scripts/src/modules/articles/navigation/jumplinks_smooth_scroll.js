/* eslint-disable no-undef */
export default function jumplinks_smooth_scroll(currentJumplink) {
    if (!$("html, body").is(":animated")) {
        let target = $(currentJumplink).attr("href");

        // The id that the href references contains a period and so it needs to be escaped for the selector to work correctly.
        target = target.replace(".", "\\.");
        $("html, body").animate(
            {
                scrollTop: $(target).offset().top,
            },
            1000,
        );
    }
}
