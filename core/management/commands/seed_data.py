from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Comment, Course, CourseContent, CourseMember


class Command(BaseCommand):
    help = "Membuat data dummy yang lebih kaya dan terasa seperti platform belajar sungguhan."

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
        self.stdout.write("Menyiapkan data platform belajar...")

        admin, _ = self.create_user("admin_lms", "admin@example.com", "admin12345", True, True)

        mentors_data = [
            ("nabila.rahma", "nabila@example.com"),
            ("arya.saputra", "arya@example.com"),
            ("nadia.putri", "nadia@example.com"),
            ("fahmi.akbar", "fahmi@example.com"),
            ("salma.kirana", "salma@example.com"),
            ("rizky.pratama", "rizky@example.com"),
        ]

        assistants_data = [
            ("salsa.helper", "salsa@example.com"),
            ("hafiz.support", "hafiz@example.com"),
            ("mira.guide", "mira@example.com"),
            ("dian.assist", "dian@example.com"),
        ]

        learners_data = [
            ("belajar01", "belajar01@example.com"),
            ("belajar02", "belajar02@example.com"),
            ("belajar03", "belajar03@example.com"),
            ("belajar04", "belajar04@example.com"),
            ("belajar05", "belajar05@example.com"),
            ("belajar06", "belajar06@example.com"),
            ("belajar07", "belajar07@example.com"),
            ("belajar08", "belajar08@example.com"),
            ("belajar09", "belajar09@example.com"),
            ("belajar10", "belajar10@example.com"),
            ("belajar11", "belajar11@example.com"),
            ("belajar12", "belajar12@example.com"),
            ("belajar13", "belajar13@example.com"),
            ("belajar14", "belajar14@example.com"),
            ("belajar15", "belajar15@example.com"),
            ("belajar16", "belajar16@example.com"),
            ("belajar17", "belajar17@example.com"),
            ("belajar18", "belajar18@example.com"),
        ]

        mentors = []
        assistants = []
        learners = []

        for username, email in mentors_data:
            user, _ = self.create_user(username, email, "mentor12345")
            mentors.append(user)

        for username, email in assistants_data:
            user, _ = self.create_user(username, email, "assistant12345")
            assistants.append(user)

        for username, email in learners_data:
            user, _ = self.create_user(username, email, "student12345")
            learners.append(user)

        programs = [
            {
                "name": "UI Design Fundamental",
                "description": "Mengenal dasar-dasar perancangan antarmuka yang rapi, nyaman digunakan, dan siap dipresentasikan sebagai portofolio awal.",
                "price": Decimal("149000"),
                "teacher": mentors[0],
                "sessions": [
                    "Mengenal pola antarmuka modern",
                    "Menyusun struktur halaman",
                    "Membangun konsistensi visual",
                    "Membuat studi kasus sederhana",
                ],
            },
            {
                "name": "Digital Marketing for Beginner",
                "description": "Belajar merancang strategi promosi digital dari nol, mulai dari memahami audiens hingga menyusun konten yang relevan.",
                "price": Decimal("179000"),
                "teacher": mentors[1],
                "sessions": [
                    "Dasar pemasaran digital",
                    "Mengenal target audiens",
                    "Strategi konten dan copywriting",
                    "Membaca hasil kampanye",
                ],
            },
            {
                "name": "Public Speaking Essentials",
                "description": "Mengembangkan kepercayaan diri saat berbicara di depan umum dengan teknik penyampaian yang runtut dan meyakinkan.",
                "price": Decimal("129000"),
                "teacher": mentors[2],
                "sessions": [
                    "Mengatasi rasa gugup",
                    "Menyusun alur penyampaian",
                    "Teknik vokal dan artikulasi",
                    "Latihan presentasi efektif",
                ],
            },
            {
                "name": "Analisis Data Dasar",
                "description": "Memahami pola pengolahan data, membaca insight dasar, dan menyusun kesimpulan yang mudah dipahami.",
                "price": Decimal("199000"),
                "teacher": mentors[3],
                "sessions": [
                    "Mengenal data dan perannya",
                    "Membersihkan data secara sederhana",
                    "Membaca pola dan insight",
                    "Menyusun ringkasan hasil",
                ],
            },
            {
                "name": "Branding untuk UMKM",
                "description": "Belajar membangun identitas usaha yang kuat mulai dari positioning, visual brand, hingga komunikasi yang konsisten.",
                "price": Decimal("159000"),
                "teacher": mentors[4],
                "sessions": [
                    "Memahami identitas brand",
                    "Menyusun pesan utama",
                    "Menentukan gaya visual",
                    "Menjaga konsistensi brand",
                ],
            },
            {
                "name": "Product Thinking Starter Pack",
                "description": "Membantu memahami proses membangun solusi yang dibutuhkan pengguna melalui sudut pandang produk.",
                "price": Decimal("219000"),
                "teacher": mentors[5],
                "sessions": [
                    "Memahami masalah pengguna",
                    "Merumuskan solusi yang relevan",
                    "Menyusun prioritas fitur",
                    "Validasi ide sederhana",
                ],
            },
            {
                "name": "Copywriting for Social Media",
                "description": "Menyusun tulisan singkat yang kuat, persuasif, dan mudah dipahami untuk berbagai platform digital.",
                "price": Decimal("99000"),
                "teacher": mentors[1],
                "sessions": [
                    "Mengenal karakter tulisan digital",
                    "Membangun hook yang menarik",
                    "Teknik call to action",
                    "Menyusun caption yang engaging",
                ],
            },
            {
                "name": "Basic Video Editing",
                "description": "Belajar menyusun alur visual, memotong footage, menambahkan transisi, dan membuat hasil akhir yang enak ditonton.",
                "price": Decimal("189000"),
                "teacher": mentors[0],
                "sessions": [
                    "Mengenal alur editing",
                    "Cutting dan sequencing",
                    "Menambahkan audio dan teks",
                    "Finalisasi video sederhana",
                ],
            },
            {
                "name": "Personal Branding Online",
                "description": "Membangun citra diri profesional di ruang digital agar lebih siap menghadapi peluang studi maupun karier.",
                "price": Decimal("139000"),
                "teacher": mentors[4],
                "sessions": [
                    "Menentukan positioning diri",
                    "Menyusun profil yang kuat",
                    "Membuat konten yang relevan",
                    "Menjaga konsistensi citra",
                ],
            },
            {
                "name": "Bahasa Inggris untuk Karier",
                "description": "Membiasakan penggunaan Bahasa Inggris praktis untuk komunikasi profesional dan kebutuhan kerja.",
                "price": Decimal("169000"),
                "teacher": mentors[2],
                "sessions": [
                    "Perkenalan profesional",
                    "Komunikasi kerja sehari-hari",
                    "Menulis pesan yang jelas",
                    "Latihan presentasi singkat",
                ],
            },
        ]

        sample_replies = [
            "Penyampaiannya runtut dan mudah diikuti. Saya jadi lebih paham gambaran besarnya.",
            "Bagian ini membantu sekali untuk memahami langkah awal sebelum praktik.",
            "Contoh yang diberikan relevan dan terasa dekat dengan kondisi nyata.",
            "Saya suka karena pembahasannya tidak terlalu rumit, tapi tetap jelas.",
            "Materinya enak diikuti. Akan lebih seru kalau ada tugas kecil di akhir sesi.",
            "Penjelasan mentor sangat membantu untuk merapikan cara berpikir saya.",
        ]

        for index, program in enumerate(programs):
            course, _ = Course.objects.update_or_create(
                name=program["name"],
                defaults={
                    "description": program["description"],
                    "price": program["price"],
                    "teacher": program["teacher"],
                }
            )

            assistant = assistants[index % len(assistants)]
            CourseMember.objects.update_or_create(
                course=course,
                user=assistant,
                defaults={"role": CourseMember.ROLE_ASSISTANT}
            )

            # 5 peserta per program
            selected_learners = learners[index:index + 5]
            for learner in selected_learners:
                CourseMember.objects.update_or_create(
                    course=course,
                    user=learner,
                    defaults={"role": CourseMember.ROLE_STUDENT}
                )

            created_sessions = []

            for session_number, session_title in enumerate(program["sessions"], start=1):
                parent_content, _ = CourseContent.objects.update_or_create(
                    course=course,
                    title=session_title,
                    defaults={
                        "parent": None,
                        "content_type": CourseContent.TYPE_TEXT,
                        "text_content": (
                            f"{session_title} membahas konsep inti yang perlu dipahami sebelum melanjutkan "
                            f"ke praktik berikutnya. Setiap pembahasan dirancang singkat, jelas, dan mudah diikuti."
                        ),
                        "order_number": session_number,
                    }
                )
                created_sessions.append(parent_content)

                CourseContent.objects.update_or_create(
                    course=course,
                    parent=parent_content,
                    title=f"Latihan Ringkas: {session_title}",
                    defaults={
                        "content_type": CourseContent.TYPE_TEXT,
                        "text_content": (
                            "Bagian ini berisi latihan singkat agar pemahamanmu semakin kuat. "
                            "Coba rangkum poin penting lalu terapkan dalam contoh sederhana."
                        ),
                        "order_number": 1,
                    }
                )

            # Buat diskusi di sesi pertama
            if created_sessions:
                first_session = created_sessions[0]
                active_members = CourseMember.objects.filter(course=course, role=CourseMember.ROLE_STUDENT)[:3]

                for idx_member, member in enumerate(active_members):
                    Comment.objects.get_or_create(
                        content=first_session,
                        member=member,
                        defaults={
                            "text": sample_replies[(index + idx_member) % len(sample_replies)]
                        }
                    )

        self.stdout.write(self.style.SUCCESS("Data platform berhasil dibuat."))
        self.stdout.write("")
        self.stdout.write("Akun contoh:")
        self.stdout.write("Admin      : admin_lms / admin12345")
        self.stdout.write("Mentor     : nabila.rahma / mentor12345")
        self.stdout.write("Pendamping : salsa.helper / assistant12345")
        self.stdout.write("Peserta    : belajar01 / student12345")