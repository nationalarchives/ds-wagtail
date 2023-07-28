const scroll_to_bottom = (element, container) => {
    try {
        const elementRect = element.getBoundingClientRect();
        const scrollY = elementRect.top;
        container.scrollLeft = 0;
        container.scrollTop = scrollY;
    } catch (e) {
        console.error(e);
    }
};

export default scroll_to_bottom;
