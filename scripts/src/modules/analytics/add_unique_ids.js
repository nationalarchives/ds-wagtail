const add_unique_ids = () => {

    const items = [
        {selector: '.blog-embed', id_prefix: 'analytics-blog-embed'},
        {selector: '.related-resources ul', id_prefix: 'analytics-related-resources'}
    ];

    items.forEach((item) => {

        try {
            const elements = document.querySelectorAll(item.selector);

            Array.prototype.forEach.call(elements, (element, index) => {
                element.id = `${item.id_prefix}-${index + 1}`;
            });

        } catch (e) {
            console.error(`Error in generate_unique_ids module`);
        }
    })
};

export default add_unique_ids;
