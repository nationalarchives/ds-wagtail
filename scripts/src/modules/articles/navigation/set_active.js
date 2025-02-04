/* eslint-disable no-undef */
export default function set_active(sections) {
    sections.each(function () {
        if (!$("html, body").is(":animated")) {
            if ($(window).scrollTop() > $(this).offset().top - 1) {
                let id = $(this).attr("id");

                // The id contains a period and so it needs to be escaped for the selector to work correctly.
                id = id.replace(".", "\\.");
                $(".jumplinks__list-item").removeClass("active");
                $(`.jumplinks__list-item a[href="#${id}"]`)
                    .parent()
                    .addClass("active");
            }
        }
    });
}
