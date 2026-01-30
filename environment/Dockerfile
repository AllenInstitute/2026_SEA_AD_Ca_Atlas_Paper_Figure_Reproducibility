# hash:sha256:077fe67842538f9c69696457033c92f01da0fa4b342a23c695bbeba70d25ccd9
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/pytorch:2.4.0-cuda12.4.0-mambaforge24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-askpass /

RUN mamba install -y \
        cudnn==9.10.2.21 \
        cusparselt==0.8.1.1 \
        cutensor==2.4.1.4 \
        jupyter==1.1.1 \
        leidenalg==0.10.2 \
        libsqlite==3.51.2 \
        louvain==0.8.2 \
        pymde==0.1.18 \
        rapidsai::rapids \
        scipy==1.17.0 \
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
