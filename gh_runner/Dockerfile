# Self-hosted GitHub Actions runner for net_gitops.
# Needs reach to the lab Kubernetes cluster (the pyats-lab workflow uses kubectl).
#
#   docker build -t gh-runner gh_runner/
#   docker run -d --env-file gh_runner/.env --network host --name gh-runner gh-runner
# kubectl pulled as a layer (avoids curl to dl.k8s.io, which is TLS-inspected here).
FROM rancher/kubectl:v1.29.3 AS kubectl

FROM ubuntu:22.04

ARG RUNNER_VERSION="2.319.1"
ARG TARGETARCH="x64"

RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates jq git sudo \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m runner

# kubectl - the pyats-lab workflow waits on ArgoCD and reads the Job logs.
COPY --from=kubectl /bin/kubectl /usr/local/bin/kubectl

WORKDIR /home/runner
RUN curl -fsSL -o runner.tar.gz \
        "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${TARGETARCH}-${RUNNER_VERSION}.tar.gz" \
    && tar xzf runner.tar.gz && rm runner.tar.gz \
    && ./bin/installdependencies.sh \
    && chown -R runner:runner /home/runner

COPY start.sh /home/runner/start.sh
RUN chmod +x /home/runner/start.sh

USER runner
ENTRYPOINT ["./start.sh"]
