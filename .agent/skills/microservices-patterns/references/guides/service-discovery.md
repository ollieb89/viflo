# Service Discovery

Extracted from [SKILL.md](../SKILL.md)

## Overview

Service discovery enables microservices to find and communicate with each other without hardcoded locations. In dynamic environments where services scale up/down and instances come and go, service discovery provides a registry where services can register themselves and clients can look up service locations.

## Patterns

### Client-Side Discovery

The client is responsible for determining the network locations of available service instances and load balancing requests across them.

```python
# Client queries service registry directly
import consul

class ClientSideDiscovery:
    """Client-side service discovery with Consul."""

    def __init__(self, consul_host: str = "localhost"):
        self.consul = consul.Consul(host=consul_host)

    def get_service(self, service_name: str) -> str:
        """Get healthy service instance URL."""
        index, services = self.consul.health.service(service_name)

        healthy_instances = [
            s for s in services
            if s['Checks'][0]['Status'] == 'passing'
        ]

        if not healthy_instances:
            raise ServiceNotFoundError(f"No healthy instances of {service_name}")

        # Simple round-robin selection
        instance = healthy_instances[0]['Service']
        return f"http://{instance['Address']}:{instance['Port']}"
```

### Server-Side Discovery

Clients make requests via a load balancer/router that queries the service registry and forwards requests to available instances.

```python
# Server-side via API Gateway
class ServerSideDiscovery:
    """Server-side discovery through load balancer."""

    def __init__(self, load_balancer_url: str):
        self.lb_url = load_balancer_url

    async def call_service(self, service_name: str, path: str):
        """Call service through load balancer."""
        # Load balancer handles discovery
        url = f"{self.lb_url}/{service_name}{path}"
        return await http_client.get(url)
```

## Implementations

### Consul

HashiCorp Consul provides service discovery, health checking, and key-value storage.

```python
# Service registration with Consul
import consul
import socket

class ConsulServiceRegistry:
    """Register and discover services via Consul."""

    def __init__(self, host: str = "localhost", port: int = 8500):
        self.consul = consul.Consul(host=host, port=port)

    def register(
        self,
        service_name: str,
        service_port: int,
        health_check_path: str = "/health"
    ):
        """Register service instance with Consul."""
        hostname = socket.gethostname()
        service_id = f"{service_name}-{hostname}-{service_port}"

        self.consul.agent.service.register(
            name=service_name,
            service_id=service_id,
            address=hostname,
            port=service_port,
            check=consul.Check.http(
                url=f"http://{hostname}:{service_port}{health_check_path}",
                interval="10s",
                timeout="5s"
            ),
            tags=["microservice", "v1"]
        )

    def deregister(self, service_id: str):
        """Remove service from registry."""
        self.consul.agent.service.deregister(service_id)

    def discover(self, service_name: str) -> list:
        """Get all healthy instances of a service."""
        index, nodes = self.consul.health.service(service_name)
        return [
            {
                "address": node["Service"]["Address"],
                "port": node["Service"]["Port"],
                "tags": node["Service"]["Tags"]
            }
            for node in nodes
            if node["Checks"][0]["Status"] == "passing"
        ]
```

### etcd

CoreOS etcd is a distributed key-value store that can be used for service discovery.

