import * as d3 from "d3";
import debounce from "../../modules/debounce";

import { processAggregationData } from "./process-aggregation-data.js";

/**
 * Shared variables between chart rendering and state
 */

// Add icon to selected icon at specified angle
const selectedIconAngleDegrees = 40;
const selectedIconAngleRadians = (selectedIconAngleDegrees * Math.PI) / 180;

/**
 * Manage Chart State
 */
const form = document.querySelector("[data-js-form-tag-frequency]");
const formApplyButton = document.querySelector("[data-js-tag-frequency-apply]");
const formClearButton = document.querySelector("[data-js-tag-frequency-clear]");

const SELECTED_PARAM_NAME = "chart_selected";

const urlParams = new URLSearchParams(window.location.search);
const initialSelection = urlParams.getAll(SELECTED_PARAM_NAME);

const hasInitialSelection = initialSelection.length > 0;

let currentSelection = initialSelection;

const setCurrentSelection = () => {
    const formInputs = form.querySelectorAll(
        `input[name=${SELECTED_PARAM_NAME}]`,
    );

    currentSelection = [...formInputs].map((input) =>
        input.getAttribute("value"),
    );

    return currentSelection;
};

const clearFormAndSumbit = () => {
    form.querySelectorAll(`input[name=${SELECTED_PARAM_NAME}]`).forEach(
        (input) => {
            input.remove();
        },
    );

    form.submit();
};

const formMatchesInitialSelection = () =>
    JSON.stringify(initialSelection) === JSON.stringify(currentSelection);

/**
 * Toggle the apply button based on the current selection
 */
const toggleApplyButton = () => {
    setCurrentSelection();

    if (formMatchesInitialSelection()) {
        formApplyButton.setAttribute("hidden", "hidden");
    } else {
        formApplyButton.removeAttribute("hidden");
    }
};

const populateForm = () => {
    if (!form) return;

    urlParams.forEach((value, key) => {
        const element = document.createElement("input");

        element.type = "hidden";

        element.name = key;
        element.value = value;

        form.appendChild(element);
    });
};

const addInput = (term, type) => {
    const newInput = document.createElement("input");

    const formInputs = form.querySelectorAll(
        `input[name=${SELECTED_PARAM_NAME}]`,
    );

    const value = `${type}:${term}`;

    newInput.type = "hidden";

    newInput.name = SELECTED_PARAM_NAME;
    newInput.value = value;

    let inserted = false;

    // Elements are added in alphabetical order to ensure a level of consistency on the query string
    for (const input of formInputs) {
        if (input.value.localeCompare(value) > 0) {
            form.insertBefore(newInput, input);
            inserted = true;
            break;
        }
    }

    if (!inserted) {
        form.appendChild(newInput);
    }
};

const removeInput = (term, type) => {
    const element = form.querySelector(`input[value="${type}:${term}"]`);

    if (element) {
        element.remove();
    }
};

/**
 * @param {String} term
 * @param {String} type
 * @returns {Boolean}
 */
const isSelectedItem = (term, type) => {
    const formInputs = form.querySelectorAll(
        `input[name=${SELECTED_PARAM_NAME}]`,
    );

    const matchingInput = [...formInputs].find((input) => {
        return input.value === `${type}:${term}`;
    });

    return matchingInput !== undefined;
};

function toggleSelectedItem(selectedElement, term, type) {
    if (isSelectedItem(term, type)) {
        removeInput(term, type);

        d3.select(selectedElement)
            .select("circle")
            .attr("stroke", "#8A8A8A")
            .attr("stroke-width", 1);

        d3.select(selectedElement).select("use").remove();
    } else {
        addInput(term, type);

        d3.select(selectedElement)
            .select("circle")
            .attr("stroke", "#1E1E1E")
            .attr("stroke-width", 5);

        d3.select(selectedElement)
            .append("use")
            .attr("href", "#selected-icon")
            .attr("width", "28")
            .attr("height", "28")
            .attr(
                "x",
                (d) => d.radius * Math.sin(selectedIconAngleRadians) - 14,
            )
            .attr(
                "y",
                (d) => -d.radius * Math.cos(selectedIconAngleRadians) - 14,
            );
    }

    toggleApplyButton();
}

/**
 * Colours are mapped to `ne_type` in the data
 */
const colorsMap = {
    LOC: "#EDAE49",
    PER: "#84A59D",
    ORG: "#B5E2FA",
    MISC: "#F28482",
};

/**
 * setCircleRadius
 *
 * @param {Array} data - Data containg count value
 * @param {Number} width - Width of the canvas
 * @param {Number} height - Height of the canvas
 * @returns {Array} - Data with radius value
 */
