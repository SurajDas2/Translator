import mimetypes
from time import sleep
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import render
from django.http import FileResponse, Http404, HttpResponse
from .forms import UploadFileForm
import pandas as pd
import pdb
import os
from translate import Translator

def translate_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # handle the file upload
            uploaded_file = request.FILES['file']
            if hasattr(uploaded_file, 'temporary_file_path'):
                file_path = uploaded_file.temporary_file_path()
            else:
                # File was uploaded into memory (not a temporary file on disk)
                file_path = 'temp.xlsx'  # Temporary filename
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
            df = pd.read_excel(file_path)
        
            # Apply translation
            translator = Translator(to_lang="hi")
            df = df.applymap(lambda x: translator.translate(str(x)) if pd.notnull(x) else x)
            # Save to a new Excel file
            output_filename = os.path.splitext(file_path)[0] + '_translated.xlsx'
            df.to_excel(output_filename, engine='xlsxwriter', index=False)

            # Save translated file path in session for download view to use
            request.session['translated_file'] = output_filename
            return render(request, 'translateApp/upload.html', {'form': form,'translated_file': output_filename })
    else:
        form = UploadFileForm()
    return render(request, 'translateApp/upload.html', {'form': form})

def download(request):
    # Get the file path from the GET request
    file_path = request.GET.get('translated_file')

    filepath = os.path.join(settings.BASE_DIR, file_path)

    # Check if file exists before attempting to open
    if os.path.exists(filepath):
        # Open the file in read-only mode
        file = open(filepath, 'rb')

        # Create a FileResponse and send it as a response
        response = FileResponse(file)

        # Suggest a download filename
        filename = os.path.basename(filepath)
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
    else:
        raise Http404("File does not exist.")


