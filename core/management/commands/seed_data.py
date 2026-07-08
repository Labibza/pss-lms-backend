from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Comment, Course, CourseContent, CourseMember


class Command(BaseCommand):
    help = "Membuat data dummy awal untuk aplikasi LMS."

    def create_user(self, username, email, password, is_staff=False, is_superuser=False):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            }
        )

        user.email = email
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(password)
        user.save()

        return user, created

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Membuat seed data LMS...")

        admin, _ = self.create_user(
            username="admin_lms",
            email="admin_lms@example.com",
            password="admin12345",
            is_staff=True,
            is_superuser=True,
        )

        teacher1, _ = self.create_user(
            username="teacher_django",
            email="teacher_django@example.com",
            password="teacher12345",
            is_staff=False,
        )

        teacher2, _ = self.create_user(
            username="teacher_python",
            email="teacher_python@example.com",
            password="teacher12345",
            is_staff=False,
        )

        assistant1, _ = self.create_user(
            username="assistant_lms",
            email="assistant_lms@example.com",
            password="assistant12345",
            is_staff=False,
        )

        student1, _ = self.create_user(
            username="student_lms_1",
            email="student1@example.com",
            password="student12345",
            is_staff=False,
        )

        student2, _ = self.create_user(
            username="student_lms_2",
            email="student2@example.com",
            password="student12345",
            is_staff=False,
        )

        course_django, _ = Course.objects.update_or_create(
            name="Dasar Django",
            defaults={
                "description": "Course pengenalan Django untuk membangun aplikasi web backend.",
                "price": Decimal("100000"),
                "teacher": teacher1,
            }
        )

        course_python, _ = Course.objects.update_or_create(
            name="Python Dasar",
            defaults={
                "description": "Course dasar pemrograman Python untuk pemula.",
                "price": Decimal("75000"),
                "teacher": teacher2,
            }
        )

        course_database, _ = Course.objects.update_or_create(
            name="Database PostgreSQL",
            defaults={
                "description": "Course pengenalan database relasional menggunakan PostgreSQL.",
                "price": Decimal("120000"),
                "teacher": teacher1,
            }
        )

        CourseMember.objects.update_or_create(
            course=course_django,
            user=assistant1,
            defaults={
                "role": CourseMember.ROLE_ASSISTANT,
            }
        )

        CourseMember.objects.update_or_create(
            course=course_django,
            user=student1,
            defaults={
                "role": CourseMember.ROLE_STUDENT,
            }
        )

        CourseMember.objects.update_or_create(
            course=course_python,
            user=student1,
            defaults={
                "role": CourseMember.ROLE_STUDENT,
            }
        )

        CourseMember.objects.update_or_create(
            course=course_python,
            user=student2,
            defaults={
                "role": CourseMember.ROLE_STUDENT,
            }
        )

        CourseMember.objects.update_or_create(
            course=course_database,
            user=student2,
            defaults={
                "role": CourseMember.ROLE_STUDENT,
            }
        )

        django_content_1, _ = CourseContent.objects.update_or_create(
            course=course_django,
            title="Pengenalan Django",
            defaults={
                "parent": None,
                "content_type": CourseContent.TYPE_TEXT,
                "text_content": "Django adalah framework web berbasis Python yang menyediakan ORM, routing, template, dan admin site.",
                "order_number": 1,
            }
        )

        django_content_2, _ = CourseContent.objects.update_or_create(
            course=course_django,
            title="Model dan Migration",
            defaults={
                "parent": None,
                "content_type": CourseContent.TYPE_TEXT,
                "text_content": "Model digunakan untuk mendefinisikan struktur data, sedangkan migration digunakan untuk menerapkan perubahan ke database.",
                "order_number": 2,
            }
        )

        CourseContent.objects.update_or_create(
            course=course_django,
            parent=django_content_2,
            title="Contoh Relasi ForeignKey",
            defaults={
                "content_type": CourseContent.TYPE_TEXT,
                "text_content": "ForeignKey digunakan untuk membuat relasi one-to-many antar model.",
                "order_number": 1,
            }
        )

        python_content_1, _ = CourseContent.objects.update_or_create(
            course=course_python,
            title="Pengenalan Python",
            defaults={
                "parent": None,
                "content_type": CourseContent.TYPE_TEXT,
                "text_content": "Python adalah bahasa pemrograman tingkat tinggi yang mudah dipelajari.",
                "order_number": 1,
            }
        )

        database_content_1, _ = CourseContent.objects.update_or_create(
            course=course_database,
            title="Pengenalan Database Relasional",
            defaults={
                "parent": None,
                "content_type": CourseContent.TYPE_TEXT,
                "text_content": "Database relasional menyimpan data dalam bentuk tabel yang saling berhubungan.",
                "order_number": 1,
            }
        )

        django_student_member = CourseMember.objects.get(
            course=course_django,
            user=student1,
        )

        python_student_member = CourseMember.objects.get(
            course=course_python,
            user=student2,
        )

        Comment.objects.get_or_create(
            content=django_content_1,
            member=django_student_member,
            defaults={
                "text": "Materi pengenalan Django sangat mudah dipahami."
            }
        )

        Comment.objects.get_or_create(
            content=python_content_1,
            member=python_student_member,
            defaults={
                "text": "Materi Python cocok untuk pemula."
            }
        )

        self.stdout.write(self.style.SUCCESS("Seed data berhasil dibuat."))
        self.stdout.write("")
        self.stdout.write("Akun yang dapat digunakan:")
        self.stdout.write("Admin       : admin_lms / admin12345")
        self.stdout.write("Teacher 1   : teacher_django / teacher12345")
        self.stdout.write("Teacher 2   : teacher_python / teacher12345")
        self.stdout.write("Assistant   : assistant_lms / assistant12345")
        self.stdout.write("Student 1   : student_lms_1 / student12345")
        self.stdout.write("Student 2   : student_lms_2 / student12345")