from django.contrib import admin
from django.db.models import Count

from .models import Comment, Course, CourseContent, CourseMember


class CourseMemberInline(admin.TabularInline):
    model = CourseMember
    extra = 1
    fields = ("user", "role", "joined_at")
    readonly_fields = ("joined_at",)


class CourseContentInline(admin.TabularInline):
    model = CourseContent
    extra = 1
    fields = ("title", "content_type", "parent", "order_number")
    show_change_link = True


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("member", "text", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "teacher",
        "price",
        "total_members",
        "total_contents",
        "created_at",
    )
    search_fields = ("name", "description", "teacher__username", "teacher__email")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CourseMemberInline, CourseContentInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("teacher").annotate(
            members_count=Count("memberships", distinct=True),
            contents_count=Count("contents", distinct=True),
        )

    def total_members(self, obj):
        return obj.members_count

    def total_contents(self, obj):
        return obj.contents_count

    total_members.short_description = "Members"
    total_contents.short_description = "Contents"


@admin.register(CourseMember)
class CourseMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "role", "joined_at")
    search_fields = ("user__username", "user__email", "course__name")
    list_filter = ("role", "course", "joined_at")
    readonly_fields = ("joined_at",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "course")


@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "content_type",
        "parent",
        "order_number",
        "created_at",
    )
    search_fields = ("title", "text_content", "course__name")
    list_filter = ("content_type", "course", "created_at")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CommentInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("course", "parent")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("short_text", "content", "member", "created_at")
    search_fields = (
        "text",
        "content__title",
        "member__user__username",
        "member__course__name",
    )
    list_filter = ("created_at", "content__course")
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "content",
            "content__course",
            "member",
            "member__user",
            "member__course",
        )

    def short_text(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + "..."
        return obj.text

    short_text.short_description = "Comment"