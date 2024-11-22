from juju.status import StatusStr, severity_map


def test_status_str_values():
    for name, value in StatusStr._member_map_.items():
        assert name == value


def test_severity_map():
    assert set(StatusStr._member_names_) == set(severity_map)