const setCircleRadius = (data, width, height) => {
    /**
     * Amount to scale the area of the canvas by
     */
    const scaleAreaValue = 0.4;

    /**
     * Area of the canvas, scaled down to allow for spacing around the circles
     */
    const scaledCanvasArea = width * height * scaleAreaValue;

    /**
     * Map data to an array of count values
     *
     * @returns {Array}
     */
    const countValues = data.map((d) => d.count);

    /**
     * Get smallest count value, to make it possible to create a range between the smallest and largest values
     */
    const smallestValue = Math.min(...countValues);

    /**
     * Get largest count value, to make it possible to create a range between the smallest and largest values
     */
    const largestValue = Math.max(...countValues);

    /**
     * Normalise the range of the count values
     * @returns {Function}
     */
    const normaliseRange = d3
        .scaleSqrt()
        .domain([smallestValue, largestValue])
        .range([50, 85]);

    /**
     * Convert the countValues to scaled radius values
     * @returns {Array}
     */
    const dataMappedToRadius = countValues.map((d) => normaliseRange(d));

    /**
     * Square the radius values to get their area
     * @returns {Array}
     */
    const circleAreas = dataMappedToRadius.map((value) => Math.pow(value, 2));

    /**
     * Add each value together to get the total area
     * @returns {Number}
     */
    const sumOfSquaredValues = circleAreas.reduce((acc, val) => acc + val, 0);

    /**
     * Calculate the scaling factor to apply to the area of each circle
     */
    const scalingFactor = scaledCanvasArea / sumOfSquaredValues;

    /**
     * Scale the area of each circle to fit the canvas
     * @returns {Array}
     */
    const scaledSquareAreas = circleAreas.map((value) => value * scalingFactor);

    /**
     * Get the square root of the scaled area values to get the dimensions of the circles
     */
    const scaledCircleRadius = scaledSquareAreas.map(
        (value) => Math.sqrt(value) / 2,
    );

    /**
     * Function to get the radius of the circle from the `scaledCircleRadius` array
     * @param {Array} d Data
     * @param {Number} i Index
     * @returns
     */
    const getCircleRadius = (i) => scaledCircleRadius[i];

    /**
     * Map the data to include the radius value
     * @returns {Array}
     */
    const dataWithRadius = data.map((d, i) => {
        return {
            ...d,
            radius: getCircleRadius(i),
        };
    });

    return dataWithRadius;
};

/**
 * Create a d3 force simulation chart
 * @param {Array} data
 * @param {Object} options
 * @returns {HTMLElement}
 */
