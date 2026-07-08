import csv
import io
from decimal import Decimal, InvalidOperation

from django.contrib.auth.models import User
from django.db import transaction

from core.models import Course, CourseMember


USER_REQUIRED_HEADERS = {
    "username",
    "email",
    "password",
    "is_staff",
}

COURSE_REQUIRED_HEADERS = {
    "name",
    "description",
    "price",
    "teacher_username",
}

MEMBER_REQUIRED_HEADERS = {
    "course_name",
    "username",
    "role",
}


def empty_result():
    """
    Format hasil import.
    """

    return {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": [],
    }


def read_csv_rows(csv_source):
    """
    Membaca CSV dari dua kemungkinan sumber:
    1. File upload dari request.FILES
    2. Path file lokal, misalnya data/courses.csv

    Fungsi ini mengembalikan:
    - rows
    - headers
    """

    if hasattr(csv_source, "read"):
        raw_data = csv_source.read()

        if isinstance(raw_data, bytes):
            text_data = raw_data.decode("utf-8-sig")
        else:
            text_data = raw_data

    else:
        with open(csv_source, "r", encoding="utf-8-sig", newline="") as file:
            text_data = file.read()

    csv_file = io.StringIO(text_data)
    reader = csv.DictReader(csv_file)

    headers = set(reader.fieldnames or [])
    rows = list(reader)

    return rows, headers


def validate_headers(headers, required_headers):
    """
    Validasi header CSV.
    Jika ada kolom wajib yang tidak ditemukan, maka import dihentikan.
    """

    missing_headers = required_headers - headers

    if missing_headers:
        missing_text = ", ".join(sorted(missing_headers))
        raise ValueError(f"Header CSV tidak lengkap. Kolom yang hilang: {missing_text}")


def parse_bool(value):
    """
    Mengubah string CSV menjadi boolean.
    """

    if value is None:
        return False

    value = str(value).strip().lower()

    return value in ["true", "1", "yes", "y", "ya"]


def parse_price(value):
    """
    Mengubah harga dari CSV menjadi Decimal.
    """

    if value is None or str(value).strip() == "":
        return Decimal("0")

    try:
        return Decimal(str(value).strip())
    except InvalidOperation:
        return None


def normalize_role(value):
    """
    Normalisasi role member.
    CSV boleh memakai:
    - std, student, siswa
    - ast, assistant, asisten
    """

    value = str(value or "").strip().lower()

    if value in ["std", "student", "siswa"]:
        return CourseMember.ROLE_STUDENT

    if value in ["ast", "assistant", "asisten"]:
        return CourseMember.ROLE_ASSISTANT

    return None


@transaction.atomic
def import_users(csv_source):
    """
    Import data user dari CSV.

    Format CSV:
    username,email,password,is_staff
    """

    result = empty_result()

    rows, headers = read_csv_rows(csv_source)
    validate_headers(headers, USER_REQUIRED_HEADERS)

    for row_number, row in enumerate(rows, start=2):
        username = str(row.get("username", "")).strip()
        email = str(row.get("email", "")).strip()
        password = str(row.get("password", "")).strip()
        is_staff = parse_bool(row.get("is_staff"))

        if not username:
            result["skipped"] += 1
            result["errors"].append(f"Baris {row_number}: username kosong.")
            continue

        if not password:
            result["skipped"] += 1
            result["errors"].append(f"Baris {row_number}: password kosong.")
            continue

        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": is_staff,
            }
        )

        user.set_password(password)
        user.save()

        if created:
            result["created"] += 1
        else:
            result["updated"] += 1

    return result


@transaction.atomic
def import_courses(csv_source):
    """
    Import data course dari CSV.

    Format CSV:
    name,description,price,teacher_username
    """

    result = empty_result()

    rows, headers = read_csv_rows(csv_source)
    validate_headers(headers, COURSE_REQUIRED_HEADERS)

    for row_number, row in enumerate(rows, start=2):
        name = str(row.get("name", "")).strip()
        description = str(row.get("description", "")).strip()
        price = parse_price(row.get("price"))
        teacher_username = str(row.get("teacher_username", "")).strip()

        if not name:
            result["skipped"] += 1
            result["errors"].append(f"Baris {row_number}: nama course kosong.")
            continue

        if price is None:
            result["skipped"] += 1
            result["errors"].append(f"Baris {row_number}: format harga tidak valid.")
            continue

        teacher = User.objects.filter(username=teacher_username).first()

        if not teacher:
            result["skipped"] += 1
            result["errors"].append(
                f"Baris {row_number}: teacher '{teacher_username}' tidak ditemukan."
            )
            continue

        course, created = Course.objects.update_or_create(
            name=name,
            defaults={
                "description": description,
                "price": price,
                "teacher": teacher,
            }
        )

        if created:
            result["created"] += 1
        else:
            result["updated"] += 1

    return result


@transaction.atomic
def import_members(csv_source):
    """
    Import data member course dari CSV.

    Format CSV:
    course_name,username,role
    """

    result = empty_result()

    rows, headers = read_csv_rows(csv_source)
    validate_headers(headers, MEMBER_REQUIRED_HEADERS)

    for row_number, row in enumerate(rows, start=2):
        course_name = str(row.get("course_name", "")).strip()
        username = str(row.get("username", "")).strip()
        role = normalize_role(row.get("role"))

        if not course_name:
            result["skipped"] += 1
            result["errors"].append(f"Baris {row_number}: course_name kosong.")
            continue

        if not username:
            result["skipped"] += 1
            result["errors"].append(f"Baris {row_number}: username kosong.")
            continue

        if role is None:
            result["skipped"] += 1
            result["errors"].append(
                f"Baris {row_number}: role tidak valid. Gunakan std atau ast."
            )
            continue

        course = Course.objects.filter(name=course_name).first()

        if not course:
            result["skipped"] += 1
            result["errors"].append(
                f"Baris {row_number}: course '{course_name}' tidak ditemukan."
            )
            continue

        user = User.objects.filter(username=username).first()

        if not user:
            result["skipped"] += 1
            result["errors"].append(
                f"Baris {row_number}: user '{username}' tidak ditemukan."
            )
            continue

        if course.teacher_id == user.id:
            result["skipped"] += 1
            result["errors"].append(
                f"Baris {row_number}: teacher tidak perlu ditambahkan sebagai member."
            )
            continue

        member, created = CourseMember.objects.update_or_create(
            course=course,
            user=user,
            defaults={
                "role": role,
            }
        )

        if created:
            result["created"] += 1
        else:
            result["updated"] += 1

    return result