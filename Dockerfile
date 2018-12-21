FROM amazonlinux:1 as builder
RUN yum -y install \
    https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum -y install python36 python36-pip python36-devel gcc sudo
COPY requirements.txt /root/
RUN pip-3.6 install wheel && pip-3.6 wheel --wheel-dir=/root/wheel -r \
    /root/requirements.txt

FROM amazonlinux:1 as production
COPY --from=builder /root/wheel /root/wheel
COPY requirements.txt /root/
COPY ipsec_exporter /opt/ipsec_exporter
COPY scripts/check_ipsec /usr/local/bin
RUN yum -y install \
    https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum -y install install python36 python36-pip python36-devel sudo openswan \
    which fping sudo && pip-3.6 install --no-index --find-links=/root/wheel -r \
    /root/requirements.txt && chmod +x /usr/local/bin/check_ipsec && rm -r \
    /root/wheel/ /root/requirements.txt /var/cache
ENTRYPOINT ["python3", "/opt/ipsec_exporter/main.py"]
