FROM ubuntu-upstart:14.04
MAINTAINER MidoNet (http://midonet.org)

ONBUILD ADD conf/midonet.list /etc/apt/sources.list.d/midonet.list
ONBUILD ADD bin/run-midolman.sh /run-midolman.sh

ONBUILD RUN curl -k http://repo.midonet.org/packages.midokura.key | apt-key add -
ONBUILD RUN apt-get -qy update
ONBUILD RUN apt-get install -qy midolman zkdump python-setproctitle

RUN apt-get -qy update
RUN apt-get -qy install git mz tcpdump nmap iptables --no-install-recommends

# Install Zulu Java 8
RUN apt-get install -qy software-properties-common
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0x219BD9C9
RUN apt-add-repository 'deb http://repos.azulsystems.com/ubuntu stable main'
RUN apt-get update && apt-get install -qy zulu-8

# Get pipework to allow arbitrary configurations on the container from the host
# Might get included into docker-networking in the future
RUN git clone http://github.com/jpetazzo/pipework /pipework
RUN mv /pipework/pipework /usr/bin/pipework

# Workaround to circumvent limitations with AppArmor profiles and docker
RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump
RUN mv /sbin/dhclient /usr/bin/dhclient

RUN apt-get update && apt-get install -qy curl && apt-get install -qy git

# Expose bgpd port in case it's a gateway
EXPOSE 179

CMD ["/run-midolman.sh"]
