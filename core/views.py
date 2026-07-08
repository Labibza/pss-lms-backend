from django.contrib.admin.views.decorators import staff_member_required
from .services.import_csv_service import import_courses, import_members, import_users

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min, Q
from django.http import HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .decorators import simple_rate_limit
from .forms import CommentForm, CourseContentForm
from .models import Comment, Course, CourseContent, CourseMember


def get_positive_int(value, default=10, max_value=50):
    """
    Helper untuk mengambil angka positif dari query parameter.
    Digunakan untuk per_page.
    """

    try:
        value = int(value)
    except (TypeError, ValueError):
        return default

    if value <= 0:
        return default

    if max_value is not None:
        return min(value, max_value)

    return value


def get_decimal_param(request, param_name):
    """
    Helper untuk mengambil angka decimal dari query parameter.
    Digunakan untuk min_price dan max_price.
    """

    value = request.GET.get(param_name, "").strip()

    if not value:
        return None

    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def get_course_base_queryset():
    """
    Query dasar course yang sudah dioptimalkan.

    select_related:
    - mengambil data teacher dalam query yang sama.

    annotate:
    - menghitung total member dan total content.
    """

    return (
        Course.objects
        .select_related("teacher")
        .annotate(
            total_members=Count("memberships", distinct=True),
            total_contents=Count("contents", distinct=True),
        )
    )


def apply_course_filters(queryset, request):
    """
    Filtering course berdasarkan query parameter.

    Parameter yang didukung:
    - q
    - teacher
    - min_price
    - max_price
    """

    q = request.GET.get("q", "").strip()
    teacher = request.GET.get("teacher", "").strip()
    min_price = get_decimal_param(request, "min_price")
    max_price = get_decimal_param(request, "max_price")

    if q:
        queryset = queryset.filter(
            Q(name__icontains=q)
            | Q(description__icontains=q)
            | Q(teacher__username__icontains=q)
            | Q(teacher__email__icontains=q)
        )

    if teacher:
        queryset = queryset.filter(
            Q(teacher__username__icontains=teacher)
            | Q(teacher__email__icontains=teacher)
        )

    if min_price is not None:
        queryset = queryset.filter(price__gte=min_price)

    if max_price is not None:
        queryset = queryset.filter(price__lte=max_price)

    return queryset


def build_query_string_without_page(request):
    """
    Membuat query string tanpa parameter page.
    Dipakai agar pagination tetap mempertahankan filter.
    """

    query_params = request.GET.copy()

    if "page" in query_params:
        query_params.pop("page")

    return query_params.urlencode()


def home(request):
    """
    Halaman utama LMS.
    """

    total_courses = Course.objects.count()
    total_users = User.objects.count()
    total_comments = Comment.objects.count()

    popular_courses = (
        get_course_base_queryset()
        .order_by("-total_members", "name")[:5]
    )

    context = {
        "title": "Learning Management System",
        "total_courses": total_courses,
        "total_users": total_users,
        "total_comments": total_comments,
        "popular_courses": popular_courses,
    }

    return render(request, "core/home.html", context)


def user_list(request):
    """
    Menampilkan daftar user.
    """

    users = (
        User.objects
        .annotate(
            total_teaching_courses=Count("teaching_courses", distinct=True),
            total_joined_courses=Count("course_memberships", distinct=True),
        )
        .order_by("username")
    )

    context = {
        "title": "Daftar User",
        "users": users,
    }

    return render(request, "core/user_list.html", context)


def course_list(request):
    """
    Menampilkan daftar course dengan filtering dan pagination.
    """

    courses_queryset = get_course_base_queryset()
    courses_queryset = apply_course_filters(courses_queryset, request)
    courses_queryset = courses_queryset.order_by("name")

    per_page = get_positive_int(
        request.GET.get("per_page"),
        default=5,
        max_value=50,
    )

    paginator = Paginator(courses_queryset, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "title": "Daftar Course",
        "courses": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "query_string": build_query_string_without_page(request),
        "total_filtered": paginator.count,
        "per_page": per_page,
        "filter_values": {
            "q": request.GET.get("q", ""),
            "teacher": request.GET.get("teacher", ""),
            "min_price": request.GET.get("min_price", ""),
            "max_price": request.GET.get("max_price", ""),
        },
    }

    return render(request, "core/course_list.html", context)


def course_detail(request, course_id):
    """
    Menampilkan detail course dan daftar konten utama.
    """

    course = get_object_or_404(
        get_course_base_queryset(),
        id=course_id,
    )

    root_contents = (
        CourseContent.objects
        .filter(course=course, parent__isnull=True)
        .prefetch_related("children")
        .order_by("order_number", "title")
    )

    context = {
        "title": course.name,
        "course": course,
        "root_contents": root_contents,
        "is_member": course.is_member(request.user),
        "can_manage": course.can_manage(request.user),
        "can_assist": course.can_assist(request.user),
        "can_view": course.can_view(request.user),
    }

    return render(request, "core/course_detail.html", context)


