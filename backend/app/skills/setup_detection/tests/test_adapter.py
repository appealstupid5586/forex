from backend.app.skills.setup_detection import detect_setup


def test_detect_setup_import():
    assert callable(detect_setup)
