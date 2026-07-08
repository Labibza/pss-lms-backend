import os
import tempfile
from decimal import Decimal
from io import StringIO

from django.contrib.auth.models import AnonymousUser, User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Comment, Course, CourseContent, CourseMember
from core.services.import_csv_service import import_courses, import_members, import_users


TEST_ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]


class LMSBaseTest(TestCase):
    """
    Base test untuk menyiapkan data awal.
    Setiap test akan memakai database test terpisah milik Django.
    """

    def setUp(self):
        cache.clear()

        self.admin = User.objects.create_superuser(
            username="admin_test",
            email="admin@example.com",
            password="admin12345",
        )

        self.teacher = User.objects.create_user(
            username="teacher_test",
            email="teacher@example.com",
            password="teacher12345",
        )

        self.assistant = User.objects.create_user(
            username="assistant_test",
            email="assistant@example.com",
            password="assistant12345",
        )

        self.student = User.objects.create_user(
            username="student_test",
            email="student@example.com",
            password="student12345",
        )

        self.other_student = User.objects.create_user(
            username="other_student",
            email="other@example.com",
            password="student12345",
        )

        self.course = Course.objects.create(
            name="Dasar Django",
            description="Course pengenalan Django untuk pemula.",
            price=Decimal("100000.00"),
            teacher=self.teacher,
        )

        self.assistant_member = CourseMember.objects.create(
            course=self.course,
            user=self.assistant,
            role=CourseMember.ROLE_ASSISTANT,
        )

        self.student_member = CourseMember.objects.create(
            course=self.course,
            user=self.student,
            role=CourseMember.ROLE_STUDENT,
        )

        self.content = CourseContent.objects.create(
            course=self.course,
            parent=None,
            title="Pengenalan Django",
            content_type=CourseContent.TYPE_TEXT,
            text_content="Django adalah framework web berbasis Python.",
            order_number=1,
        )

        self.child_content = CourseContent.objects.create(
            course=self.course,
            parent=self.content,
            title="Instalasi Django",
            content_type=CourseContent.TYPE_TEXT,
            text_content="Django dapat diinstal menggunakan pip.",
            order_number=2,
        )


@override_settings(ALLOWED_HOSTS=TEST_ALLOWED_HOSTS)
class ModelAccessTest(LMSBaseTest):
    """
    Test untuk model, relasi, constraint, dan method akses.
    """

    def test_course_access_methods_for_admin(self):
        self.assertTrue(self.course.can_manage(self.admin))
        self.assertTrue(self.course.can_assist(self.admin))
        self.assertTrue(self.course.can_view(self.admin))

    def test_course_access_methods_for_teacher(self):
        self.assertTrue(self.course.can_manage(self.teacher))
        self.assertTrue(self.course.can_assist(self.teacher))
        self.assertTrue(self.course.can_view(self.teacher))

    def test_course_access_methods_for_assistant(self):
        self.assertFalse(self.course.can_manage(self.assistant))
        self.assertTrue(self.course.can_assist(self.assistant))
        self.assertTrue(self.course.can_view(self.assistant))

    def test_course_access_methods_for_student(self):
        self.assertFalse(self.course.can_manage(self.student))
        self.assertFalse(self.course.can_assist(self.student))
        self.assertTrue(self.course.can_view(self.student))
        self.assertTrue(self.course.is_member(self.student))

    def test_course_access_methods_for_non_member(self):
        self.assertFalse(self.course.can_manage(self.other_student))
        self.assertFalse(self.course.can_assist(self.other_student))
        self.assertFalse(self.course.can_view(self.other_student))
        self.assertFalse(self.course.is_member(self.other_student))

    def test_course_access_methods_for_anonymous_user(self):
        anonymous = AnonymousUser()

        self.assertFalse(self.course.can_manage(anonymous))
        self.assertFalse(self.course.can_assist(anonymous))
        self.assertFalse(self.course.can_view(anonymous))
        self.assertFalse(self.course.is_member(anonymous))

    def test_course_member_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CourseMember.objects.create(
                    course=self.course,
                    user=self.student,
                    role=CourseMember.ROLE_STUDENT,
                )

    def test_comment_valid_course_member(self):
        comment = Comment.objects.create(
            content=self.content,
            member=self.student_member,
            text="Materinya mudah dipahami.",
        )

        self.assertEqual(comment.content, self.content)
        self.assertEqual(comment.member, self.student_member)
        self.assertEqual(comment.text, "Materinya mudah dipahami.")

    def test_comment_invalid_course_member_rejected(self):
        other_course = Course.objects.create(
            name="Course Lain",
            description="Course lain untuk validasi.",
            price=Decimal("50000.00"),
            teacher=self.teacher,
        )

        other_content = CourseContent.objects.create(
            course=other_course,
            title="Konten Course Lain",
            content_type=CourseContent.TYPE_TEXT,
            text_content="Isi konten course lain.",
            order_number=1,
        )

        with self.assertRaises(ValidationError):
            Comment.objects.create(
                content=other_content,
                member=self.student_member,
                text="Komentar tidak valid.",
            )


