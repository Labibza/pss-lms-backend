# Simple Learning Management System Backend

Simple Learning Management System Backend adalah aplikasi backend sederhana berbasis Django yang digunakan untuk mengelola data pembelajaran, course, member, konten pembelajaran, komentar, import CSV, API course, serta monitoring performa query menggunakan Django Silk.

Aplikasi ini dijalankan menggunakan Docker Compose dengan dua service utama, yaitu:

1. `web` untuk aplikasi Django.
2. `db` untuk database PostgreSQL 15.

---

## 1. Fitur Utama

Fitur yang tersedia pada aplikasi ini:

- Menampilkan halaman home.
- Menampilkan daftar user.
- Menampilkan daftar course.
- Menampilkan detail course.
- Login user.
- Logout menggunakan metode POST.
- Join course.
- Menampilkan course yang diikuti user.
- Dashboard user.
- Membatasi akses konten berdasarkan role.
- Menampilkan detail konten pembelajaran.
- Menambahkan komentar pada konten.
- Edit konten oleh admin, teacher, atau assistant.
- Statistik course.
- Statistik user.
- API daftar course.
- API detail course.
- Filtering course.
- Pagination course.
- Throttling API sederhana.
- Import CSV melalui halaman web.
- Import course melalui command line.
- Seed data dummy.
- Monitoring request dan query menggunakan Django Silk.
- Unit testing dan feature testing.

---

## 2. Aktor Sistem

Aktor dalam sistem LMS ini terdiri dari:

### Admin

Admin adalah user dengan `is_staff=True` atau superuser. Admin dapat mengelola seluruh data melalui Django Admin, mengakses halaman import CSV, dan melihat Django Silk.

### Pengajar

Pengajar adalah user yang menjadi teacher pada suatu course. Pengajar dapat mengelola course dan konten pada course yang diajarnya.

### Asisten

Asisten adalah member course dengan role `ast`. Asisten dapat membantu pengajar mengedit konten pada course tersebut.

### Siswa

Siswa adalah member course dengan role `std`. Siswa dapat join course, membuka konten, dan menambahkan komentar.

### Pengunjung

Pengunjung adalah user yang belum login. Pengunjung hanya dapat membuka halaman umum seperti home dan daftar course.

---

## 3. Teknologi yang Digunakan

| Teknologi | Fungsi |
|---|---|
| Python 3.12 | Bahasa pemrograman utama |
| Django 5.2 | Framework backend |
| PostgreSQL 15 | Database relasional |
| Docker | Container aplikasi |
| Docker Compose | Menjalankan service web dan database |
| psycopg2-binary | Koneksi Django ke PostgreSQL |
| Pillow | Mendukung upload gambar/file |
| django-silk | Profiling request dan query |
| gunicorn | Server production |
| whitenoise | Static files untuk production |
| Postman | Pengujian API |

---

## 4. Struktur Project

Struktur project:

```text
lms-backend/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/
│   ├── management/
│   │   └── commands/
│   │       ├── import_courses_csv.py
│   │       └── seed_data.py
│   │
│   ├── services/
│   │   └── import_csv_service.py
│   │
│   ├── migrations/
│   ├── admin.py
│   ├── decorators.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── data/
│   ├── users.csv
│   ├── courses.csv
│   └── members.csv
│
├── templates/
│   └── core/
│       ├── base.html
│       ├── home.html
│       ├── login.html
│       ├── course_list.html
│       ├── course_detail.html
│       ├── course_content_detail.html
│       ├── dashboard.html
│       ├── my_courses.html
│       ├── upload_csv.html
│       ├── user_list.html
│       ├── course_stat.html
│       ├── user_statistics.html
│       └── partials/
│           └── pagination.html
│
├── static/
├── media/
├── staticfiles/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── .dockerignore
├── manage.py
└── README.md
```

---

## 5. Model Database

Model utama berada di file:

```text
core/models.py
```

Model yang digunakan:

| Model | Fungsi |
|---|---|
| Course | Menyimpan data course |
| CourseMember | Menghubungkan user dengan course |
| CourseContent | Menyimpan konten pembelajaran |
| Comment | Menyimpan komentar pada konten |

---

## 6. Relasi Database

Relasi utama sistem:

```text
User ───< Course
User ───< CourseMember >─── Course
Course ───< CourseContent
CourseContent ───< CourseContent
CourseContent ───< Comment
CourseMember ───< Comment
```

