/**
 * This file is used to turn the raw data into a format that can be used by the chart
 * It's not intended for this step to be required in the final implementation
 */
import { sampleData } from "./data/sample_2k_swop_output_21.02.24.js";

const termsAndTypes = [];

sampleData.forEach((item) => {
    if (item.mentions === undefined) return;

    item.mentions.forEach((mention) => {
        const { ne_span: term, ne_type: type } = mention;

        const existingEntryIndex = termsAndTypes.findIndex((item) => {
            return item.term === term && item.type === type;
        });

        if (existingEntryIndex === -1) {
            termsAndTypes.push({
                term,
                type,
                count: 1,
            });
        } else {
            termsAndTypes[existingEntryIndex].count += 1;
        }
    });
});

const termCountsSortedDescending = termsAndTypes.sort(
    (a, b) => b.count - a.count,
);

const urlParams = new URLSearchParams(window.location.search);

const dataTypes = ["LOC", "PER", "ORG", "MISC", "DATE"];

const dataTypeParam = urlParams.get("chart_data_type");

const dataFilteredByType = termCountsSortedDescending.filter((item) => {
    if (dataTypes.includes(dataTypeParam) === false) {
        return true;
    }

    return item.type === dataTypeParam;
});

const data = dataTypeParam ? dataFilteredByType : termCountsSortedDescending;

const rangeStartParam = urlParams.get("rangeStart");

const rangeStart = rangeStartParam ? parseInt(rangeStartParam) : 0;

export const termsRange = data.slice(rangeStart, rangeStart + 20);
