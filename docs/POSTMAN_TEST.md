# Dokumentasi Uji API Menggunakan Postman

Dokumentasi ini digunakan untuk menguji endpoint API pada aplikasi Simple LMS Backend.

Base URL lokal:

```text
http://localhost:8000
```

---

## 1. Uji List Course

Method:

```http
GET
```

URL:

```text
http://localhost:8000/api/courses/
```

Expected status:

```text
200 OK
```

Expected response:

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
  "data": []
}
```

---

## 2. Uji Filter Keyword

Method:

```http
GET
```

URL:

```text
http://localhost:8000/api/courses/?q=django
```

Expected status:

```text
200 OK
```

Expected:

```text
Response hanya menampilkan course yang mengandung keyword django.
```

---

## 3. Uji Filter Teacher

Method:

```http
GET
```

URL:

```text
http://localhost:8000/api/courses/?teacher=teacher_django
```

Expected status:

```text
200 OK
```

Expected:

```text
Response hanya menampilkan course dengan teacher teacher_django.
```

---

## 4. Uji Filter Harga

Method:

```http
GET
```

URL:

```text
http://localhost:8000/api/courses/?min_price=50000&max_price=200000
```

Expected status:

```text
200 OK
```

Expected:

```text
Response hanya menampilkan course dengan harga dalam rentang tersebut.
```

---

## 5. Uji Pagination

Method:

```http
GET
```

URL:

```text
http://localhost:8000/api/courses/?page=1&per_page=2
```

Expected status:

```text
200 OK
```

Expected response memiliki metadata:

```json
{
  "pagination": {
    "current_page": 1,
    "per_page": 2,
    "total_pages": 2,
    "total_items": 3,
    "has_previous": false,
    "has_next": true
  }
}
```

---

## 6. Uji Detail Course

Method:

```http
GET
```

URL:

```text
http://localhost:8000/api/courses/1/
```

Expected status:

```text
200 OK
```

Expected response:

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
    "contents": []
  }
}
```

---

## 7. Uji Detail Course Tidak Ditemukan

Method:

```http
GET
```

URL:

```text
http://localhost:8000/api/courses/999/
```

Expected status:

```text
404 Not Found
```

---

## 8. Uji Throttling

Method:

```http
GET
```

URL:

```text
http://localhost:8000/api/courses/
```

Langkah:

```text
Klik Send lebih dari 30 kali dalam 60 detik.
```

Expected status setelah melewati limit:

```text
429 Too Many Requests
```

Expected response:

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

---

## 9. Header yang Perlu Dicek

Pada response normal, cek tab Headers di Postman.

Header yang harus muncul:

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