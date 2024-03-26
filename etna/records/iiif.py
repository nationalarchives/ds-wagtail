from collections.abc import Sequence
from typing import Literal, NotRequired, TypedDict


class InvalidManifestFormat(Exception):
    pass


class AnnotationItemBody(TypedDict):
    id: str
    type: Literal["Image"]
    height: NotRequired[int]
    width: NotRequired[int]


class AnnotationItem(TypedDict):
    id: str
    type: Literal["Annotation"]
    motivation: Literal["painting"]
    body: AnnotationItemBody
    target: str


class AnnotationPageItem(TypedDict):
    id: str
    type: Literal["AnnotationPage"]
    items: Sequence[AnnotationItem]


class ManifestItem(TypedDict):
    id: str
    height: int
    width: int
    type: Literal["Canvas"]
    items: Sequence[AnnotationPageItem]


class IIIFResourceJSON(TypedDict):
    type: Literal["Manifest"]
    items: list[ManifestItem]


class IIIFResource:
    content: IIIFResourceJSON

    def __init__(self, *, raw_data: IIIFResourceJSON) -> None:
        self.content = raw_data


class IIIFManifest(IIIFResource):
    pass


def create_resource(resource_json: IIIFResourceJSON) -> "IIIFResource":
    if resource_json["type"] == "Manifest":
        return IIIFManifest(raw_data=resource_json)
    return IIIFResource(raw_data=resource_json)


class ImageNotFoundInItem(Exception):
    pass


class ItemImage:
    url: str
    width: int | None
    height: int | None


class ManifestParser:
    manifest: IIIFManifest
    __items: list[ManifestItem] | None = None

    def __init__(self, *, manifest: IIIFManifest) -> None:
        self.manifest = manifest

    def get_items(self) -> list[ManifestItem]:
        if self.__items is not None:
            return self.__items
        self.__items = self.manifest.content["items"]
        return self.__items

    def get_item_at_index(self, index: int) -> ManifestItem:
        return self.get_items()[index]

    def get_last_index(self) -> int:
        return len(self.get_items()) - 1

    def get_items_count(self) -> int:
        return len(self.get_items())

    @classmethod
    def get_images_for_item(cls, item: ManifestItem) -> list[ItemImage]:
        if item["type"] != "Canvas":
            raise InvalidManifestFormat("Item is not a canvas.")
        canvas_items = item["items"]
        for canvas_item in canvas_items:
            if canvas_item["type"] == "AnnotationPage":
                for annotation_page_item in canvas_item["items"]:
                    body = annotation_page_item.get("body")
                    if body is not None and body["type"] == "Image":
                        if image_id := body["id"]:
                            image_dict: ItemImage = {
                                "url": image_id,
                                "width": body.get("width"),
                                "height": body.get("height"),
                            }
                            return [image_dict]
        raise ImageNotFoundInItem
