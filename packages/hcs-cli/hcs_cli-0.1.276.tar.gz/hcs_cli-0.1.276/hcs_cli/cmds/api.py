import json

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.sglib.client_util import hdc_service_client, is_regional_service, regional_service_client


@click.command()
@click.option("--method", "-m", type=click.Choice(["GET", "POST", "PUT", "DELETE", "PATCH"]), default="GET", help="HTTP method to use.")
@click.option("--data", "-d", type=str, help="Data to send with the request.")
@click.option("--file", "-f", type=str, help="Data file to send with the request.")
@click.option("--hdc", type=str, required=False, help="HDC name to use. Only valid when the service is a global service.")
@click.option("--region", type=str, required=False, help="Regional name to use. Only valid when the service is a regional service.")
@click.option(
    "--raise-on-404",
    is_flag=True,
    default=False,
    help="Raise an error on HTTP 404 responses. If not set, returns None on 404. Only valid for GET and DELETE methods.",
)
@click.argument("path", type=str, required=True)
def api(method: str, data: str, file: str, hdc: str, region: str, raise_on_404: bool, path: str, **kwargs):
    """Invoke HCS API by context path."""

    if data and file:
        raise click.UsageError("You cannot specify both --data and --file options. Use one of them.")

    if method in ["GET", "DELETE"] and (data or file):
        raise click.UsageError(f"Method {method} does not support body data. Use --data or --file only with POST, PUT, or PATCH methods.")

    if raise_on_404 and method not in ["GET", "DELETE"]:
        raise click.UsageError("The --raise-on-404 option is only applicable for GET and DELETE methods.")

    if not path.startswith("/"):
        raise click.UsageError("Path must start with a '/'. Please provide a valid context path.")

    # determine whether this is HDC service or region service
    if file:
        with open(file, "rt") as f:
            data = f.read()

    service_path = path.split("/")[1]
    api_path = path[len(service_path) + 1 :]
    if is_regional_service(service_path):
        client = regional_service_client(service_path, region=region)
    else:
        client = hdc_service_client(service_path, hdc=hdc)

    # print('service_path:', service_path)
    # print('api_path:', api_path)
    # print('method:', method)
    # print("hdc:", hdc)
    # print("region:", region)
    if method == "GET":
        response = client.get(api_path, raise_on_404=raise_on_404)
    elif method == "POST":
        response = client.post(api_path, text=data)
    elif method == "PUT":
        response = client.put(api_path, text=data)
    elif method == "DELETE":
        response = client.delete(api_path, raise_on_404=raise_on_404)
    elif method == "PATCH":
        response = client.patch(api_path, text=data)
    else:
        raise click.UsageError(f"Unsupported HTTP method: {method}")
    return response
