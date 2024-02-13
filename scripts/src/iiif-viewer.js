// sticking to universalviewer 4.0.22 for now because of
// https://github.com/UniversalViewer/universalviewer/issues/957
import { init as uvInit } from 'universalviewer';
import 'universalviewer/dist/uv.css';


document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-js-iiif-viewer-manifest-url]").forEach((element) => {
        const { jsIiifViewerManifestUrl: manifestUrl } = element.dataset;
        if (!manifestUrl) {
            throw new Error("No manifest URL provided in data-js-iiif-viewer-manifest-url attribute.")
        }
        const data = {
            manifest: manifestUrl,
            embedded: true,
        };
        const uv = uvInit(element, data);

        // override config using an inline json object
        uv.on("configure", function ({ cb }) {
            cb({
                options: {
                    useArrowKeysToNavigate: true,
                    navigatorEnabled: true,
                    footerPanelEnabled: true,
                    headerPanelEnabled: true,
                    leftPanelEnabled: true
                },
                modules: {
                    pagingHeaderPanel: {
                        options: {
                            autoCompleteBoxEnabled: true,
                            autocompleteAllowWords: true,
                            galleryButtonEnabled: true,
                            imageSelectionBoxEnabled: true,
                            pageModeEnabled: true,
                            pagingToggleEnabled: true
                        },
                    },
                },
            });
        });
    });
});