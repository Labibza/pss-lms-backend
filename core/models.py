from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Course(models.Model):
    """
    Model Course digunakan untuk menyimpan data course atau mata kuliah.
    Satu course memiliki satu teacher/pengajar.
    Satu teacher dapat mengajar banyak course.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    image = models.ImageField(upload_to="courses/", blank=True, null=True)

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="teaching_courses"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.name

    def is_member(self, user):
        """
        Mengecek apakah user adalah member pada course ini.
        """
        if not user or not user.is_authenticated:
            return False

        return self.memberships.filter(user=user).exists()

    def can_manage(self, user):
        """
        Mengecek apakah user boleh mengelola course.
        Yang boleh manage:
        1. Admin/staff
        2. Teacher dari course tersebut
        """
        if not user or not user.is_authenticated:
            return False

        return user.is_staff or self.teacher_id == user.id

    def can_assist(self, user):
        """
        Mengecek apakah user boleh membantu mengedit konten.
        Yang boleh assist:
        1. Admin/staff
        2. Teacher
        3. Member dengan role asisten
        """
        if not user or not user.is_authenticated:
            return False

        if self.can_manage(user):
            return True

        return self.memberships.filter(
            user=user,
            role=CourseMember.ROLE_ASSISTANT
        ).exists()

    def can_view(self, user):
        """
        Mengecek apakah user boleh melihat konten course.
        Yang boleh melihat:
        1. Admin/staff
        2. Teacher
        3. Asisten
        4. Siswa/member course
        """
        if not user or not user.is_authenticated:
            return False

        return self.can_assist(user) or self.is_member(user)


class CourseMember(models.Model):
    """
    Model CourseMember digunakan untuk menghubungkan user dengan course.
    Role:
    - std = student/siswa
    - ast = assistant/asisten
    """

    ROLE_STUDENT = "std"
    ROLE_ASSISTANT = "ast"

    ROLE_CHOICES = [
        (ROLE_STUDENT, "Student"),
        (ROLE_ASSISTANT, "Assistant"),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="course_memberships"
    )

    role = models.CharField(
        max_length=3,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "user")
        ordering = ["course__name", "user__username"]
        verbose_name = "Course Member"
        verbose_name_plural = "Course Members"

    def __str__(self):
        return f"{self.user.username} - {self.course.name} ({self.get_role_display()})"


class CourseContent(models.Model):
    """
    Model CourseContent digunakan untuk menyimpan materi pembelajaran.
    Konten dapat berupa teks, video, atau file.
    Field parent digunakan untuk membuat struktur konten bertingkat.
    """

    TYPE_TEXT = "text"
    TYPE_VIDEO = "video"
    TYPE_FILE = "file"

    CONTENT_TYPE_CHOICES = [
        (TYPE_TEXT, "Text"),
        (TYPE_VIDEO, "Video"),
        (TYPE_FILE, "File"),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="contents"
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True
    )

    title = models.CharField(max_length=255)

    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        default=TYPE_TEXT
    )

    text_content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    file = models.FileField(upload_to="contents/files/", blank=True, null=True)

    order_number = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["course__name", "parent_id", "order_number", "title"]
        verbose_name = "Course Content"
        verbose_name_plural = "Course Contents"

    def __str__(self):
        return f"{self.course.name} - {self.title}"

    def is_root_content(self):
        """
        Mengecek apakah konten ini adalah konten utama,
        bukan subkonten.
        """
        return self.parent is None

    def clean(self):
        """
        Validasi tambahan:
        Subkonten harus berada pada course yang sama dengan parent-nya.
        """
        if self.parent and self.parent.course_id != self.course_id:
            raise ValidationError(
                "Parent content harus berasal dari course yang sama."
            )


class Comment(models.Model):
    """
    Model Comment digunakan untuk menyimpan komentar member
    pada konten pembelajaran.
    """

    content = models.ForeignKey(
        CourseContent,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    member = models.ForeignKey(
        CourseMember,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.member.user.username} on {self.content.title}"

    def clean(self):
        """
        Validasi tambahan:
        Member hanya boleh komentar pada content dari course yang sama.

        Catatan:
        Saat validasi ModelForm, field member dan content bisa saja belum diisi.
        Jadi validasi relasi hanya dijalankan jika keduanya sudah tersedia.
        """

        if not self.content_id or not self.member_id:
            return

        if self.member.course_id != self.content.course_id:
            raise ValidationError(
                "Member hanya dapat berkomentar pada konten dari course yang diikuti."
            )

    def save(self, *args, **kwargs):
        """
        Memastikan validasi clean() tetap dijalankan
        ketika data disimpan dari shell, view, atau service.
        """
        self.full_clean()
        super().save(*args, **kwargs)