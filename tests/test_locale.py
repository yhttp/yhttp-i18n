from yhttp.ext.i18n import Locale


def test_locale_rtl():
    assert Locale('fa').rtl
    assert Locale('ar').rtl
    assert Locale('he').rtl
    assert Locale('ps').rtl
    assert Locale('sd').rtl
    assert Locale('ur').rtl
    assert Locale('yi').rtl
    assert Locale('dv').rtl
    assert Locale('ha').rtl
    assert Locale('ks').rtl
    assert Locale('ku').rtl
    assert Locale('tk').rtl
    assert Locale('ug').rtl

    assert not Locale('en').rtl
    assert not Locale('fr').rtl
    assert not Locale('es').rtl
