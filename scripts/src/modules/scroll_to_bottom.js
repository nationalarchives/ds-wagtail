const scroll_to_bottom = (element) => {
	if(element){
		element.scrollTo(0, element.scrollHeight)
	}
};

export default scroll_to_bottom;
