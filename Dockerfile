# BLLM Engine: the eBLLM package in one image, with the Lean 4 library built, the C, C++ and
# Python checks, the target agents, the memory store, the task suite and the experiments.
#
#   docker run --rm ghcr.io/creelie/bllm-engine --help
#   docker run --rm ghcr.io/creelie/bllm-engine gap
#   docker run --rm -it --entrypoint bash ghcr.io/creelie/bllm-engine
#
# Julia and the GPU stack of experiments/finetune (torch, transformers, peft, llama-cpp-python)
# are not in the image; install them on top when they are needed.
FROM python:3.12-slim

ARG VERSION=dev
LABEL org.opencontainers.image.title="BLLM Engine" \
      org.opencontainers.image.description="BLLM Engine: verifier-gated conjecture closure and the BLLM crossing network (eBLLM), with its Lean 4 library, checks, target agents and memory" \
      org.opencontainers.image.authors="Deep Bhattacharjee <d.bhattacharjee@erl-forschung.de>" \
      org.opencontainers.image.vendor="Deep Bhattacharjee" \
      org.opencontainers.image.source="https://github.com/creelie/eBLLM" \
      org.opencontainers.image.url="https://github.com/creelie/eBLLM" \
      org.opencontainers.image.documentation="https://github.com/creelie/eBLLM#readme" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${VERSION}"

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential ca-certificates curl git \
 && rm -rf /var/lib/apt/lists/*

ENV ELAN_HOME=/opt/elan \
    PATH=/opt/elan/bin:$PATH \
    EBLLM_HOME=/opt/bllm-engine \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /opt/bllm-engine

# the Lean toolchain pinned by the library, installed before the sources so that it is cached
COPY lean/lean-toolchain lean/lean-toolchain
RUN curl -sSfL -o /tmp/elan-init.sh https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
 && sh /tmp/elan-init.sh -y --no-modify-path --default-toolchain "$(cat lean/lean-toolchain)" \
 && rm /tmp/elan-init.sh \
 && lean --version

RUN pip install --no-cache-dir numpy python-sat pyyaml

COPY . .
RUN pip install --no-cache-dir . \
 && rm -rf build src/*.egg-info \
 && (cd lean && lake build) \
 && ebllm --version \
 && chmod -R a+rX /opt/elan /opt/bllm-engine

ENTRYPOINT ["ebllm"]
CMD ["--help"]
