export default function add_section_ids(sectionHeadings, sectionContents) {
    $(sectionContents).each(function (index) {
        $(this).attr("id", sectionHeadings[index].id.slice(3));
    });
}
