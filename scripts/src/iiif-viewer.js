// The UV reference is loaded by another script.
// Importing the NPM version directly does not seem to work.

document.addEventListener("DOMContentLoaded", () => {
    document
        .querySelectorAll("[data-js-iiif-viewer-manifest-url]")
        .forEach((element) => {
            const { jsIiifViewerManifestUrl: manifestUrl } = element.dataset;
            if (!manifestUrl) {
                throw new Error(
                    "No manifest URL provided in data-js-iiif-viewer-manifest-url attribute.",
                );
            }
            const data = {
                iiifManifestId: manifestUrl,
            };

            const uv = window.UV.init(element, data);

            // override config using an inline json object
            uv.on("configure", function ({ cb }) {
                cb({
                    options: {
                        useArrowKeysToNavigate: true,
                        navigatorEnabled: true,
                        footerPanelEnabled: true,
                        headerPanelEnabled: true,
                        leftPanelEnabled: true,
                        clickToZoomEnabled: false,
                    },
                    modules: {
                        pagingHeaderPanel: {
                            options: {
                                autoCompleteBoxEnabled: true,
                                autocompleteAllowWords: true,
                                galleryButtonEnabled: true,
                                imageSelectionBoxEnabled: true,
                                pageModeEnabled: true,
                                pagingToggleEnabled: true,
                            },
                        },
                        footerPanel: {
                            options: {
                                downloadEnabled: false,
                                embedEnabled: false,
                                feedbackEnabled: false,
                                fullscreenEnabled: true,
                                minimiseButtons: false,
                                moreInfoEnabled: false,
                                openEnabled: false,
                                printEnabled: false,
                                shareEnabled: false,
                            },
                        },
                    },
                });
            });
        });
});
