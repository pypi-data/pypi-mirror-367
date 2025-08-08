import pytest
import requests
from unittest.mock import patch, MagicMock
from revdownloader.downloader import BitFlush, download, autosave, loadsave, clearsave, sizeof_fmt, genbar

# Test para la clase BitFlush
class TestBitFlush:
    @patch('revdownloader.downloader.requests.Session')
    def test_login_success(self, mock_session):
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.text = 'Área personal'
        mock_session.return_value.get.return_value = mock_response

        flush = BitFlush()
        result = flush._login()
        assert result is True
        assert flush.sesskey is not None

    @patch('revdownloader.downloader.requests.Session')
    def test_login_failure(self, mock_session):
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.text = 'Error de inicio de sesión'
        mock_session.return_value.get.return_value = mock_response

        flush = BitFlush()
        result = flush._login()
        assert result is False
        assert flush.sesskey is None

    @patch('revdownloader.downloader.requests.Session')
    def test_delete_calendar(self, mock_session):
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'success'}
        mock_session.return_value.post.return_value = mock_response

        flush = BitFlush()
        flush.sesskey = 'test_sesskey'
        result = flush._delete_calendar(eventid=123)
        assert result['status'] == 'success'

# Test para la función download
class TestDownload:
    @patch('revdownloader.downloader.requests.Session')
    def test_download_success(self, mock_session):
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'part1', b'part2']
        mock_session.return_value.head.return_value = mock_response
        mock_session.return_value.get.return_value = mock_response

        filename = 'test_file'
        urls = ['http://example.com/file_part1', 'http://example.com/file_part2']
        total_size, error = download(filename, mock_session, urls)

        assert total_size == 1024
        assert error is None

    @patch('revdownloader.downloader.requests.Session')
    def test_download_error(self, mock_session):
        # Configurar el mock para simular un error
        mock_session.return_value.head.side_effect = requests.exceptions.RequestException

        filename = 'test_file'
        urls = ['http://example.com/file_part1']
        total_size, error = download(filename, mock_session, urls)

        assert total_size == 0
        assert error == "DOWNLOAD_ERROR_404"

# Test para las funciones auxiliares
def test_autosave_loadsave():
    autosave(token='test_token')
    saved_data = loadsave()
    assert saved_data['token'] == 'test_token'

    clearsave()
    assert loadsave()['token'] is None

def test_sizeof_fmt():
    assert sizeof_fmt(1024) == '1.00KiB'
    assert sizeof_fmt(1048576) == '1.00MiB'

def test_genbar():
    assert genbar(0) == '⟦▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢⟧'
    assert genbar(50) == '⟦▣▣▣▣▣▣▣▣▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢⟧'
    assert genbar(100) == '⟦▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣▣⟧'

if __name__ == "__main__":
    pytest.main()
