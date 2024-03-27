import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from booking.models import (
    AstronomyShow,
    PlanetariumDome,
    ShowSeason,
)
from booking.serializers import (
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
)

ASTRONOMY_SHOW_URL = reverse("booking:astronomyshow-list")
SHOW_SEASON_URL = reverse("booking:showseason-list")


def sample_astronomy_show(**params):
    defaults = {
        "title": "Sample astronomy show",
        "description": "Sample description",
    }
    defaults.update(params)

    return AstronomyShow.objects.create(**defaults)


def sample_show_season(**params):
    astronomy_show = sample_astronomy_show(
        title="title",
        description="description"
    )
    planetarium_dome = PlanetariumDome.objects.create(
        name="Planetarium Dome",
        rows=10,
        seats_in_row=20,
    )
    defaults = {
        "astronomy_show": astronomy_show,
        "planetarium_dome": planetarium_dome,
        "show_time": "2024-06-02 14:00:00",
    }
    defaults.update(params)

    return ShowSeason.objects.create(**defaults)


def image_upload_url(astronomy_show_id):
    return reverse(
        "booking:astronomyshow-upload-image",
        args=[astronomy_show_id]
    )


def detail_url(astronomy_show_id):
    return reverse("booking:astronomyshow-detail", args=[astronomy_show_id])


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "password",
        )
        self.client.force_authenticate(self.user)

    def test_astronomy_show_list(self):
        sample_astronomy_show()
        sample_astronomy_show()

        res = self.client.get(ASTRONOMY_SHOW_URL)

        astronomy_shows = AstronomyShow.objects.all()
        serializer = AstronomyShowListSerializer(astronomy_shows, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_astronomy_shows_by_title(self):
        astronomy_show1 = sample_astronomy_show(title="show1")
        astronomy_show2 = sample_astronomy_show(title="show2")
        astronomy_show3 = sample_astronomy_show(title="another")

        res = self.client.get(ASTRONOMY_SHOW_URL, {"title": "show"})

        serializer1 = AstronomyShowListSerializer(astronomy_show1)
        serializer2 = AstronomyShowListSerializer(astronomy_show2)
        serializer3 = AstronomyShowListSerializer(astronomy_show3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_retrieve_astronomy_show(self):
        astronomy_show = sample_astronomy_show()

        url = detail_url(astronomy_show.id)
        res = self.client.get(url)

        serializer = AstronomyShowDetailSerializer(astronomy_show)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # def test_create_astronomy_show_forbidden(self):
    #     payload = {
    #         "title": "title",
    #         "description": "some description",
    #     }
    #     res = self.client.get(ASTRONOMY_SHOW_URL, payload)
    #
    #     self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlanetariumApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_astronomy_show(self):
        payload = {
            "title": "title",
            "description": "Description",
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_put_astronomy_show_not_allowed(self):
        payload = {
            "title": "New movie",
            "description": "New description",
        }

        astronomy_show = sample_astronomy_show()
        url = detail_url(astronomy_show.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_astronomy_show_not_allowed(self):
        astronomy_show = sample_astronomy_show()
        url = detail_url(astronomy_show.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_image_to_astronomy_show_list(self):
        url = ASTRONOMY_SHOW_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Title",
                    "description": "Description",
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