@login_required
@require_POST
def join_course(request, course_id):
    """
    User login dapat bergabung ke course.
    """

    course = get_object_or_404(Course, id=course_id)

    if course.teacher_id == request.user.id:
        messages.info(
            request,
            "Anda adalah pengajar pada course ini, jadi tidak perlu join sebagai siswa."
        )
        return redirect("course_detail", course_id=course.id)

    member, created = CourseMember.objects.get_or_create(
        course=course,
        user=request.user,
        defaults={
            "role": CourseMember.ROLE_STUDENT,
        }
    )

    if created:
        messages.success(request, f"Berhasil bergabung ke course {course.name}.")
    else:
        messages.info(request, f"Anda sudah tergabung di course {course.name}.")

    return redirect("course_detail", course_id=course.id)


@login_required
def my_courses(request):
    """
    Menampilkan daftar course yang diikuti user login.
    """

    memberships = (
        CourseMember.objects
        .select_related("course", "course__teacher")
        .filter(user=request.user)
        .annotate(
            total_contents=Count("course__contents", distinct=True),
            total_members=Count("course__memberships", distinct=True),
        )
        .order_by("course__name")
    )

    context = {
        "title": "Course Saya",
        "memberships": memberships,
    }

    return render(request, "core/my_courses.html", context)


@login_required
def dashboard(request):
    """
    Dashboard user.
    """

    total_joined_courses = CourseMember.objects.filter(user=request.user).count()
    total_teaching_courses = Course.objects.filter(teacher=request.user).count()
    total_comments = Comment.objects.filter(member__user=request.user).count()

    joined_courses = (
        CourseMember.objects
        .select_related("course", "course__teacher")
        .filter(user=request.user)
        .order_by("-joined_at")[:5]
    )

    recent_comments = (
        Comment.objects
        .select_related(
            "content",
            "content__course",
            "member",
            "member__user",
        )
        .filter(member__user=request.user)
        .order_by("-created_at")[:5]
    )

    context = {
        "title": "Dashboard",
        "total_joined_courses": total_joined_courses,
        "total_teaching_courses": total_teaching_courses,
        "total_comments": total_comments,
        "joined_courses": joined_courses,
        "recent_comments": recent_comments,
    }

    return render(request, "core/dashboard.html", context)


def course_content_detail(request, content_id):
    """
    Menampilkan detail konten dan komentar.
    """

    content = get_object_or_404(
        CourseContent.objects.select_related(
            "course",
            "course__teacher",
            "parent",
        ),
        id=content_id,
    )

    course = content.course

    if not course.can_view(request.user):
        if not request.user.is_authenticated:
            messages.warning(request, "Silakan login terlebih dahulu untuk membuka konten.")
            login_url = reverse("login")
            return redirect(f"{login_url}?next={request.path}")

        return HttpResponseForbidden(
            "Anda tidak memiliki akses untuk melihat konten ini."
        )

    comments = (
        content.comments
        .select_related("member", "member__user")
        .order_by("-created_at")
    )

    context = {
        "title": content.title,
        "content": content,
        "course": course,
        "comments": comments,
        "comment_form": CommentForm(),
        "can_assist": course.can_assist(request.user),
    }

    return render(request, "core/course_content_detail.html", context)


@login_required
@require_POST
def add_comment(request, content_id):
    """
    Menambahkan komentar pada konten.
    """

    content = get_object_or_404(
        CourseContent.objects.select_related("course"),
        id=content_id,
    )

    course = content.course

    if not course.can_view(request.user):
        return HttpResponseForbidden(
            "Anda tidak memiliki akses untuk mengomentari konten ini."
        )

    member = CourseMember.objects.filter(
        course=course,
        user=request.user,
    ).first()

    if not member:
        messages.error(
            request,
            "Hanya member course yang dapat menambahkan komentar."
        )
        return redirect("course_content_detail", content_id=content.id)

    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.content = content
        comment.member = member
        comment.save()

        messages.success(request, "Komentar berhasil ditambahkan.")
    else:
        messages.error(request, "Komentar gagal ditambahkan. Periksa kembali input Anda.")

    return redirect("course_content_detail", content_id=content.id)


