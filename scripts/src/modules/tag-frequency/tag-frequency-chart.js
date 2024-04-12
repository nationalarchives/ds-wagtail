import * as d3 from "d3";
import debounce from "../../modules/debounce";

/**
 * process-sample-data.js is used to turn the raw data into a format that can be used by the chart
 * It's not intended for this step to be required in the final implementation
 */
import { termsRange } from "./process-sample-data.js";

const SELECTED_PARAM_NAME = "chart_selected";

/**
 * Colours are mapped to `ne_type` in the data
 */
const colorsMap = {
    LOC: "#EDAE49",
    PER: "#84A59D",
    ORG: "#B5E2FA",
    MISC: "#F28482",
    DATE: "#FAF0CA",
};

const urlParams = new URLSearchParams(window.location.search);

/**
 * @param {String} term
 * @param {String} type
 * @returns {Boolean}
 */
const isSelectedItem = (term, type) => {
    const selectedParams = urlParams.getAll(SELECTED_PARAM_NAME);

    return selectedParams.includes(`${term} ${type}`);
};

/**
 * Create href for each circle
 * @param {String} term
 * @param {String} type
 * @returns {String}
 */
const createHref = (term, type) => {
    const newParams = new URLSearchParams(window.location.search);

    if (isSelectedItem(term, type)) {
        newParams.delete(SELECTED_PARAM_NAME, `${term} ${type}`);
    } else {
        newParams.append(SELECTED_PARAM_NAME, `${term} ${type}`);
    }

    return `?${newParams.toString()}`;
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
        <circle cx="13.834" cy="13.833" r="13.5" fill="#D9D9D6"/>
        <path fill="#1E1E1E" fill-rule="evenodd" d="M14 24.5a10.5 10.5 0 1 0 0-21 10.5 10.5 0 0 0 0 21Zm-.27-6.253 5.833-7-1.792-1.494-5.017 6.02-2.596-2.598-1.65 1.65 3.5 3.5.904.903.817-.981Z" clip-rule="evenodd"/>
      </symbol>
    `);

    // Create a group for each circle and text element
    const node = svg
        .selectAll("a")
        .data(dataWithRadius)
        .join("a")
        .attr("href", (d) => createHref(d.term, d.type));

    // Append circle to each group
    node.append("circle")
        .attr("r", (d) => d.radius)
        .attr("fill", (d) => colorsMap[d.type])
        .attr("stroke", (d) =>
            isSelectedItem(d.term, d.type) ? "#1E1E1E" : "#8A8A8A",
        )
        .attr("stroke-width", (d) => (isSelectedItem(d.term, d.type) ? 5 : 1));

    // Add icon to selected icon at specified angle
    const selectedIconAngleDegrees = 40;
    const selectedIconAngleRadians = (selectedIconAngleDegrees * Math.PI) / 180;

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
    };
};

/**
 * Initialisation
 */
const disableAnimation = window.location.search.includes(
    "disableAnimation=true",
);

const containerForceSimulation = document.getElementById("tag-frequency-chart");

const init = () => {
    if (!containerForceSimulation) return;

    const chartCustom = chartForceSimulation(termsRange, {
        disableAnimation,
        container: containerForceSimulation,
    });

    containerForceSimulation.appendChild(chartCustom.chartElement);

    const containerResizeObserver = new ResizeObserver(
        debounce(chartCustom.updateSize, 250),
    );

    containerResizeObserver.observe(containerForceSimulation);
};

init();
