"""Test healthchecks."""

from collections.abc import Callable

from packagebusters.endpoints.healthchecks import HealthCheckEndpoint


async def test_health(test_client: Callable) -> None:
    endpoint: HealthCheckEndpoint = HealthCheckEndpoint()

    with test_client([endpoint.router]) as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() is None


async def test_readiness(test_client: Callable) -> None:
    endpoint: HealthCheckEndpoint = HealthCheckEndpoint()

    with test_client([endpoint.router]) as client:
        resp = await client.get("/readiness")
    assert resp.status_code == 200
    assert resp.json() is None
