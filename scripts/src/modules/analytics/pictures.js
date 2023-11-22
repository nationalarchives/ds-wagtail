import push_to_data_layer from "./push_to_data_layer";

export const trackPictureTranscripts = () => {
    const $imageBlockTranscripts = document.querySelectorAll(
        ".image-block[data-module='data-imageblock'] button.image-block__transcript",
    );
    $imageBlockTranscripts.forEach(($imageBlockTranscript) => {
        $imageBlockTranscript.addEventListener("click", () =>
            push_to_data_layer({
                event: "Expand accordion",
                "data-component-name": "Image transcript",
                "data-link-type":
                    $imageBlockTranscript.getAttribute("aria-expanded") ===
                    "true"
                        ? "Collapse accordion"
                        : "Expand accordion",
                "data-link": $imageBlockTranscript.innerText,
            }),
        );
    });
};

export const trackPictureTranscriptTabs = () => {
    const $imageBlockTranscriptTabs = document.querySelectorAll(
        ".image-block[data-module='data-imageblock'] .transcription__tablist .transcription__tab",
    );
    $imageBlockTranscriptTabs.forEach(($imageBlockTranscriptTab) => {
        $imageBlockTranscriptTab.addEventListener("click", () => {
            if (
                $imageBlockTranscriptTab.getAttribute("aria-selected") ===
                "false"
            ) {
                push_to_data_layer({
                    event: "Expand accordion",
                    "data-component-name": "Image transcript",
                    "data-link-type": "Tab",
                    "data-link": $imageBlockTranscriptTab.innerText,
                });
            }
        });
    });
};
