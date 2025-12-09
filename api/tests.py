from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Cat, Mission, Target


class CatTests(APITestCase):

    def setUp(self):
        self.cat = Cat.objects.create(
            name="Pipa", years_of_experience=7, breed="Ocicat", salary=50.01
        )
        self.list_url = reverse("cat-list")
        self.detail_url = reverse("cat-detail", kwargs={"pk": self.cat.pk})

    def test_create_cat_success(self):
        """Test creating a cat with a valid breed."""
        data = {
            "name": "Mushka",
            "years_of_experience": 2,
            "breed": "York Chocolate",
            "salary": 1000.00,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cat.objects.count(), 2)

    def test_get_existing_cat(self):
        """Test retrieving details for an existing cat."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Pipa")
        self.assertEqual(response.data["breed"], "Ocicat")
        self.assertEqual(response.data["salary"], 50.01)
        self.assertEqual(response.data["years_of_experience"], 7)

    def test_get_non_existing_cat(self):
        """Test that retrieving a non-existing cat returns a 404."""
        non_existing_url = reverse("cat-detail", kwargs={"pk": 999})
        response = self.client.get(non_existing_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_cat_invalid_salary(self):
        """Test that creating a cat with a negative salary fails."""
        data = {
            "name": "Furik",
            "years_of_experience": 2,
            "breed": "Toyger",
            "salary": -1000.00,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Cat.objects.count(), 1)

    def test_create_cat_invalid_years_of_experience(self):
        """Test that creating a cat with a negative negative years_of_experience fails."""
        data = {
            "name": "Furik",
            "years_of_experience": -2,
            "breed": "Toyger",
            "salary": 1000.00,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Cat.objects.count(), 1)

    def test_create_cat_invalid_breed(self):
        """Test that breed validation fails for non-existent breeds."""
        data = {
            "name": "Weeee",
            "years_of_experience": 10,
            "breed": "Ukrainian Unicorn",
            "salary": 100000.00,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("breed", response.data)

    def test_list_cats(self):
        """Test retrieving the list of cats."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_cat_salary(self):
        """Test updating only the cat's salary."""
        data = {"salary": 750.00}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cat.refresh_from_db()
        self.assertEqual(self.cat.salary, 750.00)

    def test_delete_cat(self):
        """Test removing a cat from the system."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cat.objects.count(), 0)
        list_response = self.client.get(self.list_url)
        self.assertEqual(0, len(list_response.json()))

    def test_delete_non_existing_cat(self):
        """Test that deleting a cat that does not exist returns a 404."""
        non_existing_url = reverse("cat-detail", kwargs={"pk": 999})
        response = self.client.delete(non_existing_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_change_cat_availability(self):
        """Test updating cat availability"""
        data = {"is_available": False}
        response = self.client.patch(self.detail_url, data, format="json")
        self.cat.refresh_from_db()
        self.assertEqual(self.cat.is_available, True)


class MissionTest(APITestCase):
    def setUp(self):
        self.assigned_cat = Cat.objects.create(
            name="Pipa", breed="Persian", years_of_experience=3, salary=100)
        self.unassigned_mission = Mission.objects.create()
        Target.objects.create(
            mission=self.unassigned_mission,
            name="Target 1",
            country="Catoria",
            notes="Todo add notes",
            is_complete=False
        )
        self.assigned_mission_incomplete = Mission.objects.create(
            cat=self.assigned_cat)
        Target.objects.create(
            mission=self.assigned_mission_incomplete,
            name="Target 2",
            country="Moldova",
            notes="Drink moldovian wine",
            is_complete=False
        )
        Target.objects.create(
            mission=self.assigned_mission_incomplete,
            name="Target 3",
            country="Romania",
            notes="Drunkula",
            is_complete=True
        )
        self.free_cat = Cat.objects.create(
            name="Biba", breed="Abyssinian", years_of_experience=4, salary=144)
        self.mission_completed = Mission.objects.create(
            cat=self.free_cat,
            is_complete=True
        )
        Target.objects.create(
            mission=self.mission_completed,
            name="Target 4",
            country="Zambia",
            notes="WTF am i doin here",
            is_complete=True
        )
        self.list_url = reverse('mission-list')
        self.create_url = reverse('mission-list')

    def test_can_create_valid_mission_without_cat_assigned(self):
        data = {
            "targets": [
                {
                    "name": "Target Alpha",
                    "country": "Germany",
                    "notes": "Eat all kebabs"
                },
                {
                    "name": "T2",
                    "country": "France",
                }
            ]
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_can_create_valid_mission_with_cat_assigned(self):
        data = {
            "cat": self.free_cat.pk,
            "targets": [
                {
                    "name": "target alpha",
                    "country": "germany",
                    "notes": "eat all kebabs"
                },
                {
                    "name": "t2",
                    "country": "france",
                }
            ]
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_cannot_create_mission_without_targets(self):
        data = {
            "cat": self.free_cat.pk
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_cannot_create_mission_with_targets_over_limit(self):
        data = {
            "cat": self.free_cat.pk,
            "targets": [
                {
                    "name": "target alpha",
                    "country": "germany",
                    "notes": "eat all kebabs"
                },
                {
                    "name": "t2",
                    "country": "france",
                },
                {
                    "name": "t3",
                    "country": "Bolivia"
                },
                {
                    "name": "t4",
                    "contry": "Greece",
                    "notes": "Eat all pitas"
                }
            ]
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_cannot_create_mission_with_cat_already_assigned(self):
        data = {
            "cat": self.assigned_cat.pk,
            "targets": [
                {
                    "name": "Target Alpha",
                    "country": "Germany",
                    "notes": "Eat all kebabs"
                },
            ]
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_can_delete_unassigned_mission(self):
        delete_url = reverse(
            "mission-detail", kwargs={"pk": self.unassigned_mission.pk})
        response = self.client.delete(delete_url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_cannot_delete_assigned_mission(self):
        delete_url = reverse(
            "mission-detail", kwargs={"pk": self.assigned_mission_incomplete.pk})
        response = self.client.delete(delete_url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_can_assign_available_cat_to_unassigned_mission(self):
        patch_url = reverse(
            "mission-detail", kwargs={"pk": self.unassigned_mission.pk})
        assign_data = {
            "cat": self.free_cat.pk
        }
        response = self.client.patch(patch_url, assign_data, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.unassigned_mission.refresh_from_db()
        self.assertEqual(self.unassigned_mission.cat, self.free_cat)

    def test_cannot_assign_busy_cat_to_unassigned_mission(self):
        patch_url = reverse(
            "mission-detail", kwargs={"pk": self.unassigned_mission.pk})
        assign_data = {
            "cat": self.assigned_cat.pk
        }
        response = self.client.patch(patch_url, assign_data, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.unassigned_mission.refresh_from_db()
        self.assertIsNone(self.unassigned_mission.cat)

    def test_cannot_assign_available_cat_to_assigned_mission(self):
        patch_url = reverse(
            "mission-detail", kwargs={"pk": self.assigned_mission_incomplete.pk})
        assign_data = {
            "cat": self.free_cat.pk
        }
        response = self.client.patch(patch_url, assign_data, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assigned_mission_incomplete.refresh_from_db()
        self.assertEqual(self.assigned_mission_incomplete.cat,
                         self.assigned_cat)

    def test_cannot_unassign_cat_from_mission(self):
        patch_url = reverse(
            "mission-detail", kwargs={"pk": self.assigned_mission_incomplete.pk})
        assign_data = {
            "cat": None
        }
        response = self.client.patch(patch_url, assign_data, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_list_missions(self):
        response = self.client.get(self.list_url, format="json")
        self.assertEqual(3, len(response.json()))

    def test_get_single_mission(self):
        get_url = reverse("mission-detail",
                          kwargs={"pk": self.assigned_mission_incomplete.pk})
        response = self.client.get(get_url, format="json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.assigned_mission_incomplete.pk,
                         response.json()["id"])
        self.assertEqual(self.assigned_mission_incomplete.cat.pk,
                         response.json()["cat"])
        self.assertEqual(
            self.assigned_mission_incomplete.is_complete, response.json()["is_complete"])
        self.assertEqual(self.assigned_mission_incomplete.targets.count(), len(
            response.json()["targets"]))

    def test_can_mark_mission_target_completed(self):
        mission = Mission.objects.create(cat=self.free_cat, is_complete=False)
        target = Target.objects.create(
            mission=mission, name="Eliminate everyone", country="russia", notes="Hello", is_complete=False)
        data = {
            "is_complete": True
        }
        patch_url = reverse("mission-target-detail",
                            kwargs={'mission_pk': mission.pk, 'pk': target.pk})
        response = self.client.patch(patch_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertEqual(target.is_complete, True)

    def test_last_target_completion_marks_mission_completion_and_makes_cat_available(self):
        mission = Mission.objects.create(cat=self.free_cat, is_complete=False)
        target = Target.objects.create(
            mission=mission, name="Eliminate everyone", country="rashka", notes="Hello", is_complete=False)

        data = {
            "is_complete": True
        }
        patch_url = reverse("mission-target-detail",
                            kwargs={'mission_pk': mission.pk, 'pk': target.pk})
        response = self.client.patch(patch_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        mission.refresh_from_db()
        self.free_cat.refresh_from_db()
        self.assertTrue(target.is_complete)
        self.assertTrue(mission.is_complete)
        self.assertTrue(self.free_cat.is_available)

    def test_can_update_mission_target_notes_when_not_finished(self):
        mission = Mission.objects.create(cat=self.free_cat, is_complete=False)
        target = Target.objects.create(
            mission=mission, name="Eliminate everyone", country="russia", notes="Hello", is_complete=False)
        data = {
            "notes": "Glad to do that"
        }
        patch_url = reverse("mission-target-detail",
                            kwargs={'mission_pk': mission.pk, 'pk': target.pk})
        response = self.client.patch(patch_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertEqual(target.notes, "Glad to do that")

    def test_cannot_update_mission_target_notes_when_finished(self):
        data = {
            "notes": "Updated Note"
        }
        patch_url = reverse("mission-target-detail",
                            kwargs={'mission_pk': self.mission_completed.pk, 'pk': self.mission_completed.targets.first().pk})
        response = self.client.patch(patch_url, data, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_cannot_mark_mission_target_unfinished_after_completion(self):
        data = {
            "is_complete": False
        }
        first_target = self.mission_completed.targets.first()
        patch_url = reverse("mission-target-detail",
                            kwargs={'mission_pk': self.mission_completed.pk, 'pk': first_target.pk})
        response = self.client.patch(patch_url, data, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        first_target.refresh_from_db()
        self.assertTrue(first_target.is_complete)
