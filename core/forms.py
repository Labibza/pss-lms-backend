from django import forms

from .models import Comment, CourseContent


class CommentForm(forms.ModelForm):
    """
    Form untuk menambahkan komentar pada konten pembelajaran.
    """

    class Meta:
        model = Comment
        fields = ["text"]
        labels = {
            "text": "Komentar",
        }
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tulis komentar Anda di sini...",
                    "class": "form-control",
                }
            )
        }


class CourseContentForm(forms.ModelForm):
    """
    Form untuk mengedit konten pembelajaran.
    Digunakan oleh admin, teacher, atau assistant.
    """

    class Meta:
        model = CourseContent
        fields = [
            "parent",
            "title",
            "content_type",
            "text_content",
            "video_url",
            "file",
            "order_number",
        ]
        labels = {
            "parent": "Parent Content",
            "title": "Judul Konten",
            "content_type": "Tipe Konten",
            "text_content": "Isi Materi",
            "video_url": "URL Video",
            "file": "File Materi",
            "order_number": "Urutan",
        }
        widgets = {
            "parent": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content_type": forms.Select(attrs={"class": "form-control"}),
            "text_content": forms.Textarea(attrs={"rows": 8, "class": "form-control"}),
            "video_url": forms.URLInput(attrs={"class": "form-control"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "order_number": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        course = kwargs.pop("course", None)
        current_content = kwargs.get("instance", None)

        super().__init__(*args, **kwargs)

        if course:
            parent_queryset = CourseContent.objects.filter(course=course)

            if current_content:
                parent_queryset = parent_queryset.exclude(id=current_content.id)

            self.fields["parent"].queryset = parent_queryset