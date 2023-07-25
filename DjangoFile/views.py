from django.http import HttpResponse
from django.shortcuts import redirect, render
import boto3
import urllib3
import urllib.parse
from djangoDashboard import settings
from djangoDashboard.settings import AWS_ACCESS_KEY_ID, AWS_S3_REGION_NAME, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME


def upload_file(request):
    if request.method == 'POST' and request.FILES.get('myfile'):
        file = request.FILES['myfile']

        # Dosya boyutunu kontrol et
        if file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            context={'success': False, 'error': 'Dosya boyutu çok büyük.'}
            return render(request,'file_process.html',context)

        # Dosya türünü kontrol et
        allowed_mime_types = ['application/pdf']
        if file.content_type not in allowed_mime_types:
            context={'success': False, 'error': 'Dosya geçersiz türde.'}
            return render(request,'file_process.html',context)

        # S3'e dosyayı yükleme işlemi
        s3 = boto3.client(service_name='s3', region_name=AWS_S3_REGION_NAME,
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        
        try:
            s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, 'uploaded_Files/' + file.name)
           
            bucket_name = AWS_STORAGE_BUCKET_NAME
            prefix = 'uploaded_Files/'
            response = s3.list_objects_v2(Bucket=bucket_name,Prefix=prefix)
            files = []
            download_urls = []
            if 'Contents' in response:
                for file in response['Contents']:
                    key = file['Key'].removeprefix(prefix)
                    files.append(key)
                    print(key)
                    download_url = s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket_name, 'Key': file['Key']},
                        ExpiresIn=3600  # İndirme URL'sinin geçerlilik süresi (saniye cinsinden)
                    )
                    download_urls.append(download_url)
        
            context={
            'files': files,
            'download_urls': download_urls,
            'success': True
            }

            return render(request,'file_process.html', context)
        except Exception as e:
            context={'success': False, 'error': str(e)}
            return  render(request,'file_process.html', context)

    return redirect('file_process')

def download_file(request,file_name):
    s3 = boto3.client(service_name='s3', region_name=AWS_S3_REGION_NAME,
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    prefix = 'uploaded_Files/'  
    file_name = urllib.parse.unquote(file_name)              
    file_key = prefix+file_name.strip('/')  # İndirmek istediğiniz dosyanın adını buraya yazın
    print("hey"+file_key)
    response = s3.get_object(Bucket='testbucket-burak1', Key=file_key)
    file_contents = response['Body'].read()
    
    # İndirilen dosyayı istemciye gönder
    response = HttpResponse(file_contents, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment;  filename="{}"'.format(file_name)
    
    return response