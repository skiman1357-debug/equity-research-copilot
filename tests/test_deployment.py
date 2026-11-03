from pathlib import Path
from unittest.mock import Mock, MagicMock
import io
import xml.etree.ElementTree as ET
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest
import agent
import openai
import deployment


@pytest.mark.parametrize('provided,expected,result', [
    ('', '', False), ('wrong', 'secret', False),
    ('secret', 'secret', True), ('żółć', 'żółć', True),
])
def test_access_code(provided, expected, result):
    assert deployment.access_allowed(provided, expected) is result


def test_download_invalid_xml_leaves_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(deployment.urllib.request, 'urlopen', lambda *a, **k: io.BytesIO(b'not XML'))
    target = tmp_path / 'report.xhtml'
    with pytest.raises(ET.ParseError):
        deployment.download_report('https://example.test/report', target)
    assert not target.exists()
    assert not list(tmp_path.glob('*.part'))


def test_download_too_large_leaves_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(deployment, 'MAX_REPORT_BYTES', 4)
    monkeypatch.setattr(deployment.urllib.request, 'urlopen', lambda *a, **k: io.BytesIO(b'<root/>'))
    target = tmp_path / 'report.xhtml'
    with pytest.raises(ValueError):
        deployment.download_report('https://example.test/report', target)
    assert not target.exists()
    assert not list(tmp_path.glob('*.part'))


def test_download_valid_xml(tmp_path, monkeypatch):
    monkeypatch.setattr(deployment.urllib.request, 'urlopen', lambda *a, **k: io.BytesIO(b'<root/>'))
    target = tmp_path / 'report.xhtml'
    deployment.download_report('https://example.test/report', target)
    assert target.read_bytes() == b'<root/>'


def test_prepare_data_downloads_only_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(deployment, 'REPORTS_DIR', tmp_path)
    monkeypatch.setattr(deployment, 'REPORT_FILES', ['a.xhtml', 'b.xhtml'])
    (tmp_path / 'a.xhtml').write_text('<root/>')
    setup, download = Mock(), Mock()
    monkeypatch.setattr(deployment, 'setup_database', setup)
    monkeypatch.setattr(deployment, 'download_report', download)
    monkeypatch.setattr(deployment, 'read_report', lambda _: [{'text': 'report'}])
    deployment.prepare_data()
    setup.assert_called_once()
    download.assert_called_once_with(deployment.REPORT_BASE_URL + 'b.xhtml', tmp_path / 'b.xhtml')


def make_app():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'))
    app.secrets['XAI_API_KEY'] = 'fake-test-key'
    app.secrets['XAI_MODEL'] = 'test-model'
    app.secrets['DEMO_ACCESS_CODE'] = 'test-access'
    return app


def test_public_demo_does_not_initialize_or_call_api(monkeypatch):
    prepare, run = Mock(), Mock()
    monkeypatch.setattr(deployment, 'prepare_data', prepare)
    monkeypatch.setattr(agent, 'run_agent', run)
    app = make_app().run()
    assert not app.exception
    assert 'Zapisane podsumowanie' in app.info[0].value
    prepare.assert_not_called()
    run.assert_not_called()


def test_invalid_access_cannot_start_analysis(monkeypatch):
    prepare, run = Mock(), Mock()
    monkeypatch.setattr(deployment, 'prepare_data', prepare)
    monkeypatch.setattr(agent, 'run_agent', run)
    app = make_app().run()
    app.radio[0].set_value('Analiza na żywo').run()
    app.text_input[0].set_value('wrong')
    app.button[0].click().run()
    assert not app.exception
    assert app.error[0].value == 'Nieprawidłowy kod dostępu.'
    prepare.assert_not_called()
    run.assert_not_called()


def test_valid_access_runs_and_renders_answer(monkeypatch):
    st.cache_resource.clear()
    monkeypatch.setattr(openai, 'OpenAI', MagicMock())
    prepare = Mock()
    run = Mock(return_value='Testowa odpowiedź')
    monkeypatch.setattr(deployment, 'prepare_data', prepare)
    monkeypatch.setattr(agent, 'run_agent', run)
    app = make_app().run()
    app.radio[0].set_value('Analiza na żywo').run()
    app.text_input[0].set_value('test-access')
    app.button[0].click().run()
    assert not app.exception
    prepare.assert_called_once()
    run.assert_called_once()
    assert any(x.value == 'Testowa odpowiedź' for x in app.markdown)
    st.cache_resource.clear()


def test_live_disabled_without_code(monkeypatch):
    monkeypatch.delenv('DEMO_ACCESS_CODE', raising=False)
    run = Mock()
    monkeypatch.setattr(agent, 'run_agent', run)
    app = make_app()
    app.secrets['DEMO_ACCESS_CODE'] = ''
    app.run().radio[0].set_value('Analiza na żywo').run()
    assert not app.exception
    assert not app.button
    run.assert_not_called()