Penjelasan:

- Satu user sebagai teacher dapat memiliki banyak course.
- Satu user dapat menjadi member di banyak course.
- Satu course dapat memiliki banyak member.
- Satu course dapat memiliki banyak konten.
- Satu konten dapat memiliki subkonten.
- Satu konten dapat memiliki banyak komentar.
- Satu member dapat menulis banyak komentar.

---

## 7. Hak Akses

Hak akses ditentukan melalui beberapa method pada model `Course`.

| Method | Fungsi |
|---|---|
| `is_member(user)` | Mengecek apakah user adalah member course |
| `can_manage(user)` | Mengecek apakah user adalah admin atau teacher |
| `can_assist(user)` | Mengecek apakah user adalah admin, teacher, atau assistant |
| `can_view(user)` | Mengecek apakah user boleh melihat konten |

---

## 8. Instalasi dan Menjalankan Project

### 8.1 Clone atau Buka Project

Masuk ke folder project:

```bash
cd lms-backend
```

### 8.2 Build Docker Image

Jalankan:

```bash
docker compose build
```

### 8.3 Jalankan Container

Jalankan:

```bash
docker compose up -d
```

### 8.4 Jalankan Migration

Jalankan:

```bash
docker compose exec web python manage.py migrate
```

### 8.5 Buat Superuser

Jalankan:

```bash
docker compose exec web python manage.py createsuperuser
```

### 8.6 Jalankan Seed Data

Jalankan:

```bash
docker compose exec web python manage.py seed_data
```

### 8.7 Buka Aplikasi

Buka browser:

```text
http://localhost:8000/
```

---

## 9. Akun Testing

Jika menjalankan command:

```bash
docker compose exec web python manage.py seed_data
```

Maka akun berikut akan dibuat:

| Role | Username | Password |
|---|---|---|
| Admin | admin_lms | admin12345 |
| Teacher 1 | teacher_django | teacher12345 |
| Teacher 2 | teacher_python | teacher12345 |
| Assistant | assistant_lms | assistant12345 |
| Student 1 | student_lms_1 | student12345 |
| Student 2 | student_lms_2 | student12345 |

---

## 10. URL Halaman Web

| Halaman | URL | Akses |
|---|---|---|
| Home | `/` | Semua |
| Login | `/login/` | Semua |
| Logout | `/logout/` | Login, POST only |
| Daftar User | `/users/` | Semua |
| Daftar Course | `/courses/` | Semua |
| Detail Course | `/courses/<id>/` | Semua |
| Join Course | `/courses/<id>/join/` | Login |
| My Courses | `/my-courses/` | Login |
| Dashboard | `/dashboard/` | Login |
| Detail Content | `/contents/<id>/` | Member/Admin/Teacher/Assistant |
| Edit Content | `/contents/<id>/edit/` | Admin/Teacher/Assistant |
| Statistik Course | `/statistics/courses/` | Semua |
| Statistik User | `/statistics/users/` | Semua |
| Import CSV | `/import-csv/` | Staff/Admin |
| Django Admin | `/admin/` | Staff/Admin |
| Django Silk | `/silk/` | Staff/Admin |

---

## 11. Filtering dan Pagination Course

Daftar course mendukung filtering menggunakan query parameter.

Contoh:

```text
/courses/?q=django
```

```text
/courses/?teacher=teacher_django
```

```text
/courses/?min_price=50000&max_price=200000
```

```text
/courses/?q=django&teacher=teacher_django&min_price=50000&max_price=200000&page=1&per_page=5
```

Parameter yang tersedia:

| Parameter | Fungsi |
|---|---|
| `q` | Mencari berdasarkan nama, deskripsi, username teacher, atau email teacher |
| `teacher` | Filter berdasarkan username/email teacher |
| `min_price` | Filter harga minimum |
| `max_price` | Filter harga maksimum |
| `page` | Nomor halaman |
| `per_page` | Jumlah data per halaman |

---

## 12. Dokumentasi API

### 12.1 List Course

Endpoint:

```http
GET /api/courses/
```

Contoh:

```text
http://localhost:8000/api/courses/
```

Response success:

