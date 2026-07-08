from django.core.management.base import BaseCommand, CommandError

from core.services.import_csv_service import import_courses


class Command(BaseCommand):
    help = "Import data course dari file CSV."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            type=str,
            help="Path file CSV, contoh: data/courses.csv",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]

        try:
            result = import_courses(csv_path)
        except FileNotFoundError:
            raise CommandError(f"File tidak ditemukan: {csv_path}")
        except ValueError as error:
            raise CommandError(str(error))
        except Exception as error:
            raise CommandError(f"Import gagal: {error}")

        self.stdout.write(self.style.SUCCESS("Import course selesai."))
        self.stdout.write(f"Created: {result['created']}")
        self.stdout.write(f"Updated: {result['updated']}")
        self.stdout.write(f"Skipped: {result['skipped']}")

        if result["errors"]:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Catatan / Error:"))

            for error in result["errors"]:
                self.stdout.write(f"- {error}")