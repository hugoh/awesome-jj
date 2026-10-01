from unittest.mock import patch

from awesome_jj_tools.cli import main


def test_discovery_report_exits_2_when_a_sweep_crashes(capsys):
    with patch("awesome_jj_tools.discover.run", side_effect=RuntimeError("boom")):
        assert main(["discovery-report"]) == 2
    assert "RuntimeError: boom" in capsys.readouterr().err
