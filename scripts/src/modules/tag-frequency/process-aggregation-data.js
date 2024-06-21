import { aggregations } from "./data/aggregations.js";

export const processAggregationData = (chartContainer) => {
    if (!chartContainer) {
        return;
    }

    const data =
        JSON.parse(chartContainer.getAttribute("data-js-tag-frequency-data")) ??
        aggregations;

    /**
     * Maximum number of entries to display in chart
     */
    const MAX_ENTRIES = 20;

    /**
     * getEntriesByType
     *
     * @param {String} type
     * @returns {Array}
     *
     * Helper function to get entries by type
     */
    const getEntriesByType = (type) =>
        data.find((aggregation) => aggregation.name === type)?.entries;

    /**
     * mapDataByType
     *
     * @param {Array} data
     * @param {String} type
     * @returns {Array}
     *
     * Helper function to add type to entry
     */
    const mapDataByType = (data, type) => {
        const mappedData = data?.map((entry) => {
            return {
                term: entry.value,
                count: entry.doc_count,
                type,
            };
        });

        return mappedData ?? [];
    };

    const locationEntries = getEntriesByType("enrichmentLoc");
    const mappedLocations = mapDataByType(locationEntries, "LOC");

    const personEntries = getEntriesByType("enrichmentPer");
    const mappedPersons = mapDataByType(personEntries, "PER");

    const orgEntries = getEntriesByType("enrichmentOrg");
    const mappedOrgs = mapDataByType(orgEntries, "ORG");

    const miscEntries = getEntriesByType("enrichmentMisc");
    const mappedMisc = mapDataByType(miscEntries, "MISC");

    const allEntries = [
        ...mappedLocations,
        ...mappedPersons,
        ...mappedOrgs,
        ...mappedMisc,
    ];

    const entriesSortedByCount = allEntries.sort((a, b) => b.count - a.count);

    const dataByQueryParam = {
        LOC: mappedLocations,
        PER: mappedPersons,
        ORG: mappedOrgs,
        MISC: mappedMisc,
        default: entriesSortedByCount,
    };

    // The code below shouldn't be needed once we're working with the live API
    const urlParams = new URLSearchParams(window.location.search);

    const dataTypeParam = urlParams.get("chart_data_type");

    const categorisedEntries =
        dataByQueryParam[dataTypeParam] ?? dataByQueryParam.default;

    const topEntries = categorisedEntries.slice(0, MAX_ENTRIES);

    return topEntries;
};
