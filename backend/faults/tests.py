from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import StudentProfile, User
from organizations.models import Organization, OrganizationManager, OrganizationMembership

from .models import MaintenanceRating, MaintenanceRequest


def make_user(username, role, **extra):
    return User.objects.create_user(
        username=username,
        password=username,
        role=role,
        **extra,
    )


def make_student(username, room_number=""):
    user = make_user(username, User.Role.STUDENT)
    StudentProfile.objects.create(
        user=user,
        student_number=username,
        is_dorm_resident=bool(room_number),
        dormitory_name="خوابگاه الف" if room_number else "",
        building="A" if room_number else "",
        room_number=room_number,
    )
    return user


class FaultTestCase(APITestCase):
    """داده مشترک: دو سازمان، مدیر، دانشجو و مسئولین تأسیسات/اینترنت."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="root", password="root", role=User.Role.MANAGER
        )

        self.manager = make_user("manager1", User.Role.MANAGER)
        self.dorm = Organization.objects.create(name="خوابگاه الف")
        OrganizationManager.objects.create(organization=self.dorm, manager=self.manager)

        self.other_manager = make_user("manager2", User.Role.MANAGER)
        self.other_dorm = Organization.objects.create(name="خوابگاه ب")
        OrganizationManager.objects.create(
            organization=self.other_dorm, manager=self.other_manager
        )

        self.student = make_student("4011111", room_number="9")
        OrganizationMembership.objects.create(organization=self.dorm, user=self.student)

        self.other_student = make_student("4022222", room_number="3")
        OrganizationMembership.objects.create(
            organization=self.other_dorm, user=self.other_student
        )

        # مسئولین همین سازمان
        self.facilities = make_user("tech1", User.Role.FACILITIES)
        OrganizationMembership.objects.create(
            organization=self.dorm,
            user=self.facilities,
            role=OrganizationMembership.Role.FACILITIES,
        )
        self.internet = make_user("net1", User.Role.INTERNET)
        OrganizationMembership.objects.create(
            organization=self.dorm,
            user=self.internet,
            role=OrganizationMembership.Role.INTERNET,
        )

        self.list_url = reverse("faults:maintenance-request-list-create")
        self.org_url = reverse(
            "faults:organization-maintenance-requests",
            kwargs={"organization_id": self.dorm.pk},
        )

    def detail_url(self, request_obj):
        return reverse(
            "faults:organization-maintenance-request-detail",
            kwargs={"organization_id": self.dorm.pk, "pk": request_obj.pk},
        )

    def action_url(self, request_obj):
        return reverse(
            "faults:organization-maintenance-request-updates",
            kwargs={"organization_id": self.dorm.pk, "pk": request_obj.pk},
        )

    def rate_url(self, request_obj):
        return reverse(
            "faults:organization-maintenance-request-rate",
            kwargs={"organization_id": self.dorm.pk, "pk": request_obj.pk},
        )

    def make_request(self, **kwargs):
        data = {
            "organization": self.dorm,
            "reporter": self.student,
            "title": "نشتی آب",
            "room_number": "9",
            "category": MaintenanceRequest.Category.FACILITIES,
        }
        data.update(kwargs)
        maintenance_request = MaintenanceRequest.objects.create(**data)
        maintenance_request.add_update(
            author=maintenance_request.reporter,
            note="ثبت اعلام خرابی",
        )
        return maintenance_request


class CreateFaultTests(FaultTestCase):

    def test_student_can_create_with_category_and_profile_room(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            self.list_url,
            {"organization": self.dorm.pk, "title": "لامپ خراب", "category": "repairs"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = MaintenanceRequest.objects.get(pk=response.data["id"])
        self.assertEqual(created.category, MaintenanceRequest.Category.REPAIRS)
        self.assertEqual(created.room_number, "9")
        self.assertEqual(created.status, MaintenanceRequest.Status.SUBMITTED)
        self.assertEqual(created.updates.count(), 1)

    def test_category_is_required(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            self.list_url,
            {"organization": self.dorm.pk, "title": "بدون دسته"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category", response.data)

    def test_non_member_cannot_create(self):
        self.client.force_authenticate(user=self.other_student)

        response = self.client.post(
            self.list_url,
            {"organization": self.dorm.pk, "title": "خرابی", "category": "repairs"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inside_organization_url(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            self.org_url,
            {"title": "خرابی اینترنت", "category": "internet"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["organization"], self.dorm.pk)
        self.assertEqual(response.data["category"], "internet")

    def test_anonymous_is_rejected(self):
        response = self.client.post(self.list_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StudentListTests(FaultTestCase):

    def test_student_only_sees_own_requests(self):
        self.make_request(title="مال من")
        self.make_request(
            organization=self.other_dorm,
            reporter=self.other_student,
            title="مال دیگری",
            room_number="3",
        )

        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item["title"] for item in response.data["results"]]
        self.assertEqual(titles, ["مال من"])

    def test_room_number_ordering_is_numeric(self):
        for room in ("9", "10", "2"):
            self.make_request(title=f"اتاق {room}", room_number=room)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(f"{self.list_url}?ordering=room_number")

        rooms = [item["room_number"] for item in response.data["results"]]
        self.assertEqual(rooms, ["2", "9", "10"])

    def test_filter_by_status(self):
        self.make_request(title="باز")
        self.make_request(title="بسته", status=MaintenanceRequest.Status.RESOLVED)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(f"{self.list_url}?status=resolved")

        titles = [item["title"] for item in response.data["results"]]
        self.assertEqual(titles, ["بسته"])


class ManagerAndStaffListTests(FaultTestCase):

    def test_manager_sees_all_requests_and_can_filter(self):
        self.make_request(title="تأسیسات", category="facilities")
        self.make_request(title="اینترنت", category="internet")
        self.make_request(title="تعمیرات", category="repairs")

        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.org_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

        response = self.client.get(f"{self.org_url}?category=internet")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "اینترنت")

    def test_other_manager_and_student_are_forbidden(self):
        self.client.force_authenticate(user=self.other_manager)
        self.assertEqual(
            self.client.get(self.org_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.client.force_authenticate(user=self.student)
        self.assertEqual(
            self.client.get(self.org_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_each_staff_sees_only_own_category(self):
        self.make_request(title="تأسیسات", category="facilities")
        self.make_request(title="اینترنت", category="internet")

        self.client.force_authenticate(user=self.facilities)
        facilities_response = self.client.get(self.org_url)
        self.assertEqual(
            [item["title"] for item in facilities_response.data["results"]],
            ["تأسیسات"],
        )

        self.client.force_authenticate(user=self.internet)
        internet_response = self.client.get(self.org_url)
        self.assertEqual(
            [item["title"] for item in internet_response.data["results"]],
            ["اینترنت"],
        )

    def test_system_admin_sees_requests(self):
        self.make_request()
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.org_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


class DetailAndActionTests(FaultTestCase):

    def setUp(self):
        super().setUp()
        self.request_obj = self.make_request()

    def test_reporter_sees_detail_with_timeline(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_url(self.request_obj))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_number"], "4011111")
        self.assertEqual(len(response.data["updates"]), 1)

    def test_other_student_cannot_view_detail(self):
        self.client.force_authenticate(user=self.other_student)
        response = self.client.get(self.detail_url(self.request_obj))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_patch_sets_resolved_at_and_timeline(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.patch(
            self.detail_url(self.request_obj),
            {"status": "resolved", "manager_note": "لوله تعویض شد"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.status, MaintenanceRequest.Status.RESOLVED)
        self.assertIsNotNone(self.request_obj.resolved_at)
        self.assertEqual(self.request_obj.updates.count(), 2)
        self.assertEqual(self.request_obj.updates.last().author, self.manager)

    def test_reporter_cannot_patch(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.patch(
            self.detail_url(self.request_obj),
            {"status": "resolved"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_assign_staff_member(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            self.action_url(self.request_obj),
            {
                "new_status": "in_progress",
                "assigned_to_id": self.facilities.pk,
                "comment": "به مسئول تأسیسات ارجاع شد",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.assigned_to, self.facilities)
        self.assertEqual(self.request_obj.status, MaintenanceRequest.Status.IN_PROGRESS)

    def test_manager_cannot_assign_student(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            self.action_url(self.request_obj),
            {"assigned_to_id": self.student.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_can_resolve_own_category(self):
        self.client.force_authenticate(user=self.facilities)

        response = self.client.post(
            self.action_url(self.request_obj),
            {"new_status": "resolved", "comment": "شیر آب تعویض شد"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.status, MaintenanceRequest.Status.RESOLVED)
        self.assertIsNotNone(self.request_obj.resolved_at)

    def test_staff_cannot_change_category_or_assign(self):
        self.client.force_authenticate(user=self.facilities)

        response = self.client.post(
            self.action_url(self.request_obj),
            {"category": "internet"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            self.action_url(self.request_obj),
            {"assigned_to_id": self.internet.pk},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_of_other_category_cannot_handle_request(self):
        another_facilities_request = self.make_request(category="repairs")
        self.client.force_authenticate(user=self.internet)

        response = self.client.post(
            self.action_url(another_facilities_request),
            {"new_status": "resolved"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RatingTests(FaultTestCase):

    def setUp(self):
        super().setUp()
        self.request_obj = self.make_request(status=MaintenanceRequest.Status.RESOLVED)

    def test_reporter_can_rate_resolved_request_once(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            self.rate_url(self.request_obj),
            {"score": 5, "comment": "سریع بود"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            MaintenanceRating.objects.filter(request=self.request_obj, score=5).exists()
        )

        response = self.client.post(
            self.rate_url(self.request_obj),
            {"score": 4},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_requires_resolved_status(self):
        open_request = self.make_request()
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            self.rate_url(open_request),
            {"score": 4},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_student_cannot_rate(self):
        self.client.force_authenticate(user=self.other_student)
        response = self.client.post(
            self.rate_url(self.request_obj),
            {"score": 5},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CancelAndNoteTests(FaultTestCase):

    def test_reporter_can_cancel_and_notes_stop(self):
        maintenance_request = self.make_request()
        cancel_url = reverse(
            "faults:maintenance-request-cancel",
            kwargs={"pk": maintenance_request.pk},
        )
        notes_url = reverse(
            "faults:maintenance-request-updates",
            kwargs={"pk": maintenance_request.pk},
        )

        self.client.force_authenticate(user=self.student)
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        maintenance_request.refresh_from_db()
        self.assertEqual(maintenance_request.status, MaintenanceRequest.Status.CANCELLED)
        self.assertEqual(maintenance_request.updates.count(), 2)

        response = self.client.post(notes_url, {"note": "بعد از لغو"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_student_cannot_cancel(self):
        maintenance_request = self.make_request()
        cancel_url = reverse(
            "faults:maintenance-request-cancel",
            kwargs={"pk": maintenance_request.pk},
        )

        self.client.force_authenticate(user=self.other_student)
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_personal_detail_and_timeline_dates(self):
        maintenance_request = self.make_request()
        old = timezone.now() - timedelta(days=1)
        MaintenanceRequest.objects.filter(pk=maintenance_request.pk).update(created_at=old)

        self.client.force_authenticate(user=self.student)
        detail_url = reverse(
            "faults:maintenance-request-detail",
            kwargs={"pk": maintenance_request.pk},
        )
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], maintenance_request.title)
