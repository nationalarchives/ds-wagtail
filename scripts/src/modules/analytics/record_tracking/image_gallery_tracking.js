import push_to_data_layer from "../push_to_data_layer";

export default function imageGalleryTracking() {
    const imageGallery = document.querySelector("[data-image-gallery]");
    const imageGalleryOpen = imageGallery.querySelector("[data-image-gallery-open]");
    const imageGalleryClose = imageGallery.querySelector("[data-image-gallery-close]");
    let imageGalleryTranscriptionTab = imageGallery.querySelectorAll("[data-transcription-tab]");
    let imageGalleryTranslationTab = imageGallery.querySelectorAll("[data-translation-tab]");

    // 'open gallery' button tracking - on click
    imageGalleryOpen.addEventListener("click", e => {
        push_to_data_layer({
            "event": "Image gallery",
            "data-component-name": e.target.getAttribute("data-component-name"),
            "data-link-type": e.target.getAttribute("data-link-type"),
            "data-link": e.target.getAttribute("data-link")
        })
    })

    // 'open gallery' button tracking - on keypress
    imageGalleryOpen.addEventListener("keyup", e => {
        if(e.key === "Enter") {
            push_to_data_layer({
                "event": "Image gallery",
                "data-component-name": e.target.getAttribute("data-component-name"),
                "data-link-type": e.target.getAttribute("data-link-type"),
                "data-link": e.target.getAttribute("data-link")
            })
        }
    })

    // 'close gallery' button tracking - on click
    imageGalleryClose.addEventListener("click", e => {
        push_to_data_layer({
            "event": "Image gallery",
            "data-component-name": e.target.getAttribute("data-component-name"),
            "data-link-type": e.target.getAttribute("data-link-type"),
            "data-link": e.target.getAttribute("data-link")
        })
    })

    // 'close gallery' button tracking - on keypress
    imageGalleryClose.addEventListener("keyup", e => {
        if(e.key === "Enter") {
            push_to_data_layer({
                "event": "Image gallery",
                "data-component-name": e.target.getAttribute("data-component-name"),
                "data-link-type": e.target.getAttribute("data-link-type"),
                "data-link": e.target.getAttribute("data-link")
            })
        }
    })
    
    imageGalleryTranscriptionTab.forEach((tab) => {
        // 'transcription' tab tracking - on click
        tab.addEventListener("click", e => {
            push_to_data_layer({
                "event": "Transcript",
                "data-component-name": e.target.getAttribute("data-component-name"),
                "data-link-type": e.target.getAttribute("data-link-type"),
                "data-link": e.target.getAttribute("data-link")
            })
        });

        // 'transcription' tab tracking - on keypress
        tab.addEventListener("keyup", e => {
            if(e.key === "Enter") {
                push_to_data_layer({
                    "event": "Transcript",
                    "data-component-name": e.target.getAttribute("data-component-name"),
                    "data-link-type": e.target.getAttribute("data-link-type"),
                    "data-link": e.target.getAttribute("data-link")
                })
            }
        })
    });

    imageGalleryTranslationTab.forEach((tab) => {
        // 'translation' tab tracking - on click
        tab.addEventListener("click", e => {
            push_to_data_layer({
                "event": "Transcript",
                "data-component-name": e.target.getAttribute("data-component-name"),
                "data-link-type": e.target.getAttribute("data-link-type"),
                "data-link": e.target.getAttribute("data-link")
            })
        });

        // 'translation' tab tracking - on keypress
        tab.addEventListener("keyup", e => {
            if(e.key === "Enter") {
                push_to_data_layer({
                    "event": "Transcript",
                    "data-component-name": e.target.getAttribute("data-component-name"),
                    "data-link-type": e.target.getAttribute("data-link-type"),
                    "data-link": e.target.getAttribute("data-link")
                })
            }
        })
    });
}
