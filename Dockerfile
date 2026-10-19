# Anaxia, the BLLM engine: the eBLLM package in one image, with the Lean 4 library built, the C,
# C++ and Python checks, the target agents, the memory store, the task suite, the experiments and
# the BLLM paper.
#
#   docker pull ghcr.io/creelie/bllm-engine:latest
#   docker run --rm ghcr.io/creelie/bllm-engine --version
#   docker run --rm -it --entrypoint bash ghcr.io/creelie/bllm-engine
#
# Every merge to main rebuilds and republishes the image; when it starts, the engine compares
# itself with the published `latest` and prints the pull command if that is newer
# (ANAXIA_NO_UPDATE_CHECK=1 turns this off; `anaxia update` asks explicitly).
#
# Julia and the GPU stack of experiments/finetune (torch, transformers, peft, llama-cpp-python)
# are not in the image; install them on top when they are needed.
FROM python:3.12-slim

ARG VERSION=dev
ARG REVISION=
ARG CREATED=
LABEL org.opencontainers.image.title="Anaxia" \
      org.opencontainers.image.description="Anaxia, the BLLM engine: verifier-gated conjecture closure and the BLLM crossing network (eBLLM), with its Lean 4 library, checks, target agents, memory and the BLLM paper" \
      org.opencontainers.image.authors="Deep Bhattacharjee <d.bhattacharjee@erl-forschung.de>" \
      org.opencontainers.image.vendor="Deep Bhattacharjee" \
      org.opencontainers.image.source="https://github.com/creelie/eBLLM" \
      org.opencontainers.image.url="https://github.com/creelie/eBLLM" \
      org.opencontainers.image.documentation="https://github.com/creelie/eBLLM#readme" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${REVISION}" \
      org.opencontainers.image.created="${CREATED}"

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential ca-certificates curl git \
 && rm -rf /var/lib/apt/lists/*

ENV ELAN_HOME=/opt/elan \
    PATH=/opt/elan/bin:$PATH \
    EBLLM_HOME=/opt/bllm-engine \
    ANAXIA_IMAGE=1 \
    ANAXIA_VERSION=${VERSION} \
    ANAXIA_REVISION=${REVISION} \
    ANAXIA_CREATED=${CREATED} \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /opt/bllm-engine

# the Lean toolchain pinned by the library, installed before the sources so that it is cached
COPY lean/lean-toolchain lean/lean-toolchain
RUN curl -sSfL -o /tmp/elan-init.sh https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
 && sh /tmp/elan-init.sh -y --no-modify-path --default-toolchain "$(cat lean/lean-toolchain)" \
 && rm /tmp/elan-init.sh \
 && lean --version

RUN pip install --no-cache-dir numpy python-sat pyyaml networkx

COPY . .
RUN pip install --no-cache-dir . \
 && rm -rf build src/*.egg-info \
 && (cd lean && lake build) \
 && ANAXIA_NO_UPDATE_CHECK=1 anaxia --version \
 && chmod -R a+rX /opt/elan /opt/bllm-engine

ENTRYPOINT ["anaxia"]
CMD ["--help"]
