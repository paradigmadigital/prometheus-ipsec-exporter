FROM amazonlinux:2 as builder
RUN yum -y install \
    https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum -y install python3 python3-pip python3-devel gcc sudo
COPY requirements.txt /root/
RUN pip-3 install wheel && pip-3 wheel --wheel-dir=/root/wheel -r \
    /root/requirements.txt

FROM amazonlinux:2 as production
COPY --from=builder /root/wheel /root/wheel
COPY requirements.txt /root/
RUN yum -y install \
    https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum -y install install python3 python3-pip python3-devel sudo openswan \
    which fping sudo && pip-3 install --no-index --find-links=/root/wheel -r \
    /root/requirements.txt
COPY ipsec_exporter /opt/ipsec_exporter
COPY scripts/check_ipsec /usr/local/bin
RUN rm -r /root/wheel/ /root/requirements.txt /var/cache && chmod +x /usr/local/bin/check_ipsec
ENTRYPOINT ["python3", "/opt/ipsec_exporter/main.py"]
