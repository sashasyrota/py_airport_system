import os
import tempfile

from PIL import Image
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport_system.models import AirplaneType, Airplane
from airport_system.serializers import (
    AirplaneRetrieveSerializer,
    AirplaneListSerializer
)
from user.models import User


AIRPLANE_URL = reverse("airport_system:airplane-list")


def airplane_image_upload_url(airplane_id: int):
    return reverse("airport_system:airplane-upload-image", args=(airplane_id,))


def airplane_detail_url(airplane_id: int):
    return reverse("airport_system:airplane-detail", args=(airplane_id,))


def sample_airplane(**params):
    airplane_type = AirplaneType.objects.create(name="test_type")
    defaults = {
        "name": "test_airplane",
        "rows": 6,
        "seats_in_row": 6,
        "airplane_type": airplane_type
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


class UnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(AIRPLANE_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test", password="testtest")
        self.client.force_authenticate(self.user)
        self.airplane = sample_airplane()

    def test_airplane_list(self):
        result = self.client.get(AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data["results"], serializer.data)

    def test_filter_airplane_by_airplane_types(self):
        airplane_type1 = AirplaneType.objects.create(name="test_type1")
        params1 = {
            "name": "test_airplane1",
            "airplane_type": airplane_type1
        }
        sample_airplane(**params1)
        airplanes = Airplane.objects.filter(airplane_type=airplane_type1.id)
        result = self.client.get(
            f"{AIRPLANE_URL}"
            f"?airplane_types={airplane_type1.id}"
        )
        serializer = AirplaneListSerializer(airplanes, many=True)
        self.assertEqual(result.data["results"], serializer.data)

    def test_retrieve_airplane(self):
        airplane = sample_airplane()
        url = airplane_detail_url(airplane.id)
        result = self.client.get(url)
        serializer = AirplaneRetrieveSerializer(airplane)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_airplane(self):
        result = self.client.post(AIRPLANE_URL)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_admin_upload_image_to_airplane(self):
        url = airplane_image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airplane.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn("image", res.data)


class AdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            email="admin_test",
            password="admin_testtest",
            is_staff=True
        )
        self.client.force_authenticate(self.admin_user)
        self.airplane = sample_airplane()
        self.airplane_type = AirplaneType.objects.create(name="test_type")

    def test_admin_create_airplane(self):
        data_airplane = {
            "name": "test_airplane",
            "rows": 6,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.pk
        }
        result = self.client.post(AIRPLANE_URL, data_airplane)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_upload_image_to_airplane(self):
        url = airplane_image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airplane.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        url = airplane_image_upload_url(self.airplane.id)
        res = self.client.post(url, {"image": "not_image"}, format="multipart")
        self.airplane.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list(self):
        url = AIRPLANE_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "test_airplane1",
                    "rows": 6,
                    "seats_in_row": 6,
                    "airplane_type": self.airplane_type.pk,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(name="test_airplane1")
        self.assertFalse(airplane.image)

    def test_image_shown_in_airplane_detail(self):
        url = airplane_image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(airplane_detail_url(self.airplane.id))
        self.assertTrue(res.data["image"])
        self.airplane.refresh_from_db()

    def test_image_shown_in_airplane_list(self):
        url = airplane_image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPLANE_URL)
        for result in res.data["results"]:
            self.assertNotIn("image", result)
