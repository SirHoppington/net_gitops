# Self-hosted GitHub Actions runner for net_gitops.
# Needs reach to the lab Kubernetes cluster (the pyats-lab workflow uses kubectl).
#
#   docker build -t gh-runner gh_runner/
#   docker run -d --env-file gh_runner/.env --network host --name gh-runner gh-runner
# Binaries pulled as layers (avoid curl to TLS-inspected hosts like dl.k8s.io).
FROM rancher/kubectl:v1.29.3 AS kubectl
FROM docker:27-cli AS dockercli

FROM ubuntu:22.04

ARG RUNNER_VERSION="2.319.1"
ARG KIND_VERSION="v0.23.0"
# TARGETARCH is auto-provided by buildkit (amd64 / arm64) -> build native for the host.
ARG TARGETARCH

RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates jq git sudo \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m runner \
    && echo "runner ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/runner \
    && chmod 440 /etc/sudoers.d/runner

# kubectl - waits on ArgoCD and reads Job logs.
COPY --from=kubectl /bin/kubectl /usr/local/bin/kubectl
# docker CLI + kind - the build+load pre-step builds the pyATS image and loads
# it into the kind cluster (uses the host docker socket mounted at runtime).
COPY --from=dockercli /usr/local/bin/docker /usr/local/bin/docker
RUN curl -fsSLo /usr/local/bin/kind \
        "https://github.com/kubernetes-sigs/kind/releases/download/${KIND_VERSION}/kind-linux-${TARGETARCH}" \
    && chmod +x /usr/local/bin/kind

WORKDIR /home/runner
# Map docker arch -> GitHub runner arch naming (amd64->x64, arm64->arm64).
RUN case "${TARGETARCH}" in \
        amd64) RUNNER_ARCH=x64 ;; \
        arm64) RUNNER_ARCH=arm64 ;; \
        *) echo "unsupported TARGETARCH=${TARGETARCH}" && exit 1 ;; \
    esac \
    && curl -fsSL -o runner.tar.gz \
        "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz" \
    && tar xzf runner.tar.gz && rm runner.tar.gz \
    && ./bin/installdependencies.sh \
    && chown -R runner:runner /home/runner

COPY start.sh /home/runner/start.sh
RUN chmod +x /home/runner/start.sh

USER runner
ENTRYPOINT ["./start.sh"]
