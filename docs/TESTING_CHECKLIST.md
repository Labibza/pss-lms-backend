# Checklist Pengujian Manual LMS Backend

Checklist ini digunakan untuk memastikan fitur utama aplikasi berjalan dengan baik.

---

## 1. Setup Project

- [ ] Docker Desktop berjalan.
- [ ] `docker compose build` berhasil.
- [ ] `docker compose up -d` berhasil.
- [ ] Container `web` berjalan.
- [ ] Container `db` berjalan.
- [ ] `python manage.py check` berhasil.
- [ ] Migration berhasil.
- [ ] Seed data berhasil.

---

## 2. Halaman Umum

- [ ] Halaman home `/` dapat dibuka.
- [ ] Halaman users `/users/` dapat dibuka.
- [ ] Halaman courses `/courses/` dapat dibuka.
- [ ] Halaman statistik course `/statistics/courses/` dapat dibuka.
- [ ] Halaman statistik user `/statistics/users/` dapat dibuka.

---

## 3. Authentication

- [ ] Halaman login `/login/` dapat dibuka.
- [ ] Login dengan student berhasil.
- [ ] Login dengan teacher berhasil.
- [ ] Login dengan assistant berhasil.
- [ ] Login dengan admin berhasil.
- [ ] Logout hanya berjalan dengan POST.
- [ ] Logout berhasil mengarahkan ke home.

---

## 4. Course

- [ ] Daftar course tampil.
- [ ] Detail course tampil.
- [ ] Course menampilkan teacher.
- [ ] Course menampilkan jumlah member.
- [ ] Course menampilkan jumlah konten.
- [ ] User login dapat join course.
- [ ] User yang sudah join tidak membuat duplikasi membership.
- [ ] Teacher tidak perlu join course miliknya sendiri.

---

## 5. Course Content

- [ ] Pengunjung tidak bisa membuka konten.
- [ ] Student yang belum join tidak bisa membuka konten.
- [ ] Student yang sudah join bisa membuka konten.
- [ ] Teacher bisa membuka konten.
- [ ] Assistant bisa membuka konten.
- [ ] Admin bisa membuka konten.

---

## 6. Comment

- [ ] Student yang sudah join bisa menambahkan komentar.
- [ ] Student yang belum join tidak bisa menambahkan komentar.
- [ ] Komentar tampil pada halaman detail konten.
- [ ] Komentar tersimpan di Django Admin.

---

## 7. Edit Content

- [ ] Student tidak bisa edit konten.
- [ ] Assistant bisa edit konten.
- [ ] Teacher bisa edit konten.
- [ ] Admin bisa edit konten.
- [ ] Perubahan konten tersimpan.

---

## 8. Filtering dan Pagination

- [ ] Filter keyword course berjalan.
- [ ] Filter teacher berjalan.
- [ ] Filter harga minimum berjalan.
- [ ] Filter harga maksimum berjalan.
- [ ] Pagination course berjalan.
- [ ] Filter tetap aktif saat pindah halaman.

---

## 9. Import CSV

- [ ] User non-staff tidak bisa membuka `/import-csv/`.
- [ ] Admin/staff bisa membuka `/import-csv/`.
- [ ] Import `users.csv` berhasil.
- [ ] Import `courses.csv` berhasil.
- [ ] Import `members.csv` berhasil.
- [ ] Data hasil import tampil di halaman course.
- [ ] Data hasil import tampil di Django Admin.
- [ ] Command `import_courses_csv` berhasil dijalankan.

---

## 10. API dan Postman

- [ ] `GET /api/courses/` berhasil.
- [ ] `GET /api/courses/?q=django` berhasil.
- [ ] `GET /api/courses/?teacher=teacher_django` berhasil.
- [ ] `GET /api/courses/?min_price=50000&max_price=200000` berhasil.
- [ ] `GET /api/courses/?page=1&per_page=2` berhasil.
- [ ] `GET /api/courses/1/` berhasil.
- [ ] `GET /api/courses/999/` menghasilkan 404.
- [ ] API memiliki header rate limit.
- [ ] API menghasilkan 429 jika request terlalu banyak.

---

## 11. Django Admin

- [ ] Admin dapat login ke `/admin/`.
- [ ] Model Course tampil.
- [ ] Model CourseMember tampil.
- [ ] Model CourseContent tampil.
- [ ] Model Comment tampil.
- [ ] Admin dapat menambah course.
- [ ] Admin dapat menambah member.
- [ ] Admin dapat menambah content.
- [ ] Admin dapat melihat comment.

---

## 12. Django Silk

- [ ] `/silk/` dapat dibuka.
- [ ] Request `/courses/` tercatat.
- [ ] Request `/api/courses/` tercatat.
- [ ] Query SQL dapat dilihat.
- [ ] Jumlah query dapat dipantau.