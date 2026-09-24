import io
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from app import app
from compressor import CompressionError, compress_pdf


class WebTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_and_health(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/health').json, {'status': 'ok'})

    def test_missing_or_wrong_file(self):
        for data in ({}, {'file': (io.BytesIO(b'hello'), 'test.txt')},
                     {'file': (io.BytesIO(b'hello'), 'test.pdf')}):
            self.assertEqual(self.client.post('/compress', data=data).status_code, 400)

    def test_size_limit(self):
        with patch.dict(app.config, MAX_CONTENT_LENGTH=100):
            response = self.client.post('/compress', data={'file': (io.BytesIO(b'x' * 101), 'test.pdf')})
        self.assertEqual(response.status_code, 413)
        self.assertIn('error', response.json)


class CompressionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.source = Path(self.directory.name) / 'input.pdf'
        self.output = Path(self.directory.name) / 'output.pdf'
        self.source.write_bytes(b'%PDF-1.4\nplaceholder')

    def test_same_path_and_invalid_quality(self):
        with self.assertRaises(CompressionError):
            compress_pdf(self.source, self.source)
        with self.assertRaises(CompressionError):
            compress_pdf(self.source, self.output, 'invalid')

    def test_failure_preserves_existing_destination(self):
        self.output.write_bytes(b'existing document')
        with patch('compressor.shutil.which', return_value='/usr/bin/gs'), patch(
            'compressor.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'gs')
        ):
            with self.assertRaises(CompressionError):
                compress_pdf(self.source, self.output)
        self.assertEqual(self.output.read_bytes(), b'existing document')
        self.assertEqual(len(list(self.source.parent.iterdir())), 2)

    def test_timeout_and_missing_dependency(self):
        with patch('compressor.shutil.which', return_value=None):
            with self.assertRaisesRegex(CompressionError, 'introuvable'):
                compress_pdf(self.source, self.output)
        with patch('compressor.shutil.which', return_value='/usr/bin/gs'), patch(
            'compressor.subprocess.run', side_effect=subprocess.TimeoutExpired('gs', 120)
        ):
            with self.assertRaisesRegex(CompressionError, '120 secondes'):
                compress_pdf(self.source, self.output)

    def test_larger_output_keeps_original(self):
        def write_output(command, **kwargs):
            path = next(arg.split('=', 1)[1] for arg in command if arg.startswith('-sOutputFile='))
            Path(path).write_bytes(b'%PDF-' + b'x' * 1000)
        with patch('compressor.shutil.which', return_value='/usr/bin/gs'), patch(
            'compressor.subprocess.run', side_effect=write_output
        ):
            compress_pdf(self.source, self.output)
        self.assertEqual(self.output.read_bytes(), self.source.read_bytes())

    @unittest.skipUnless(shutil.which('gs'), 'Ghostscript is required')
    def test_real_pdf_all_qualities_and_download(self):
        subprocess.run(['gs', '-q', '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite',
                        f'-sOutputFile={self.source}', '-c',
                        '/Helvetica findfont 24 scalefont setfont 72 720 moveto (PDF Toolkit) show showpage'],
                       check=True, capture_output=True)
        original = self.source.read_bytes()
        for quality in ('screen', 'ebook', 'printer', 'prepress'):
            with self.subTest(quality=quality):
                response = app.test_client().post('/compress', data={
                    'file': (io.BytesIO(original), '../../test.pdf'), 'quality': quality,
                })
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, 'application/pdf')
                self.assertTrue(response.data.startswith(b'%PDF-'))
                self.assertLessEqual(len(response.data), len(original))
                self.assertIn('test-compresse.pdf', response.headers['Content-Disposition'])
                self.assertEqual(response.headers['Cache-Control'], 'no-store')
                self.output.write_bytes(response.data)
                subprocess.run(['gs', '-q', '-dBATCH', '-dNOPAUSE', '-sDEVICE=nullpage', str(self.output)],
                               check=True, capture_output=True)
                response.close()
        self.assertEqual(self.source.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
