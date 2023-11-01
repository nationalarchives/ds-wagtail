import push_to_data_layer from "./push_to_data_layer";

const trackHeroCaptions = () => {
    const $heroCaptions = document.querySelectorAll(".tna-hero__details");
    $heroCaptions.forEach(($heroCaption) => {
        $heroCaption.addEventListener("toggle", () =>
            push_to_data_layer({
                event: "Expand accordion",
                "data-component-name": "Hero banner image",
                "data-link-type": "Tooltip",
                "data-link": $heroCaption.hasAttribute("open")
                    ? "Expand caption"
                    : "Collapse caption",
            }),
        );
    });
};

export default trackHeroCaptions;
