import Mirador from "./mirador.min.js";

const viewer = document.getElementById("mirador-viewer");
const manifestId = viewer.getAttribute("data-id");

const miradorInstance = Mirador.viewer({
    // see https://github.com/ProjectMirador/mirador/blob/5cb692ed31480c1e130f4a8715726688cb35796d/src/config/settings.js#L264 for config options
    id: 'mirador-viewer', // id selector where Mirador should be instantiated
    theme: {
        palette: {
            primary: {
                main: "#1967d2",
            },
        },
    },
    windows: [{
        manifestId,
        view: 'single',
    }],
    window: {
        allowClose: false, // Prevent the user from closing this window
        allowMaximize: false,
        allowFullscreen: true,
        defaultSideBarPanel: 'info',
        sideBarOpenByDefault: false,
        highlightAllAnnotations: true,
        views: [ // Only allow the user to select single and gallery view
            { key: 'single' },
            { key: 'gallery' },
        ]
    },
    thumbnailNavigation: {
        defaultPosition: 'far-bottom',
    },
    workspace: {
        type: 'mosaic',
        showZoomControls: true,
    },
    workspaceControlPanel: {
        enabled: false, // Remove extra workspace settings
    },
});
