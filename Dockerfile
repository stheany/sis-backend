FROM python:3.10.4-alpine
ENV LD_LIBRARY_PATH=/lib
ENV PYTHONUNBUFFERED 1
RUN mkdir /src
# set work directory
WORKDIR /src
RUN wget https://download.oracle.com/otn_software/linux/instantclient/216000/instantclient-basic-linux.x64-21.6.0.0.0dbru.zip && \
    unzip instantclient-basic-linux.x64-21.6.0.0.0dbru.zip && \
    cp -r instantclient_21_6/* /lib && \
    rm -rf instantclient-basic-linux.x64-21.6.0.0.0dbru.zip && \
    apk add libaio libnsl libc6-compat && \
    cd /lib && \
    ln -s /lib64/* /lib && \
    ln -s libnsl.so.2 /usr/lib/libnsl.so.1 && \
    ln -s libc.so /usr/lib/libresolv.so.2
RUN apk add --no-cache gcc musl-dev linux-headers
ADD requirements.txt /src/
RUN pip install --upgrade pip
RUN pip install --no-build-isolation cx-Oracle==8.3.0
RUN pip install -r requirements.txt