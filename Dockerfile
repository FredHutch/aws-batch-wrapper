FROM fredhutch/fredhutch-ubuntu:16.04_20171030

RUN apt-get update -y

RUN apt-get install -y ca-certificates mdadm curl unzip

RUN curl https://s3-us-west-2.amazonaws.com/fredhutch-aws-batch-tools/linux-build-of-batchit/batchit > /usr/local/bin/batchit

RUN chmod a+x /usr/local/bin/batchit

# about gosu: https://docs.docker.com/engine/reference/builder/#exec-form-entrypoint-example
#RUN curl -LO https://github.com/tianon/gosu/releases/download/1.10/gosu-amd64 > /usr/local/bin/gosu

#RUN chmod a+x /usr/local/bin/gosu

RUN curl -LO https://github.com/awslabs/aws-batch-helpers/archive/master.zip && \
    unzip master.zip && \
    cp aws-batch-helpers-master/fetch-and-run/fetch_and_run.sh /usr/local/bin && \
    rm -rf aws-batch-helpers-master master.zip


ADD ./entrypoint_linux /usr/local/bin/entrypoint


ENTRYPOINT ["/usr/local/bin/entrypoint"]