@override_settings(ALLOWED_HOSTS=TEST_ALLOWED_HOSTS)
class WebViewTest(LMSBaseTest):
    """
    Test untuk halaman web berbasis template.
    """

    def test_home_page(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")
        self.assertContains(response, "Home LMS")
        self.assertContains(response, "Total Course")

    def test_user_list_page(self):
        response = self.client.get(reverse("user_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/user_list.html")
        self.assertContains(response, "Daftar User")
        self.assertContains(response, "teacher_test")

    def test_course_list_page(self):
        response = self.client.get(reverse("course_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/course_list.html")
        self.assertContains(response, "Daftar Course")
        self.assertContains(response, "Dasar Django")

    def test_course_list_filter(self):
        Course.objects.create(
            name="Python Dasar",
            description="Course Python.",
            price=Decimal("75000.00"),
            teacher=self.teacher,
        )

        response = self.client.get(
            reverse("course_list"),
            {
                "q": "Python",
                "per_page": 10,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Dasar")
        self.assertNotContains(response, "Dasar Django")

    def test_course_list_pagination(self):
        for number in range(1, 8):
            Course.objects.create(
                name=f"Course Tambahan {number}",
                description=f"Deskripsi course tambahan {number}.",
                price=Decimal("50000.00"),
                teacher=self.teacher,
            )

        response = self.client.get(
            reverse("course_list"),
            {
                "per_page": 5,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["page_obj"].has_other_pages())
        self.assertGreaterEqual(response.context["paginator"].num_pages, 2)

    def test_course_detail_public_can_open_but_cannot_view_content(self):
        response = self.client.get(
            reverse("course_detail", args=[self.course.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/course_detail.html")
        self.assertContains(response, "Dasar Django")
        self.assertContains(response, "Konten hanya dapat dilihat")

    def test_login_page(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/login.html")
        self.assertContains(response, "Login")

    def test_login_success_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "student_test",
                "password": "student12345",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_logout_get_not_allowed(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 405)

    def test_logout_post_success(self):
        self.client.force_login(self.student)

        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_dashboard_logged_in(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/dashboard.html")
        self.assertContains(response, "Course Diikuti")
        self.assertContains(response, "Komentar Saya")

    def test_my_courses_logged_in(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("my_courses"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/my_courses.html")
        self.assertContains(response, "Dasar Django")

    def test_join_course_requires_login(self):
        response = self.client.post(
            reverse("join_course", args=[self.course.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_student_can_join_course(self):
        self.client.force_login(self.other_student)

        response = self.client.post(
            reverse("join_course", args=[self.course.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CourseMember.objects.filter(
                course=self.course,
                user=self.other_student,
                role=CourseMember.ROLE_STUDENT,
            ).exists()
        )

    def test_teacher_cannot_join_own_course_as_student(self):
        self.client.force_login(self.teacher)

        response = self.client.post(
            reverse("join_course", args=[self.course.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            CourseMember.objects.filter(
                course=self.course,
                user=self.teacher,
            ).exists()
        )

    def test_content_detail_redirects_anonymous_to_login(self):
        response = self.client.get(
            reverse("course_content_detail", args=[self.content.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_content_detail_for_member(self):
        self.client.force_login(self.student)

        response = self.client.get(
            reverse("course_content_detail", args=[self.content.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/course_content_detail.html")
        self.assertContains(response, "Pengenalan Django")
        self.assertContains(response, "Django adalah framework web berbasis Python.")

    def test_content_detail_for_non_member_forbidden(self):
        self.client.force_login(self.other_student)

        response = self.client.get(
            reverse("course_content_detail", args=[self.content.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_add_comment_success(self):
        self.client.force_login(self.student)

        response = self.client.post(
            reverse("add_comment", args=[self.content.id]),
            {
                "text": "Komentar dari unit test.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Comment.objects.filter(
                content=self.content,
                member=self.student_member,
                text="Komentar dari unit test.",
            ).exists()
        )

    def test_add_comment_non_member_forbidden(self):
        self.client.force_login(self.other_student)

        response = self.client.post(
            reverse("add_comment", args=[self.content.id]),
            {
                "text": "Komentar tidak boleh masuk.",
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_edit_content_for_student_forbidden(self):
        self.client.force_login(self.student)

        response = self.client.get(
            reverse("edit_content", args=[self.content.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_edit_content_for_assistant_allowed(self):
        self.client.force_login(self.assistant)

        response = self.client.get(
            reverse("edit_content", args=[self.content.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/edit_content.html")
        self.assertContains(response, "Edit Konten")

    def test_edit_content_success_by_assistant(self):
        self.client.force_login(self.assistant)

        response = self.client.post(
            reverse("edit_content", args=[self.content.id]),
            {
                "parent": "",
                "title": "Pengenalan Django Updated",
                "content_type": CourseContent.TYPE_TEXT,
                "text_content": "Materi sudah diperbarui.",
                "video_url": "",
                "order_number": 3,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.content.refresh_from_db()

        self.assertEqual(self.content.title, "Pengenalan Django Updated")
        self.assertEqual(self.content.text_content, "Materi sudah diperbarui.")

    def test_course_stat_page(self):
        response = self.client.get(reverse("course_stat"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/course_stat.html")
        self.assertContains(response, "Statistik Course")

    def test_user_statistics_page(self):
        response = self.client.get(reverse("user_statistics"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/user_statistics.html")
        self.assertContains(response, "Statistik User")


@override_settings(ALLOWED_HOSTS=TEST_ALLOWED_HOSTS)
class APITest(LMSBaseTest):
    """
    Test untuk endpoint API JSON.
    """

    def setUp(self):
        super().setUp()
        cache.clear()

    def test_api_courses_json(self):
        response = self.client.get(
            reverse("api_courses"),
            REMOTE_ADDR="10.0.0.1",
        )

        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertEqual(payload["message"], "Daftar course berhasil diambil.")
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["data"][0]["name"], "Dasar Django")
        self.assertIn("pagination", payload)

    def test_api_course_detail_json(self):
        response = self.client.get(
            reverse("api_course_detail", args=[self.course.id]),
            REMOTE_ADDR="10.0.0.2",
        )

        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertEqual(payload["message"], "Detail course berhasil diambil.")
        self.assertEqual(payload["data"]["name"], "Dasar Django")
        self.assertEqual(len(payload["data"]["contents"]), 2)

    def test_api_filter_and_pagination(self):
        Course.objects.create(
            name="Python Dasar",
            description="Course Python untuk pemula.",
            price=Decimal("75000.00"),
            teacher=self.teacher,
        )

        response = self.client.get(
            reverse("api_courses"),
            {
                "q": "Python",
                "page": 1,
                "per_page": 1,
            },
            REMOTE_ADDR="10.0.0.3",
        )

        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertEqual(payload["pagination"]["current_page"], 1)
        self.assertEqual(payload["pagination"]["per_page"], 1)
        self.assertEqual(payload["data"][0]["name"], "Python Dasar")

    def test_api_rate_limit_returns_429(self):
        cache.clear()

        url = reverse("api_courses")

        for _ in range(30):
            response = self.client.get(
                url,
                REMOTE_ADDR="10.0.0.99",
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.get(
            url,
            REMOTE_ADDR="10.0.0.99",
        )

        self.assertEqual(response.status_code, 429)

        payload = response.json()

        self.assertEqual(payload["message"], "Terlalu banyak request. Silakan coba lagi nanti.")
        self.assertEqual(payload["detail"]["limit"], 30)


@override_settings(ALLOWED_HOSTS=TEST_ALLOWED_HOSTS)
class ImportCSVServiceTest(LMSBaseTest):
    """
    Test untuk service import CSV.
    """

    def test_import_users_service(self):
        csv_data = StringIO(
            "username,email,password,is_staff\n"
            "csv_user,csv_user@example.com,password123,false\n"
            "csv_admin,csv_admin@example.com,admin123,true\n"
        )

        result = import_users(csv_data)

        self.assertEqual(result["created"], 2)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["skipped"], 0)

        csv_user = User.objects.get(username="csv_user")
        csv_admin = User.objects.get(username="csv_admin")

        self.assertTrue(csv_user.check_password("password123"))
        self.assertTrue(csv_admin.is_staff)

    def test_import_courses_service(self):
        csv_data = StringIO(
            "name,description,price,teacher_username\n"
            "Course CSV Test,Course hasil test,150000,teacher_test\n"
        )

        result = import_courses(csv_data)

        self.assertEqual(result["created"], 1)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["skipped"], 0)

        course = Course.objects.get(name="Course CSV Test")

        self.assertEqual(course.teacher, self.teacher)
        self.assertEqual(course.price, Decimal("150000"))

    def test_import_courses_skips_missing_teacher(self):
        csv_data = StringIO(
            "name,description,price,teacher_username\n"
            "Course Tanpa Teacher,Course gagal,150000,teacher_ghost\n"
        )

        result = import_courses(csv_data)

        self.assertEqual(result["created"], 0)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["skipped"], 1)
        self.assertIn("tidak ditemukan", result["errors"][0])

    def test_import_members_service(self):
        new_user = User.objects.create_user(
            username="csv_student",
            email="csv_student@example.com",
            password="student12345",
        )

        csv_data = StringIO(
            "course_name,username,role\n"
            "Dasar Django,csv_student,ast\n"
        )

        result = import_members(csv_data)

        self.assertEqual(result["created"], 1)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["skipped"], 0)

        member = CourseMember.objects.get(
            course=self.course,
            user=new_user,
        )

        self.assertEqual(member.role, CourseMember.ROLE_ASSISTANT)

    def test_import_members_skips_invalid_role(self):
        csv_data = StringIO(
            "course_name,username,role\n"
            "Dasar Django,student_test,invalid_role\n"
        )

        result = import_members(csv_data)

        self.assertEqual(result["created"], 0)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["skipped"], 1)
        self.assertIn("role tidak valid", result["errors"][0])


@override_settings(ALLOWED_HOSTS=TEST_ALLOWED_HOSTS)
class UploadCSVViewTest(LMSBaseTest):
    """
    Test untuk halaman upload CSV.
    """

    def test_upload_csv_requires_staff(self):
        response = self.client.get(reverse("upload_csv"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_non_staff_cannot_access_upload_csv(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("upload_csv"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_staff_can_open_upload_csv_page(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("upload_csv"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/upload_csv.html")
        self.assertContains(response, "Import CSV")

    def test_staff_can_upload_user_csv(self):
        self.client.force_login(self.admin)

        csv_file = SimpleUploadedFile(
            "users.csv",
            (
                b"username,email,password,is_staff\n"
                b"upload_user,upload_user@example.com,password123,false\n"
            ),
            content_type="text/csv",
        )

        response = self.client.post(
            reverse("upload_csv"),
            {
                "import_type": "users",
                "csv_file": csv_file,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Import user selesai.")
        self.assertTrue(User.objects.filter(username="upload_user").exists())


@override_settings(ALLOWED_HOSTS=TEST_ALLOWED_HOSTS)
class ManagementCommandTest(LMSBaseTest):
    """
    Test untuk custom management command.
    """

    def test_import_courses_csv_command(self):
        csv_content = (
            "name,description,price,teacher_username\n"
            "Command Course,Course dari command,175000,teacher_test\n"
        )

        temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            encoding="utf-8",
            newline="",
        )

        try:
            temp_file.write(csv_content)
            temp_file.close()

            output = StringIO()

            call_command(
                "import_courses_csv",
                temp_file.name,
                stdout=output,
            )

            self.assertIn("Import course selesai.", output.getvalue())
            self.assertTrue(
                Course.objects.filter(name="Command Course").exists()
            )

        finally:
            os.unlink(temp_file.name)

    def test_seed_data_command(self):
        output = StringIO()

        call_command(
            "seed_data",
            stdout=output,
        )

        self.assertIn("Seed data berhasil dibuat.", output.getvalue())
        self.assertTrue(User.objects.filter(username="admin_lms").exists())
        self.assertTrue(Course.objects.filter(name="Python Dasar").exists())