```json
{
  "message": "Daftar course berhasil diambil.",
  "filters": {
    "q": "",
    "teacher": "",
    "min_price": "",
    "max_price": ""
  },
  "pagination": {
    "current_page": 1,
    "per_page": 10,
    "total_pages": 1,
    "total_items": 3,
    "has_previous": false,
    "has_next": false
  },
  "count": 3,
  "data": [
    {
      "id": 1,
      "name": "Dasar Django",
      "description": "Course pengenalan Django untuk membangun aplikasi web backend.",
      "price": 100000.0,
      "teacher": "teacher_django",
      "total_members": 2,
      "total_contents": 3,
      "created_at": "2026-07-09T10:00:00+07:00"
    }
  ]
}
```

---

### 12.2 List Course dengan Filter

Endpoint:

```http
GET /api/courses/?q=django
```

Contoh lengkap:

```text
http://localhost:8000/api/courses/?q=django&teacher=teacher_django&min_price=50000&max_price=200000&page=1&per_page=10
```

Parameter:

| Parameter | Contoh | Keterangan |
|---|---|---|
| `q` | django | Keyword pencarian |
| `teacher` | teacher_django | Filter teacher |
| `min_price` | 50000 | Harga minimum |
| `max_price` | 200000 | Harga maksimum |
| `page` | 1 | Halaman |
| `per_page` | 10 | Jumlah data per halaman |

---

### 12.3 Detail Course

Endpoint:

```http
GET /api/courses/<id>/
```

Contoh:

```text
http://localhost:8000/api/courses/1/
```

Response success:

```json
{
  "message": "Detail course berhasil diambil.",
  "data": {
    "id": 1,
    "name": "Dasar Django",
    "description": "Course pengenalan Django untuk membangun aplikasi web backend.",
    "price": 100000.0,
    "teacher": "teacher_django",
    "total_members": 2,
    "total_contents": 3,
    "contents": [
      {
        "id": 1,
        "title": "Pengenalan Django",
        "content_type": "text",
        "parent_id": null,
        "order_number": 1
      }
    ]
  }
}
```

---

### 12.4 Response Jika Course Tidak Ditemukan

Endpoint:

```text
http://localhost:8000/api/courses/999/
```

Response:

```text
Status: 404 Not Found
```

---

### 12.5 Response Jika Terkena Throttling

Jika request API terlalu banyak, response:

```json
{
  "message": "Terlalu banyak request. Silakan coba lagi nanti.",
  "detail": {
    "limit": 30,
    "period_seconds": 60,
    "retry_after_seconds": 42
  }
}
```

Status:

```text
429 Too Many Requests
```

---

## 13. Header Rate Limit API

Setiap response API normal memiliki header:

```text
X-RateLimit-Limit
X-RateLimit-Remaining
X-RateLimit-Reset
```

Contoh:

```text
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 29
X-RateLimit-Reset: 58
```

---

## 14. Import CSV

Fitur import CSV dapat dilakukan melalui dua cara:

1. Import melalui halaman web.
2. Import melalui command line.

---

### 14.1 Import CSV Melalui Web

URL:

```text
http://localhost:8000/import-csv/
```

Akses:

```text
Staff/Admin only
```

Urutan import:

```text
1. Import users.csv
2. Import courses.csv
3. Import members.csv
```

Urutan ini penting karena:

- Course membutuhkan teacher dari tabel user.
- Member membutuhkan user dan course yang sudah ada.

---

### 14.2 Format CSV User

File:

```text
data/users.csv
```

Format:

```csv
username,email,password,is_staff
admin_csv,admin_csv@example.com,admin12345,true
teacher_csv,teacher_csv@example.com,teacher12345,false
student_csv_1,student_csv_1@example.com,student12345,false
```

---

### 14.3 Format CSV Course

File:

```text
data/courses.csv
```

Format:

```csv
name,description,price,teacher_username
Django CSV Course,Course hasil import CSV tentang Django,100000,teacher_csv
Python CSV Course,Course hasil import CSV tentang Python,90000,teacher_csv
```

---

### 14.4 Format CSV Member

File:

```text
data/members.csv
```

Format:

```csv
course_name,username,role
Django CSV Course,student_csv_1,std
Django CSV Course,assistant_csv,ast
```

Role yang valid:

| Role | Keterangan |
|---|---|
| `std` | Student |
| `ast` | Assistant |

---

### 14.5 Import Course Melalui Command Line

Perintah:

```bash
docker compose exec web python manage.py import_courses_csv data/courses.csv
```

Contoh output:

```text
Import course selesai.
Created: 3
Updated: 0
Skipped: 0
```

Jika dijalankan ulang:

```text
Import course selesai.
Created: 0
Updated: 3
Skipped: 0
```

