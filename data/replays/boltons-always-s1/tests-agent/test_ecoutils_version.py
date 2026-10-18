import datetime

from boltons import ecoutils


def test_eco_version():
    assert ecoutils.ECO_VERSION == '1.1.0'
    assert ecoutils.get_profile()['_eco_version'] == '1.1.0'


def test_version_history_documented():
    assert '1.1.0' in ecoutils.__doc__ or '1.1.0 - ' in open(ecoutils.__file__).read()


def test_no_get_utc_now_helper():
    assert not hasattr(ecoutils, '_get_utc_now')


def test_start_time_info_is_aware_utc():
    dt = datetime.datetime.fromisoformat(ecoutils.START_TIME_INFO['time_utc'])
    assert dt.utcoffset() == datetime.timedelta(0)


def test_start_time_info():
    info = ecoutils.START_TIME_INFO
    assert str(datetime.datetime.fromisoformat(info['time_utc'])) == info['time_utc']
    assert isinstance(info['time_utc_offset'], float)


def test_linux_dist_keys_present():
    p = ecoutils.get_profile()
    for k in ('linux_dist_name', 'linux_dist_version'):
        assert k in p