const chartForceSimulation = (data, options = {}) => {
    const { height = 550, disableAnimation = true, container = null } = options;

    let containerWidth = container.getBoundingClientRect().width;
    const dataWithRadius = setCircleRadius(data, containerWidth, height);

    /**
     * Create d3 instance of SVG element
     */
    const svg = d3
        .create("svg")
        .attr("width", "100%")
        .attr("height", height)
        .attr("font-size", 14)
        .attr("font-family", "sans-serif")
        .attr("text-anchor", "middle");

    // Add selected icon symbol to the SVG
    svg.append("defs").html(`
      <symbol id="selected-icon" viewBox="0 0 28 28">
  <g transform="rotate(0 14 14)">
    <circle cx="14.0000" cy="14.0000" r="13.5" fill="#000000" stroke="#FFFFFF" stroke-width="2"/>
    <path fill="none" stroke="#FFFFFF" stroke-width="2" d="M
      ${14 + Math.cos(Math.PI / 4) * (13.5 - 7)}  ${
          14 + Math.sin(Math.PI / 4) * (13.5 - 7)
      }  L
      ${14 - Math.cos(Math.PI / 4) * (13.5 - 7)}  ${
          14 - Math.sin(Math.PI / 4) * (13.5 - 7)
      }  "/>
    <path fill="none" stroke="#FFFFFF" stroke-width="2" d="M
      ${14 + Math.sin(Math.PI / 4) * (13.5 - 7)}  ${
          14 - Math.cos(Math.PI / 4) * (13.5 - 7)
      }  L
      ${14 - Math.sin(Math.PI / 4) * (13.5 - 7)}  ${
          14 + Math.cos(Math.PI / 4) * (13.5 - 7)
      }  "/>
  </g>
</symbol>
`);

    // Create a group for each circle and text element
    const node = svg
        .selectAll("g.circle-group")
        .data(dataWithRadius)
        .join("g")
        .attr("class", "circle-group")
        .attr("data-term", (d) => d.term)
        .attr("data-type", (d) => d.type)
        .attr("cursor", "pointer");

    // Append circle to each group
    node.append("circle")
        .attr("r", (d) => d.radius)
        .attr("fill", (d) => colorsMap[d.type])
        .attr("stroke", (d) =>
            isSelectedItem(d.term, d.type) ? "#1E1E1E" : "#8A8A8A",
        )
        .attr("stroke-width", (d) => (isSelectedItem(d.term, d.type) ? 5 : 1));

    node.each(function (d) {
        if (isSelectedItem(d.term, d.type)) {
            d3.select(this)
                .append("use")
                .attr("href", "#selected-icon")
                .attr("width", "28")
                .attr("height", "28")
                .attr(
                    "x",
                    (d) => d.radius * Math.sin(selectedIconAngleRadians) - 14,
                )
                .attr(
                    "y",
                    (d) => -d.radius * Math.cos(selectedIconAngleRadians) - 14,
                );
        }
    });

    // Append text to each group
    node.append("text")
        .selectAll("tspan")
        .data((d) => {
            const terms = d.term.split(/(?=[A-Z][a-z])/g);

            terms.push(`(${d.count.toLocaleString("en")})`);

            return terms;
        })
        .join("tspan")
        .attr("x", 0)
        .attr("y", (d, i, nodes) => `${i - nodes.length / 2 + 0.8}em`)
        .text((d) => d)
        .join("tspan");

    /**
     * Run the force simulation, responsible for positioning the circles within the SVG element
     * Gets called on initial page load, and when the SVG is resized
     * @param {Array} data
     * @param {Number} width
     * @param {Number} height
     */
    const runForceSimulation = (data, width, height) => {
        simulation
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("charge", d3.forceManyBody().strength(5))
            .force(
                "collision",
                d3.forceCollide().radius((d) => d.radius + 5),
            );

        if (width > height) {
            simulation.force("y", d3.forceY(height / 2).strength(0.03));
        } else {
            simulation.force("y", null);
        }

        if (disableAnimation) {
            simulation.nodes(data).stop().tick(300);
            node.attr("transform", (d) => `translate(${d.x}, ${d.y})`);
        } else {
            simulation
                .nodes(data)
                .on("tick", () =>
                    node.attr("transform", (d) => `translate(${d.x}, ${d.y})`),
                );
        }
    };

    /**
     * Create a d3 force simulation instance with initial radius data
     * {@link https://d3js.org/d3-force/simulation}
     */
    const simulation = d3.forceSimulation(dataWithRadius);

    runForceSimulation(dataWithRadius, containerWidth, height);

    d3.selectAll(node).on("click", (event) => {
        const selectedElement = event.target.closest(".circle-group");
        const term = d3.select(selectedElement).attr("data-term");
        const type = d3.select(selectedElement).attr("data-type");

        toggleSelectedItem(selectedElement, term, type);
    });

    const updateSize = () => {
        const newWidth = container.getBoundingClientRect().width;

        if (newWidth === containerWidth) return;

        containerWidth = newWidth;

        const newDataWithRadius = setCircleRadius(data, newWidth, height);

        // Update node data with the new radius values
        node.data(newDataWithRadius);

        // Update circle radius and icon position
        node.select("circle").attr("r", (d) => d.radius);

        node.select("use")
            .attr(
                "x",
                (d) => d.radius * Math.sin(selectedIconAngleRadians) - 14,
            )
            .attr(
                "y",
                (d) => -d.radius * Math.cos(selectedIconAngleRadians) - 14,
            );

        /**
         * Update simulation with new radius data calculated from the new width
         * and re run simulation
         */
        simulation.nodes(newDataWithRadius);

        runForceSimulation(newDataWithRadius, newWidth, height);

        simulation.alpha(1).restart();
    };

    return {
        chartElement: svg.node(),
        updateSize,
        node,
    };
};

/**
 * Initialisation
 */
const disableAnimation = window.location.search.includes(
    "disableAnimation=true",
);

const containerForceSimulation = document.getElementById("tag-frequency-chart");

const chartData = processAggregationData(containerForceSimulation);

const init = () => {
    if (!containerForceSimulation) return;

    populateForm();

    if (hasInitialSelection) {
        formClearButton.removeAttribute("hidden");
    }

    const chartCustom = chartForceSimulation(chartData, {
        disableAnimation,
        container: containerForceSimulation,
    });

    containerForceSimulation.appendChild(chartCustom.chartElement);

    const containerResizeObserver = new ResizeObserver(
        debounce(chartCustom.updateSize, 250),
    );

    containerResizeObserver.observe(containerForceSimulation);

    formClearButton.addEventListener("click", clearFormAndSumbit);
};

init();
