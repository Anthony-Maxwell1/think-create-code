from django.http import HttpResponse
from zipfile import ZipFile, ZIP_DEFLATED

class ZipFileResponse(HttpResponse):
    content_type = 'application/octet-stream'
    
    def __init__(self, filename='file.zip', content_encoding='utf-8', *args, **kwargs):
        kwargs.setdefault('content_type', self.content_type)
        super(ZipFileResponse, self).__init__(*args, **kwargs)
        self['Content-Disposition'] = 'attachment; filename=%s' % filename
        self._zipfile = ZipFile(file=self, mode='w', compression=ZIP_DEFLATED)
        self._filename = None
        self._content_encoding = content_encoding

    def append(self, filename, content):
        if self._content_encoding:
            content = content.encode(self._content_encoding)
        self._zipfile.writestr(filename, content)

    def close(self):
        self._zipfile.close()