---

## 15. Seed Data

Untuk membuat data dummy:

```bash
docker compose exec web python manage.py seed_data
```

Data yang dibuat:

- Admin.
- Teacher.
- Assistant.
- Student.
- Course.
- Course member.
- Course content.
- Comment.

---

## 16. Testing

Menjalankan semua test:

```bash
docker compose exec web python manage.py test
```

Menjalankan test app core:

```bash
docker compose exec web python manage.py test core
```

Menjalankan test dengan output detail:

```bash
docker compose exec web python manage.py test core -v 2
```

Menjalankan test class tertentu:

```bash
docker compose exec web python manage.py test core.tests.APITest
```

---

## 17. Pengujian Manual dengan Postman

Minimal endpoint yang diuji:

| No | Method | Endpoint | Tujuan |
|---|---|---|---|
| 1 | GET | `/api/courses/` | Menampilkan semua course |
| 2 | GET | `/api/courses/?q=django` | Filter course berdasarkan keyword |
| 3 | GET | `/api/courses/?teacher=teacher_django` | Filter course berdasarkan teacher |
| 4 | GET | `/api/courses/?min_price=50000&max_price=200000` | Filter course berdasarkan harga |
| 5 | GET | `/api/courses/?page=1&per_page=2` | Uji pagination |
| 6 | GET | `/api/courses/1/` | Detail course |
| 7 | GET | `/api/courses/999/` | Uji course tidak ditemukan |
| 8 | GET | `/api/courses/` berkali-kali | Uji throttling |

---

## 18. Monitoring Query dengan Django Silk

Buka:

```text
http://localhost:8000/silk/
```

Gunakan Silk untuk memantau:

- Jumlah request.
- Jumlah query.
- Waktu eksekusi request.
- Query SQL yang dijalankan.
- Endpoint yang lambat.

Contoh endpoint yang dapat diuji:

```text
/courses/
/api/courses/
/api/courses/?q=django
```

---

## 19. Perintah Penting Docker

Menjalankan container:

```bash
docker compose up -d
```

Melihat log web:

```bash
docker compose logs -f web
```

Menghentikan container:

```bash
docker compose down
```

Restart web:

```bash
docker compose restart web
```

Masuk ke container web:

```bash
docker compose exec web bash
```

Masuk ke database PostgreSQL:

```bash
docker compose exec db psql -U lms_user -d lms_db
```

---

## Dokumentasi Tambahan

Dokumentasi tambahan tersedia pada folder `docs`.

| File | Fungsi |
|---|---|
| `docs/POSTMAN_TEST.md` | Panduan pengujian API menggunakan Postman |
| `docs/TESTING_CHECKLIST.md` | Checklist pengujian manual fitur LMS |
| `postman/LMS_Backend_API.postman_collection.json` | File collection Postman |

## 20. Troubleshooting

### 20.1 Error `no such table`

Solusi:

```bash
docker compose exec web python manage.py migrate
```

---

### 20.2 Error `Unknown command: seed_data`

Pastikan struktur file:

```text
core/management/commands/seed_data.py
```

Lalu restart:

```bash
docker compose restart web
```

---

### 20.3 Error `teacher tidak ditemukan` saat import course

Penyebab:

```text
courses.csv diimport sebelum users.csv
```

Solusi:

```text
Import users.csv terlebih dahulu.
```

---

### 20.4 Error `course tidak ditemukan` saat import member

Penyebab:

```text
members.csv diimport sebelum courses.csv
```

Solusi:

```text
Import courses.csv terlebih dahulu.
```

---

### 20.5 API Mengembalikan 429

Penyebab:

```text
Request API terlalu banyak dalam waktu singkat.
```

Solusi development:

```bash
docker compose restart web
```

---

### 20.6 Warning `/app/staticfiles/` Tidak Ada

Buat folder:

```bash
docker compose exec web mkdir -p staticfiles
```

Atau jalankan:

```bash
docker compose exec web python manage.py collectstatic
```

---

## 21. Status Project

Project sudah mencakup:

```text
✓ Desain database
✓ Model dan schema
✓ API
✓ Authentication
✓ Authorization berbasis role
✓ Throttling
✓ Pagination
✓ Filtering
✓ Unit testing
✓ Dokumentasi
✓ Uji Postman
✓ Docker Compose
✓ PostgreSQL
✓ Import CSV
✓ Seed data
✓ Django Admin
✓ Django Silk
```