/* global image_source */

import Openseadragon from "openseadragon";

if (image_source) {
    const seadragon_options = {
        id: "js-image-viewer",
        toolbar: "js-viewer-toolbar",
        zoomInButton: "zoom-in",
        zoomOutButton: "zoom-out",
        fullPageButton: "full-page",
        showNavigator: true,
        navigatorPosition: "ABSOLUTE",
        navigatorTop: "40vh",
        navigatorLeft: "79vw",
        navigatorHeight: "20vh",
        navigatorWidth: "20vw",
        homeButton: "home",
        tileSources: {
            type: "image",
            url: image_source,
            buildPyramid: false,
        },
    };

    const viewer = Openseadragon(seadragon_options);
    const canvas = document.getElementsByClassName("openseadragon-canvas")[0];
    const header = document.getElementsByClassName("image-viewer__header")[0];
    const footer = document.getElementsByClassName("image-viewer__footer")[0];

    viewer.addHandler("full-page", (data) => {
        const full_screen_button = document.getElementById("full-page");

        if (full_screen_button) {
            if (data.fullPage) {
                full_screen_button.textContent = "Exit full screen";
                return;
            }
            full_screen_button.textContent = "Full screen";
            full_screen_button.focus();
        }
    });

    try {
        canvas.addEventListener("focus", () => {
            header.style.borderBottom = "solid 0.3125rem #8EC0EC";
            footer.style.borderTop = "solid 0.3125rem #8EC0EC";
        });

        canvas.addEventListener("blur", () => {
            header.style.borderBottom = "none";
            footer.style.borderTop = "none";
        });
    } catch (e) {
        console.error(e);
    }
}
