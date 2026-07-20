from wagtail.test.utils import WagtailPageTestCase

from app.api.models import APIToken
from app.media.models import EtnaMedia


class MediaAPITest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.api_token = APIToken.objects.create(name="media-api-token")
        cls.media = EtnaMedia.objects.create(
            title="Media with chapters",
            file="media/test.mp4",
            type="video",
            duration=10,
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
            chapters=[
                (
                    "chapter",
                    {
                        "time": "00:00:05",
                        "heading": "Second",
                        "transcript": "",
                    },
                ),
                (
                    "chapter",
                    {
                        "time": "00:00:02",
                        "heading": "First",
                        "transcript": "",
                    },
                ),
            ],
        )

    def request_api(self, path):
        return self.client.get(
            path,
            format="json",
            HTTP_AUTHORIZATION=f"Token {self.api_token.key}",
        )

    def test_media_listing_returns_chapters_as_sorted_seconds(self):
        response = self.request_api("/api/v2/media/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        media_item = next(
            item for item in payload["items"] if item["uuid"] == str(self.media.uuid)
        )

        self.assertEqual(
            [chapter["time"] for chapter in media_item["chapters"]], [2, 5]
        )
        self.assertTrue(
            all(isinstance(chapter["time"], int) for chapter in media_item["chapters"])
        )

    def test_media_detail_returns_chapters_as_sorted_seconds(self):
        response = self.request_api(f"/api/v2/media/{self.media.uuid}/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual([chapter["time"] for chapter in payload["chapters"]], [2, 5])
        self.assertTrue(
            all(isinstance(chapter["time"], int) for chapter in payload["chapters"])
        )
