from pyfiglet import Figlet
from application.utils import banner


def test_banner_runs():
    try:
        banner()
        assert True
    except Exception:
        assert False


def test_ascii_contains_nbc():
    f = Figlet(font="dos_rebel")
    ascii_art = f.renderText("NBC")
    assert "N" in ascii_art and "B" in ascii_art and "C" in ascii_art
