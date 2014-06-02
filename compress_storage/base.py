# -*- coding: utf-8 -*-
try:
    from celery.task import task
except ImportError:
    task = None

import os
from django.conf import settings
from django.db.models.fields.files import FieldFile

FILE_COMPRESS_DELETE_OLD_FILE = getattr(settings, 'FILE_COMPRESS_DELETE_OLD_FILE', True)


class CompressFieldFile(FieldFile):
    compress_ext = None

    def _is_compressed(self):
        basename, ext = os.path.splitext(self.name)
        compress_ext = '.' + self.compress_ext
        return compress_ext == ext
    is_compressed = property(_is_compressed)

    def _compress_name(self):
        basename, ext = os.path.splitext(self.name)
        return basename + ('.' + self.compress_ext)
    compress_name = property(_compress_name)

    def _compress_full_name(self):
        basename, ext = os.path.splitext(self.file.name)
        return basename + ('.' + self.compress_ext)
    compress_full_name = property(_compress_full_name)

    def compress_content(self):
        """
        Method to change for new implementations
        """
        raise NotImplementedError()

    def _update_filefield_name(self, delete_old_file=True):
        # update field value
        old_name = self.name

        setattr(self.instance, self.field.name, self.compress_name)
        self.instance.save()

        if delete_old_file:
            self.file.close()
            self.storage.delete(old_name)

    def compress(self, async=True, delete_old_file=FILE_COMPRESS_DELETE_OLD_FILE):
        if async and task:
            file_content = task(self.compress_content).delay()
        else:
            file_content = self.compress_content()

        self._update_filefield_name(delete_old_file=delete_old_file)

        return file_content
