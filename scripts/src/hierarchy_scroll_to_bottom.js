const scroll_to_bottom = () => {
	const hierarchy_list = document.querySelector('.hierarchy-global__list');
	hierarchy_list.scrollTo(0, hierarchy_list.scrollHeight)
}

scroll_to_bottom();
