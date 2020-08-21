FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update
RUN apt-get -y update && apt-get -y install gcc \
	 g++ \
     git \
     zlib1g-dev

COPY ./ /kb/module
RUN mkdir -p /kb/module/deps

WORKDIR /kb/module/deps
RUN git clone https://github.com/lh3/wgsim.git
WORKDIR /kb/module/deps/wgsim
RUN gcc -g -O2 -Wall -o wgsim wgsim.c -lz -lm

# -----------------------------------------

RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
