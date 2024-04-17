/**
 * LeafletJS
 * Docs - {@link https://leafletjs.com/}
 */
import L from "leaflet";

/**
 * Leaflet Marker Cluster plugin
 * Docs - {@link https://github.com/Leaflet/Leaflet.markercluster}
 */
import "leaflet.markercluster";

// Data will be replaced with dynamic API data in a future phase
import data from "./data/map-data-unprocessed.json";

// Filter data to include only items with lat and lon
const dataWithLatLon = data.data.filter((item) => {
    const details = item["@template"].details;
    return details.lat && details.lon;
});

// Convert data to GeoJSON format
const dataToGeoJson = {
    type: "FeatureCollection",
    features: dataWithLatLon.map((item) => {
        const { lat, lon, title, description, itemURL, collection, ciimId } =
            item["@template"].details;

        return {
            type: "Feature",
            geometry: {
                type: "Point",
                coordinates: [lon, lat],
            },
            properties: {
                title,
                description,
                itemURL,
                collection,
                ciimId,
            },
        };
    }),
};

export default function () {
    const mapElement = document.getElementById("ohos-search-results-map");

    // Get lat, lon, and zoom query string parameters to set initial map state
    const queryStringParams = new URLSearchParams(document.location.search);

    const queryStringHasLatAndLon =
        queryStringParams.get("lat") && queryStringParams.get("lon");

    const defaultLat = mapElement.dataset.jsDefaultLat;
    const defaultLon = mapElement.dataset.jsDefaultLon;
    const defaultZoom = mapElement.dataset.jsDefaultZoom;

    const initialLat = queryStringHasLatAndLon
        ? queryStringParams.get("lat")
        : defaultLat;
    const initialLon = queryStringHasLatAndLon
        ? queryStringParams.get("lon")
        : defaultLon;
    const initialZoom = queryStringParams.get("zoom") ?? defaultZoom;

    // Initialize map
    const map = L.map(mapElement, {
        center: [initialLat, initialLon],
        minZoom: 3,
        zoom: initialZoom,
        zoomControl: false, // Disable default zoom control so it can be positioned in the top right corner
    });

    // Define and add zoom control position
    L.control
        .zoom({
            position: "topright",
        })
        .addTo(map);

    // Define and add tile layer (map canvas)
    L.tileLayer("http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", {
        attribution:
            '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);

    // Define and add icon for marker cluster group
    const markers = L.markerClusterGroup({
        iconCreateFunction: function (cluster) {
            const clusteredMarkersCount = cluster.getChildCount();

            return L.divIcon({
                html: `
                    <div>
                        <span>${clusteredMarkersCount}</span>
                    </div>
                `,
                className: "leaflet-marker-icon marker-cluster",
                iconSize: L.point(54, 54),
            });
        },
    }).addTo(map);

    // Define icon for marker
    const markerIcon = L.icon({
        iconUrl: "../../static/images/icons/icon-map-pin.svg",
        iconSize: [31, 39],
        iconAnchor: [15, 39],
    });

    // Popup options
    const popupOptions = {
        maxWidth: 400,
        offset: [0, -35],
        className: "ohos-popup",
    };

    // Create GeoJSON layer with popups
    L.geoJSON(dataToGeoJson, {
        onEachFeature(feature, layer) {
            // Popup content
            const templateTitle = feature.properties.title
                ? `<h3 class="tna-heading-m"><a href="/catalogue/id/${feature.properties.ciimId}">${feature.properties.title}</a></h3>`
                : "";
            const templateDescription = feature.properties.description
                ? `<p>${feature.properties.description}</p>`
                : "";
            const templateCollection = feature.properties.collection
                ? `Collection: <a href="/search/catalogue/?collection=${feature.properties.collection}">${feature.properties.collection}</a>`
                : "";

            const popupTemplate = `
                <div>
                    <i class="ohos-popup__icon fa-solid fa-file"></i>
                </div>
                <div class="ohos-popup__content">
                    ${templateTitle}
                    ${templateDescription}
                    ${templateCollection}
                </div>
            `;

            // Bind popup to layer
            layer.bindPopup(popupTemplate, popupOptions);
        },
        // Create markers and add to marker cluster group
        pointToLayer(feature, latlon) {
            const marker = L.marker(latlon, { icon: markerIcon });
            markers.addLayer(marker);
            return marker;
        },
    });

    // Add moveend event listener to map and update queryParams for link sharing
    map.on("moveend", function () {
        const { lat, lng: lon } = map.getCenter();
        const zoom = map.getZoom();

        const state = { lat, lon, zoom };
        const url = new URL(location);
        lat && url.searchParams.set("lat", lat);
        lon && url.searchParams.set("lon", lon);
        zoom && url.searchParams.set("zoom", zoom);

        history.pushState(state, "", url);
    });
}