```python
# Service registration with etcd
import etcd3
import json
import asyncio

class EtcdServiceRegistry:
    """Service discovery using etcd."""

    def __init__(self, endpoints: list = None):
        self.endpoints = endpoints or ["localhost:2379"]
        self.etcd = etcd3.client(host=self.endpoints[0].split(":")[0])

    async def register(
        self,
        service_name: str,
        instance_id: str,
        host: str,
        port: int,
        ttl: int = 30
    ):
        """Register service with lease (TTL)."""
        lease = self.etcd.lease(ttl)

        service_info = {
            "host": host,
            "port": port,
            "registered_at": datetime.now().isoformat()
        }

        key = f"/services/{service_name}/{instance_id}"
        self.etcd.put(key, json.dumps(service_info), lease=lease)

        # Keep lease alive
        while True:
            await asyncio.sleep(ttl / 2)
            lease.refresh()

    def discover(self, service_name: str) -> list:
        """Get all instances of a service."""
        prefix = f"/services/{service_name}/"
        instances = []

        for value, metadata in self.etcd.get_prefix(prefix):
            instance_data = json.loads(value.decode())
            instance_data["id"] = metadata.key.decode().split("/")[-1]
            instances.append(instance_data)

        return instances

    def watch(self, service_name: str, callback):
        """Watch for changes in service instances."""
        prefix = f"/services/{service_name}/"
        events = self.etcd.watch_prefix(prefix)

        for event in events:
            callback(event)
```

### Kubernetes

Kubernetes has built-in service discovery via DNS and environment variables.

```python
# Kubernetes-native service discovery
import os
import kubernetes
from kubernetes import client, config

class KubernetesServiceDiscovery:
    """Service discovery in Kubernetes cluster."""

    def __init__(self, namespace: str = "default"):
        config.load_incluster_config()  # or load_kube_config()
        self.v1 = client.CoreV1Api()
        self.namespace = namespace

    def get_service_url_env(self, service_name: str) -> str:
        """Get service URL from Kubernetes environment variables."""
        # Kubernetes sets env vars like: ORDER_SERVICE_SERVICE_HOST
        env_name = f"{service_name.upper().replace('-', '_')}_SERVICE_HOST"
        host = os.environ.get(env_name)

        port_env = f"{service_name.upper().replace('-', '_')}_SERVICE_PORT"
        port = os.environ.get(port_env, "80")

        if host:
            return f"http://{host}:{port}"

        # Fallback to DNS name
        return f"http://{service_name}.{self.namespace}.svc.cluster.local"

    def get_service_endpoints(self, service_name: str) -> list:
        """Get pod endpoints for a service."""
        endpoints = self.v1.read_namespaced_endpoints(
            name=service_name,
            namespace=self.namespace
        )

        addresses = []
        if endpoints.subsets:
            for subset in endpoints.subsets:
                for address in subset.addresses or []:
                    port = subset.ports[0].port if subset.ports else 80
                    addresses.append(f"{address.ip}:{port}")

        return addresses

    def list_services(self, selector: dict = None) -> list:
        """List services matching selector."""
        label_selector = ",".join([f"{k}={v}" for k, v in selector.items()]) if selector else None

        services = self.v1.list_namespaced_service(
            namespace=self.namespace,
            label_selector=label_selector
        )

        return [
            {
                "name": svc.metadata.name,
                "cluster_ip": svc.spec.cluster_ip,
                "ports": [(p.port, p.target_port) for p in svc.spec.ports or []]
            }
            for svc in services.items
        ]
```

## Comparison

| Feature | Consul | etcd | Kubernetes |
|---------|--------|------|------------|
| **Type** | Full-featured service mesh | Key-value store | Container orchestrator |
| **Health Checks** | Built-in HTTP/TCP/Script | Requires custom implementation | Built-in readiness/liveness |
| **Key-Value Store** | Yes | Yes (primary) | ConfigMaps/Secrets |
| **Multi-Datacenter** | Native support | Via clustering | Via federation |
| **Learning Curve** | Medium | Low | Low (if using K8s) |
| **Best For** | Complex multi-service architectures | Simple, fast discovery | K8s-native applications |

## Best Practices

1. **Always use health checks** - Unhealthy instances should be automatically removed
2. **Implement client-side caching** - Cache service locations to reduce registry load
3. **Handle failures gracefully** - Retry with backoff when registry is unavailable
4. **Use service mesh for advanced features** - Consider Istio/Linkerd for mTLS, traffic splitting
5. **Version your services** - Use tags/labels to manage service versions
