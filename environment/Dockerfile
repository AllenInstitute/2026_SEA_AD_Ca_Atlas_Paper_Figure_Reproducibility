# hash:sha256:23ec1e063f1984c853eb441a564a665717e62342012b628963fa2cbb5ab00847
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/pytorch:2.4.0-cuda12.4.0-mambaforge24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-askpass /

RUN conda install -y \
        jupyterlab==4.5.1 \
    && conda clean -ya

RUN mamba install -y \
        cudnn==9.3.0.75 \
        cusparselt==0.6.3.2 \
        cutensor==2.0.2.5 \
        leidenalg==0.10.2 \
        louvain==0.8.2 \
        pymde==0.1.18 \
        rapidsai::rapids \
        scipy==1.14.1 \
    && mamba clean -ya

RUN pip install -U --no-cache-dir \
    rapids-singlecell==0.13.5 \
    scanpy==1.10.4 \
    sopa==2.1.10 \
    spatialdata-plot==0.2.13
