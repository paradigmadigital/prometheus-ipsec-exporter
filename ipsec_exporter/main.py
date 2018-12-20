#!/usr/bin/env python

import subprocess
import glob
import re
from sys import exit
from os import devnull
from flask import Flask, Response
from prometheus_client import Gauge, generate_latest


class IpsecExporter:
    def __init__(self):
        self.app = Flask(__name__)
        self.devnull = open(devnull, "w")
        self.connections = self.get_connections()
        if not self.connections:
            print("There's no files in /etc/ipsec.d/")
            exit(1)
        self.gauge = Gauge("ipsec_tunnel_status",
                           "Output from the check_ipsec script",
                           ["connection_name"])
        self.run_webserver()

    def get_connections(self):
        "Get ipsec's connection name with it's initialized prometheus gauge."
        ipsec_conf_files = glob.glob("/etc/ipsec.d/*.conf")
        connections = []

        for ipsec_conf_file in ipsec_conf_files:
            # Read all files on /etc/ipsec.d/*.conf
            f = open(ipsec_conf_file)
            lines = f.readlines()
            f.close()

            # Get all lines that match with the next regex
            r = re.compile("^conn")

            # Assume there"s only one conn per file and change some chars
            connection = list(
                filter(r.match, lines)
            )[0].split(" ")[1].replace("-", "_").replace("\n", "")

            connections.append(connection)

        return connections

    def serve_metrics(self):
        "Main method to serve the metrics."
        connections = self.connections
        devnull = self.devnull
        gauge = self.gauge

        @self.app.route("/metrics")
        def metrics():
            """
            Flask endpoint to expose the prometheus metrics. With every request
            it gets, it executes the 'check_ipsec' command.
            """
            for conn in connections:
                ipsec_process = subprocess.call(["check_ipsec", conn],
                                                stdout=devnull,
                                                stderr=subprocess.STDOUT)
                gauge.labels(conn).set(ipsec_process)

            metrics = generate_latest()

            return Response(metrics,
                            mimetype='text/plain',
                            content_type='text/plain; charset=utf-8')

    def run_webserver(self):
        "Start the web application."
        self.serve_metrics()
        self.app.run(
            port="9000",
            host="0.0.0.0",
            use_reloader=False,
            debug=False
        )


if __name__ == "__main__":
    IpsecExporter()
