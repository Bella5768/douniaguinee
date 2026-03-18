from django.core.management.base import BaseCommand
from django.core.files import File
from inscriptions.models import Restitution
import os

class Command(BaseCommand):
    help = 'Upload TDR PDF to restitution'

    def add_arguments(self, parser):
        parser.add_argument('pdf_path', type=str, help='Path to the PDF file')

    def handle(self, *args, **options):
        pdf_path = options['pdf_path']
        
        if not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f'File not found: {pdf_path}'))
            return

        try:
            # Get the first restitution object
            restitution = Restitution.objects.first()
            if not restitution:
                self.stdout.write(self.style.ERROR('No restitution object found'))
                return

            # Open and upload the PDF
            with open(pdf_path, 'rb') as f:
                restitution.tdr_pdf.save(f'tdr_document.pdf', File(f))
                restitution.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully uploaded TDR PDF to restitution: {restitution.tdr_pdf.name}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error uploading PDF: {str(e)}'))
