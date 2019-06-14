FROM balenalib/rpi-raspbian

RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    git \
    libglib2.0-dev \
    bluez

RUN pip3 install bluepy datetime

WORKDIR /app
RUN git clone https://github.com/hassiweb/mitemp.git
RUN git clone https://github.com/ChristianKuehnel/btlewrap.git
RUN mv /app/btlewrap-git/btlewrap /app/mitemp/
RUN rm -rf /app/btlewrap-git

CMD ["bash"]
