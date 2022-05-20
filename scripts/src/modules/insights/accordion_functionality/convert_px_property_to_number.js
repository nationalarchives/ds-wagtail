export default function convert_px_property_to_number(property) {
    return parseInt(property.replace("px", ""));
}
