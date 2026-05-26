# hash:sha256:ba804dfe947ef8f4adb6f4ae2350f8bcf2c6a9b793cf6d065f6fb97b3b89e72a
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/pytorch:2.4.0-cuda12.4.0-mambaforge24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN mamba install -y \
        cudnn==9.10.2.21 \
        cusparselt==0.8.1.1 \
        cutensor==2.4.1.4 \
        jupyter==1.1.1 \
        leidenalg==0.10.2 \
        libsqlite==3.51.2 \
        louvain==0.8.2 \
        pymde==0.1.18 \
        rapidsai::rapids==25.08.00 \
        scipy==1.16.3 \
        sqlite==3.51.2 \
    && mamba clean -ya

RUN pip install -U --no-cache-dir \
    igraph==1.0.0 \
    rapids-singlecell==0.13.5 \
    scanpy==1.12 \
    spatialdata==0.6.1 \
    spatialdata-plot==0.2.13

ADD "https://github.com/coder/code-server/releases/download/v4.100.3/code-server-4.100.3-linux-amd64.tar.gz" /.code-server/code-server.tar.gz
	
RUN cd /.code-server \
    && tar -xvf code-server.tar.gz \
    && rm code-server.tar.gz \
    && ln -s /.code-server/code-server-4.100.3-linux-amd64/bin/code-server /usr/bin/code-server \
    && mkdir -p /.vscode/extensions

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
