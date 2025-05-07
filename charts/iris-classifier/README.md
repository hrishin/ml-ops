# Iris Classifier API Helm Chart

This Helm chart deploys the **Iris Classifier API** to a Kubernetes cluster. It provides configuration for replicas, container image, resources, logging, ingress routing, and Prometheus metrics.

## Prerequisites

- Helm 3.x
- Kubernetes 1.19+
- Optional: Prometheus for metrics scraping

## Installation

```bash
helm repo add iris-api https://hrishin.github.io/ml-ops
helm install iris-api iris-api/iris-classifier-api
```

## Configuration
The following table lists the configurable parameters of the chart and their default values.

| Parameter                   | Description                                           | Default                                  |
| --------------------------- | ----------------------------------------------------- | ---------------------------------------- |
| `replicaCount`              | Number of replicas for the deployment                 | `2`                                      |
| `image.repository`          | Container image repository                            | `docker.io/hriships/iris-classifier-api` |
| `image.tag`                 | Container image tag                                   | `v1.3.0`                                 |
| `image.pullPolicy`          | Image pull policy                                     | `Always`                                 |
| `resources.limits.cpu`      | CPU limit                                             | `500m`                                   |
| `resources.limits.memory`   | Memory limit                                          | `512Mi`                                  |
| `resources.requests.cpu`    | CPU request                                           | `200m`                                   |
| `resources.requests.memory` | Memory request                                        | `256Mi`                                  |
| `logLevel`                  | Log verbosity level (e.g., `INFO`, `DEBUG`)           | `INFO`                                   |
| `args`                      | Arguments passed to the application (e.g., port)      | `[8080]`                                 |
| `route.port`                | Service port exposed by the application               | `8080`                                   |
| `route.host`                | Ingress host                                          | `iris.kube.two.inc`                      |
| `route.paths`               | List of ingress paths                                 | `["/api/v1"]`                            |
| `metrics.enabled`           | Enable Prometheus metrics endpoint                    | `true`                                   |
| `metrics.path`              | Path for Prometheus to scrape metrics                 | `/metrics`                               |
| `metrics.port`              | Port exposing metrics                                 | `8000`                                   |
| `storage.size`              | (Optional) Persistent volume size for the application | *commented out by default*               |

To override defaults, pass your custom values file:

```bash
helm install iris-api -f my-values.yaml iris-api/iris-classifier-api
```


