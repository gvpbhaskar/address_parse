FROM ubuntu:latest

ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
        && apt-get update \
	&& apt-get install -y --no-install-recommends openssh-server \
	&& echo "$SSH_PASSWD" | chpasswd 

# LIBPOSTAL
# Install Libpostal dependencies
RUN apt-get update && \
	apt-get install -y \
		make \
		curl \
		autoconf \
		automake \
		libtool \
		pkg-config \
		python3-pip

# Download libpostal source to /usr/local/libpostal-1.1-alpha
RUN cd /usr/local && curl -sL https://github.com/openvenues/libpostal/archive/v1.1-alpha.tar.gz | tar -xz


# Create Libpostal data directory at /var/libpostal/data
RUN cd /var && \
	mkdir libpostal && \
	cd libpostal && \
	mkdir data

# Install Libpostal from source
RUN cd /usr/local/libpostal-1.1-alpha && \
	./bootstrap.sh && \
	./configure --datadir=/var/libpostal/data && \
	make -j4 && \
	make install && \
	ldconfig
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip3 install -r requirements.txt
ADD . /code/

# Install Libpostal python Bindings
ADD country_addvers.txt world-cities.txt /code/
COPY sshd_config /etc/ssh/
COPY init.sh /usr/local/bin/
RUN chmod u+x /usr/local/bin/init.sh
EXPOSE 5000 2222
ENTRYPOINT ["init.sh"]
