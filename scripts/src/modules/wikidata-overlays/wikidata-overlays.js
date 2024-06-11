/**
 * fetchData
 *
 * @param {String} url
 * @returns {Promise<Object>}
 *
 * Fetch data from a given URL
 */
const fetchData = async (url) => {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error("Network response was not ok");
    }

    return response.json();
};

const createTemplate = (data, tagType) => {
    const template = document.createElement("template");

    const tagTypeTemplate = tagType
        ? `<p class="wikidata__description">${tagType}</p>`
        : "";
    const imageTemplate = data.imagePath
        ? `<img src="${data.imagePath}" alt="" width="74" class="wikidata__header-img" loading="lazy">`
        : "";
    const countryTemplate = data.countryLabel
        ? `<p class="wikidata__header-meta">${data.countryLabel}</p>`
        : "";
    const titleTemplate = data.label
        ? `<h3 class="wikidata__label">${data.label}</h3>`
        : "";
    const descriptionTemplate = data.description
        ? `<p>${data.description}</p>`
        : "";
    const idTemplate = data.id ? `${data.id}` : "";

    template.innerHTML = `
    <div class="wikidata__header">
      ${imageTemplate}

      <div>
        ${tagTypeTemplate}
        ${titleTemplate}
        ${countryTemplate}
      </div>
    </div>

    <div class="wikidata__content">
      ${descriptionTemplate}

      <div class="wikidata__footer">
        <img src="/static/images/wikidata-logo.png" width="34" height="25" alt="Wikidata logo">
        ${idTemplate}
      </div>
    </div>
  `;

    return template;
};

/**
 * createWikidataOverlays
 *
 * @param {Object} data
 */
const createWikidataOverlays = (data) => {
    Object.entries(data).forEach(([id, item]) => {
        // Multiple tags can have the same wikidata entry
        const overlayContainers = document.querySelectorAll(
            `[data-js-wikidata-overlay="https://www.wikidata.org/wiki/${id}"]`,
        );

        overlayContainers.forEach((overlayContainer) => {
            const tagType = overlayContainer.getAttribute(
                "data-js-wikidata-tag-type-label",
            );

            const template = createTemplate(item, tagType);
            overlayContainer.appendChild(template.content);
        });
    });
};

const wikidataLinks = document.querySelectorAll("[data-js-wikidata-url]");
const wikidataIds = [...wikidataLinks].map((link) =>
    link.getAttribute("data-js-wikidata-url").split("/").pop(),
);

/**
 * Multiple tags can have the same wikidata entry so we remove them before building the API query
 */
const uniqueWikidataIds = [...new Set(wikidataIds)];

/**
 * buildSparqlQuery
 *
 * Build query using SPARQL to fetch data from Wikidata
 * {@link https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial}
 *
 * To assist building the query it's possible to get entity data from the rest API
 * {@link https://www.wikidata.org/w/rest.php/wikibase/v0/entities/items/[entityId]}
 *
 * It's also possible to browse properties by ID
 * {@link https://hay.toolforge.org/propbrowse/}
 *
 * @param {Array} ids
 * @returns {String}
 */
const buildSparqlQuery = (ids) => `
# Properties that will be returned by the API
SELECT ?item ?finalItem ?label ?description ?image ?countryLabel
WHERE {
  VALUES ?item { ${ids.map((id) => `wd:${id}`).join(" ")} }

  # Handle redirects
  OPTIONAL {
    ?item owl:sameAs ?redirectedItem .
  }

  # Use the redirected item if it exists, otherwise use the original item
  BIND(COALESCE(?redirectedItem, ?item) AS ?finalItem)

  # Specific fields for each item
  OPTIONAL {
    ?finalItem rdfs:label ?label .
    FILTER(LANG(?label) = "en")
  }

  OPTIONAL {
    ?finalItem schema:description ?description .
    FILTER(LANG(?description) = "en")
  }

  OPTIONAL { ?finalItem wdt:P18 ?image . }

  OPTIONAL {
    ?finalItem wdt:P17 ?country .
    ?country rdfs:label ?countryLabel .
    FILTER(LANG(?countryLabel) = "en")
  }
}
`;

const executeSparqlQuery = async (query) => {
    const url = `https://query.wikidata.org/sparql?query=${encodeURIComponent(query)}&format=json`;
    const data = await fetchData(url);
    return data;
};

const formattedData = {};

const addResultToFormattedData = (result) => {
    const id = result.item.value.split("/").pop();

    if (!formattedData[id]) {
        formattedData[id] = {
            id,
            label: result.label.value,
            countryLabel: result?.countryLabel?.value,
            description: result.description.value,
            imagePath: result?.image?.value
                ? `${result.image.value}?width=74`
                : "",
        };
    }
};

const init = async () => {
    const sparqlQuery = buildSparqlQuery(uniqueWikidataIds);
    const data = await executeSparqlQuery(sparqlQuery);
    const results = data?.results?.bindings || [];

    results.forEach((result) => {
        addResultToFormattedData(result);
    });

    if (Object.keys(formattedData).length > 0) {
        createWikidataOverlays(formattedData);
    }
};

init().catch((error) => console.error("init - Error fetching data:", error));
