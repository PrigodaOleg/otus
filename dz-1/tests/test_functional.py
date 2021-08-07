import log_analyzer
import sys


def test_args():
    old_args = sys.argv
    sys.argv = [old_args[0]]
    try:
        config = log_analyzer.get_config()
        assert config['REPORT_SIZE'] == -1

        sys.argv += ['--report_size', '100']
        config = log_analyzer.get_config()
        assert config['REPORT_SIZE'] == 100
    finally:
        sys.argv = old_args