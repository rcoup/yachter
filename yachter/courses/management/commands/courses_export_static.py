from django.core.management.base import LabelCommand

from yachter.courses.utils import export_static_html

class Command(LabelCommand):
    help = "Export a static HTML/JSON website for browsing the courses."
    args = "exportPath"
    label = 'path to export dir'

    def handle_label(self, export_path, **options):
        export_static_html(export_path)
