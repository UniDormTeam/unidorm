from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import StudentProfile, User

from .models import Organization, OrganizationManager, OrganizationMembership


def make_manager(username):
    return User.objects.create_user(
        username=username,
        password=username,
        role=User.Role.MANAGER,
    )


class OrganizationTestCase(APITestCase):
    """داده مشترک تست‌های سازمان."""

    def setUp(self):
        self.manager = make_manager("manager1")
        self.other_manager = make_manager("manager2")

        self.organization = Organization.objects.create(name="خوابگاه الف")
        OrganizationManager.objects.create(
            organization=self.organization,
            manager=self.manager,
        )

        self.other_organization = Organization.objects.create(name="خوابگاه ب")
        OrganizationManager.objects.create(
            organization=self.other_organization,
            manager=self.other_manager,
        )

        self.list_url = reverse("organizations:organization-list-create")
        self.detail_url = reverse(
            "organizations:organization-detail",
            kwargs={"pk": self.organization.pk},
        )
        self.members_url = reverse(
            "organizations:organization-members",
            kwargs={"organization_id": self.organization.pk},
        )
        self.managers_url = reverse(
            "organizations:organization-managers",
            kwargs={"organization_id": self.organization.pk},
        )


class OrganizationCrudTests(OrganizationTestCase):

    def test_manager_can_create_organization_and_is_assigned(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            self.list_url,
            {"name": "خوابگاه جدید", "location": "کوی دانشگاه"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        organization = Organization.objects.get(pk=response.data["id"])
        self.assertTrue(
            OrganizationManager.objects.filter(
                organization=organization,
                manager=self.manager,
            ).exists()
        )
        self.assertEqual(response.data["my_role"], "manager")

    def test_manager_only_sees_own_organizations(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertEqual(names, ["خوابگاه الف"])

    def test_other_manager_cannot_edit_organization(self):
        self.client.force_authenticate(user=self.other_manager)

        response = self.client.patch(
            self.detail_url,
            {"description": "تغییر غیرمجاز"},
            format="json",
        )

        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )

    def test_organization_detail_has_stats(self):
        student = User.objects.create_user(
            username="4011111",
            password="x",
            role=User.Role.STUDENT,
        )
        OrganizationMembership.objects.create(
            organization=self.organization,
            user=student,
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stats"]["total_students"], 1)
        self.assertEqual(len(response.data["managers"]), 1)


class MemberManagementTests(OrganizationTestCase):

    def test_add_member_creates_account_and_profile(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            self.members_url,
            {
                "username": "401223344",
                "first_name": "امیر",
                "last_name": "حسینی",
                "membership_role": "student",
                "room_number": "305",
                "phone_number": "09191234567",
                "is_dorm_resident": True,
                "dormitory_name": "خوابگاه الف",
                "building": "A",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["account_status"], "CREATED_AND_ATTACHED")

        user = User.objects.get(username="401223344")
        self.assertEqual(user.role, User.Role.STUDENT)
        # رمز پیش‌فرض همان نام کاربری است
        self.assertTrue(user.check_password("401223344"))
        self.assertTrue(StudentProfile.objects.filter(user=user, room_number="305").exists())
        self.assertTrue(
            OrganizationMembership.objects.filter(
                organization=self.organization,
                user=user,
            ).exists()
        )

    def test_add_existing_student_attaches_without_duplicate_account(self):
        student = User.objects.create_user(
            username="401999999",
            password="x",
            role=User.Role.STUDENT,
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            self.members_url,
            {"username": "401999999", "membership_role": "student"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["account_status"], "EXISTING_ATTACHED")
        self.assertEqual(User.objects.filter(username="401999999").count(), 1)
        self.assertTrue(
            OrganizationMembership.objects.filter(
                organization=self.organization,
                user=student,
            ).exists()
        )

    def test_add_facilities_officer_creates_staff_account(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            self.members_url,
            {
                "username": "tech1",
                "first_name": "رضا",
                "membership_role": "facilities",
                "phone_number": "09120001122",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="tech1")
        self.assertEqual(user.role, User.Role.FACILITIES)
        membership = OrganizationMembership.objects.get(user=user)
        self.assertEqual(membership.role, OrganizationMembership.Role.FACILITIES)

    def test_duplicate_membership_is_rejected(self):
        student = User.objects.create_user(
            username="402000000",
            password="x",
            role=User.Role.STUDENT,
        )
        OrganizationMembership.objects.create(
            organization=self.organization,
            user=student,
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            self.members_url,
            {"username": "402000000", "membership_role": "student"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_cannot_add_members(self):
        student = User.objects.create_user(
            username="402111111",
            password="x",
            role=User.Role.STUDENT,
        )
        OrganizationMembership.objects.create(
            organization=self.organization,
            user=student,
        )

        self.client.force_authenticate(user=student)
        response = self.client.post(
            self.members_url,
            {"username": "402222222", "membership_role": "student"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_members_can_be_filtered_by_role(self):
        student = User.objects.create_user(
            username="403000001",
            password="x",
            role=User.Role.STUDENT,
        )
        staff = User.objects.create_user(
            username="403000002",
            password="x",
            role=User.Role.INTERNET,
        )
        OrganizationMembership.objects.create(
            organization=self.organization,
            user=student,
            role=OrganizationMembership.Role.STUDENT,
        )
        OrganizationMembership.objects.create(
            organization=self.organization,
            user=staff,
            role=OrganizationMembership.Role.INTERNET,
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.get(f"{self.members_url}?role=internet")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["username"], "403000002")

    def test_bulk_add_reports_success_and_errors(self):
        bulk_url = reverse(
            "organizations:organization-members-bulk",
            kwargs={"organization_id": self.organization.pk},
        )
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            bulk_url,
            {
                "members": [
                    {"username": "404000001", "membership_role": "student"},
                    {"username": "404000002", "membership_role": "student"},
                    # ردیف تکراری داخل همان درخواست
                    {"username": "404000001", "membership_role": "student"},
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["summary"]["total_processed"], 3)
        # ردیف تکراری باید رد شود و بقیه ثبت شوند
        self.assertEqual(response.data["summary"]["created"], 2)
        self.assertEqual(response.data["summary"]["failed_count"], 1)
        self.assertEqual(
            OrganizationMembership.objects.filter(
                organization=self.organization
            ).count(),
            2,
        )

    def test_import_students_from_csv(self):
        import_url = reverse(
            "organizations:organization-import-students",
            kwargs={"organization_id": self.organization.pk},
        )
        content = (
            "شماره دانشجویی,نام,نام خانوادگی,شماره اتاق\n"
            "405000001,مهدی,کریمی,101\n"
            "405000002,زهرا,احمدی,102\n"
        ).encode("utf-8")
        upload = SimpleUploadedFile("students.csv", content, content_type="text/csv")

        self.client.force_authenticate(user=self.manager)
        response = self.client.post(import_url, {"file": upload}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["summary"]["created"], 2)
        self.assertEqual(
            OrganizationMembership.objects.filter(
                organization=self.organization
            ).count(),
            2,
        )
        self.assertTrue(User.objects.filter(username="405000001").exists())


class ManagerAssignmentTests(OrganizationTestCase):

    def test_manager_can_assign_another_manager(self):
        third_manager = make_manager("manager3")
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            self.managers_url,
            {"manager": third_manager.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            OrganizationManager.objects.filter(
                organization=self.organization,
                manager=third_manager,
            ).exists()
        )

    def test_student_account_cannot_be_assigned_as_manager(self):
        student = User.objects.create_user(
            username="406000001",
            password="x",
            role=User.Role.STUDENT,
        )
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            self.managers_url,
            {"manager": student.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
