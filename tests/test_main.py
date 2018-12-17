import unittest.mock
import pytest
from ipsec_exporter.main import IpsecExporter


class TestIpsecExporter(unittest.TestCase):
    def setUp(self):
        self.flask_patch = unittest.mock.patch('ipsec_exporter.main.Flask')
        self.devnull_patch = unittest.mock.patch('ipsec_exporter.main.devnull')
        self.open_patch = unittest.mock.patch('ipsec_exporter.main.open',
                                              autospect=True)
        self.glob_patch = unittest.mock.patch('ipsec_exporter.main.glob.glob')
        self.exit_patch = unittest.mock.patch('ipsec_exporter.main.exit')
        self.gauge_patch = unittest.mock.patch('ipsec_exporter.main.Gauge')
        self.generate_latest_patch = unittest.mock.patch(
            'ipsec_exporter.main.generate_latest'
        )

        self.flask = self.flask_patch.start()
        self.devnull = self.devnull_patch.start()
        self.open = self.open_patch.start()
        self.glob = self.glob_patch.start()
        self.exit = self.exit_patch.start()
        self.gauge = self.gauge_patch.start()
        self.generate_latest = self.generate_latest_patch.start()

    def tearDown(self):
        self.flask.stop()
        self.devnull.stop()
        self.open.stop()
        self.glob.stop()
        self.exit.stop()
        self.gauge.stop()
        self.generate_latest.stop()

    @unittest.mock.patch('ipsec_exporter.main.IpsecExporter.run_webserver')
    @unittest.mock.patch('ipsec_exporter.main.IpsecExporter.get_connections')
    def test_init_fail(self, connections, webserver):
        connections.return_value = []
        IpsecExporter()
        self.flask.assert_called_once_with('ipsec_exporter.main')
        assert self.open.call_count == 1
        assert connections.call_count == 1
        self.exit.assert_called_once_with(1)

    @unittest.mock.patch('ipsec_exporter.main.IpsecExporter.run_webserver')
    @unittest.mock.patch('ipsec_exporter.main.IpsecExporter.get_connections')
    def test_init_correct(self, connections, webserver):
        connections.return_value = ['/etc/ipsec.d/myconnection.conf']
        IpsecExporter()
        self.flask.assert_called_once_with('ipsec_exporter.main')
        assert self.open.call_count == 1
        assert connections.call_count == 1
        assert self.exit.call_count == 0
        assert webserver.call_count == 1

    @unittest.mock.patch('ipsec_exporter.main.IpsecExporter.run_webserver')
    def test_get_connections(self, webserver):
        self.glob.return_value = ['/etc/ipsec.d/myconnection.conf']
        self.open().readlines.return_value = ['conn myconnection', 'nope']

        IpsecExporter()
        assert self.exit.call_count == 0
        assert webserver.call_count == 1
        # It's three and not two because it adds the call to readlines
        assert self.open.call_count == 3
        self.gauge.assert_called_once_with(
            "ipsec_myconnection",
            "Output from the check_ipsec script"
        )

    @unittest.mock.patch('ipsec_exporter.main.IpsecExporter.serve_metrics')
    @unittest.mock.patch('ipsec_exporter.main.IpsecExporter.get_connections')
    def test_run_webserver(self, connections, serve_metrics):
        connections.return_value = ['/etc/ipsec.d/myconnection.conf']
        IpsecExporter()
        assert self.exit.call_count == 0
        assert serve_metrics.call_count == 1
        # TODO test self.flask.run

    @pytest.mark.skip(reason="it's in the TODO list")
    def test_serve_metrics(self):
        pass
