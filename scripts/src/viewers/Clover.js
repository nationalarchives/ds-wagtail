import React, { useEffect, useState } from "react";
import Viewer from "@samvera/clover-iiif/viewer";
// import {
//     Homepage,
//     Label,
//     Metadata,
//     PartOf,
//     RequiredStatement,
//     SeeAlso,
//     Summary,
// } from "@samvera/clover-iiif/primitives";
//import Slider from "@samvera/clover-iiif/slider";

import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";

const Clover = () => {
    const [manifest, setManifest] = useState();

    const viewer = document.getElementById("clover-viewer");

    const manifestId = viewer.getAttribute("data-id");

    const options = {
        // Primary title (Manifest label) for top level canvas.  Defaults to true
        //showTitle: false,

        // IIIF Badge and popover containing options.  Defaults to true
        showIIIFBadge: false,

        // Ignore supplementing canvases by label value that are not for captioning
        ignoreCaptionLabels: ["Chapters"],

        // Override canvas background color, defaults to #1a1d1e
        canvasBackgroundColor: "#f4f4f4",

        // Set canvas zooming onScoll (this defaults to false)
        openSeadragon: {
            sequenceMode: true,
            gestureSettingsMouse: {
                scrollToZoom: true,
            },
        },

        // custom options

        informationPanel: {
            open: true,
            renderToggle: true,
        },
    };

    const customTheme = {
        colors: {
            /**
             * Black and dark grays in a light theme.
             * All must contrast to 4.5 or greater with `secondary`.
             */
            primary: "#000",
            primaryMuted: "#546E7A",
            primaryAlt: "#26262a",

            /**
             * Key brand color(s).
             * `accent` must contrast to 4.5 or greater with `secondary`.
             */
            accent: "#1e1e1e",
            accentMuted: "#343338",
            accentAlt: "#747474",

            /**
             * White and light grays in a light theme.
             * All must must contrast to 4.5 or greater with `primary` and  `accent`.
             */
            secondary: "#FFFFFF",
            secondaryMuted: "#d9d9d6",
            secondaryAlt: "#d9d9d6",
        },
        fonts: {
            sans: "'Open Sans', sans-serif",
            display: "'Roboto', sans-serif",
        },
    };

    useEffect(() => {
        (async () => {
            const response = await fetch(manifestId);
            const json = await response.json();
            setManifest(json);
        })();
    }, [manifestId]);

    if (!manifest) return "";

    return (
        <article>
            <Viewer
                iiifContent={manifestId}
                customTheme={customTheme}
                options={options}
            />
            {/* <div>
                <Label label={manifest.label} as="h1" />
                <Summary summary={manifest.summary} as="p" />
                <Metadata metadata={manifest.metadata} />
                <RequiredStatement
                    requiredStatement={manifest.requiredStatement}
                />
                <PartOf partOf={manifest.partOf} />
                <SeeAlso seeAlso={manifest.seeAlso} />
                <Homepage homepage={manifest.homepage} />
            </div> */}
            {/* Needs a specific collection to work correctly */}
            {/* <Slider iiifContent={collectionId} /> */}
        </article>
    );
};

export default Clover;