@login_required
def edit_content(request, content_id):
    """
    Mengedit konten pembelajaran.
    """

    content = get_object_or_404(
        CourseContent.objects.select_related("course", "course__teacher"),
        id=content_id,
    )

    course = content.course

    if not course.can_assist(request.user):
        return HttpResponseForbidden(
            "Anda tidak memiliki akses untuk mengedit konten ini."
        )

    if request.method == "POST":
        form = CourseContentForm(
            request.POST,
            request.FILES,
            instance=content,
            course=course,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Konten berhasil diperbarui.")
            return redirect("course_content_detail", content_id=content.id)
    else:
        form = CourseContentForm(instance=content, course=course)

    context = {
        "title": f"Edit Konten - {content.title}",
        "form": form,
        "content": content,
        "course": course,
    }

    return render(request, "core/edit_content.html", context)


def course_stat(request):
    """
    Statistik course.
    """

    stats = Course.objects.aggregate(
        total_courses=Count("id"),
        max_price=Max("price"),
        min_price=Min("price"),
        avg_price=Avg("price"),
    )

    courses = (
        get_course_base_queryset()
        .order_by("-total_members", "name")
    )

    context = {
        "title": "Statistik Course",
        "stats": stats,
        "courses": courses,
    }

    return render(request, "core/course_stat.html", context)


def user_statistics(request):
    """
    Statistik user.
    """

    total_users = User.objects.count()
    total_staff = User.objects.filter(is_staff=True).count()
    total_non_staff = User.objects.filter(is_staff=False).count()
    total_users_joined_course = (
        CourseMember.objects
        .values("user")
        .distinct()
        .count()
    )

    users = (
        User.objects
        .annotate(
            total_teaching_courses=Count("teaching_courses", distinct=True),
            total_joined_courses=Count("course_memberships", distinct=True),
            total_comments=Count("course_memberships__comments", distinct=True),
        )
        .order_by("username")
    )

    context = {
        "title": "Statistik User",
        "total_users": total_users,
        "total_staff": total_staff,
        "total_non_staff": total_non_staff,
        "total_users_joined_course": total_users_joined_course,
        "users": users,
    }

    return render(request, "core/user_statistics.html", context)


@require_GET
@simple_rate_limit(limit=30, period=60, key_prefix="api")
def api_courses(request):
    """
    API daftar course dengan filtering, pagination, dan throttling.

    Contoh:
    /api/courses/?q=django&page=1&per_page=10
    /api/courses/?teacher=teacher1&min_price=50000&max_price=200000
    """

    courses_queryset = get_course_base_queryset()
    courses_queryset = apply_course_filters(courses_queryset, request)
    courses_queryset = courses_queryset.order_by("name")

    per_page = get_positive_int(
        request.GET.get("per_page"),
        default=10,
        max_value=50,
    )

    paginator = Paginator(courses_queryset, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))

    data = []

    for course in page_obj.object_list:
        data.append(
            {
                "id": course.id,
                "name": course.name,
                "description": course.description,
                "price": float(course.price),
                "teacher": course.teacher.username,
                "total_members": course.total_members,
                "total_contents": course.total_contents,
                "created_at": course.created_at.isoformat(),
            }
        )

    return JsonResponse(
        {
            "message": "Daftar course berhasil diambil.",
            "filters": {
                "q": request.GET.get("q", ""),
                "teacher": request.GET.get("teacher", ""),
                "min_price": request.GET.get("min_price", ""),
                "max_price": request.GET.get("max_price", ""),
            },
            "pagination": {
                "current_page": page_obj.number,
                "per_page": per_page,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "has_previous": page_obj.has_previous(),
                "has_next": page_obj.has_next(),
            },
            "count": len(data),
            "data": data,
        }
    )


@require_GET
@simple_rate_limit(limit=30, period=60, key_prefix="api")
def api_course_detail(request, course_id):
    """
    API detail course dengan throttling.
    """

    course = get_object_or_404(
        get_course_base_queryset(),
        id=course_id,
    )

    contents = (
        CourseContent.objects
        .filter(course=course)
        .order_by("parent_id", "order_number", "title")
    )

    content_data = []

    for content in contents:
        content_data.append(
            {
                "id": content.id,
                "title": content.title,
                "content_type": content.content_type,
                "parent_id": content.parent_id,
                "order_number": content.order_number,
            }
        )

    data = {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "price": float(course.price),
        "teacher": course.teacher.username,
        "total_members": course.total_members,
        "total_contents": course.total_contents,
        "contents": content_data,
    }

    return JsonResponse(
        {
            "message": "Detail course berhasil diambil.",
            "data": data,
        }
    )


@require_POST
def logout_post(request):
    """
    Logout berbasis POST.
    """

    logout(request)
    messages.success(request, "Anda berhasil logout.")
    return redirect("home")


def logout_get_not_allowed(request):
    """
    Jika user mencoba logout lewat GET.
    """

    return HttpResponseNotAllowed(
        ["POST"],
        "Logout harus menggunakan metode POST."
    )

@staff_member_required(login_url="/admin/login/")
def upload_csv(request):
    """
    Halaman import CSV.
    Hanya staff/admin yang boleh mengakses halaman ini.
    """

    result = None

    if request.method == "POST":
        import_type = request.POST.get("import_type")
        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            messages.error(request, "File CSV belum dipilih.")
            return redirect("upload_csv")

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "File harus berformat .csv.")
            return redirect("upload_csv")

        try:
            if import_type == "users":
                result = import_users(csv_file)
                messages.success(request, "Import user selesai.")

            elif import_type == "courses":
                result = import_courses(csv_file)
                messages.success(request, "Import course selesai.")

            elif import_type == "members":
                result = import_members(csv_file)
                messages.success(request, "Import member selesai.")

            else:
                messages.error(request, "Tipe import tidak valid.")
                return redirect("upload_csv")

        except ValueError as error:
            messages.error(request, str(error))

        except Exception as error:
            messages.error(request, f"Terjadi error saat import CSV: {error}")

    context = {
        "title": "Import CSV",
        "result": result,
    }

    return render(request, "core/upload_csv.html", context)