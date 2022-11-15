FROM quay.io/astronomer/astro-runtime:6.0.4

RUN git clone https://github.com/Homebrew/brew ~/.linuxbrew/Homebrew \
&& mkdir ~/.linuxbrew/bin \
&& ln -s ../Homebrew/bin/brew ~/.linuxbrew/bin \
&& eval $(~/.linuxbrew/bin/brew shellenv) \
&& brew --version
RUN brew install librdkafka
ENV C_INCLUDE_PATH=/opt/homebrew/Cellar/librdkafka/1.8.2/include
ENV LIBRARY_PATH=/opt/homebrew/Cellar/librdkafka/1.8.2/lib