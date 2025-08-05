import base64
import logging
import ssl
import subprocess
import sys

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import profile
from hcs_core.util import pki_util

import hcs_cli.cmds.dev.util.mqtt_helper as mqtt_helper
import hcs_cli.service.vmhub as vmhub
from hcs_cli.support.exec_util import exec

log = logging.getLogger("mqtt")


@click.group()
def mqtt():
    """MQTT commands for testing and development."""
    pass


@mqtt.command()
@click.option("--legacy", is_flag=True, default=False, help="Use legacy certificate chain for testing.")
@cli.org_id
def test(org: str, legacy: bool, **kwargs):

    org_id = cli.get_org_id(org)
    print(f"Testing MQTT connection for organization: {org_id}")

    print("Preparing cert via PKI...")
    cert_config = mqtt_helper.prepare_cert(org_id)

    _verify_cert_chain(cert_config["client_cert_chain_file"])
    _verify_cert_chain(cert_config["client_cert_chain_legacy_file"])

    profile_data = profile.current()
    for region_config in profile_data.hcs.regions:
        print(f"---- Testing MQTT (cert from PKI) in region: {region_config.name} -----")
        host = region_config.mqtt
        if not host:
            print(f"{region_config.name}: no MQTT host configured")
            continue
        print(f"{region_config.name}: {host}")

        print("---- Testing SSL connection (via openssl) -----")
        cert_name = "client_cert_chain_legacy_file" if legacy else "client_cert_chain_file"
        cmd = f"openssl s_client -showcerts -connect {host}:443 -CAfile {cert_config['root_ca_file']} -cert {cert_config[cert_name]} -key {cert_config['key_file']}"
        cp = exec(cmd, raise_on_error=False)

        print("---- Testing pub/sub (via mqtt client) -----")
        mqtt_helper.test_mqtt(host, cert_config, use_legacy_cert=legacy)

    test_vmhub_otp(org_id)


def test_vmhub_otp(org_id: str):
    profile_data = profile.current()
    resource_name = "agent1"
    for region_config in profile_data.hcs.regions:
        print(f"---- Testing MQTT (cert from VMHub) in region: {region_config.name} -----")
        vmhub.otp.use_region(region_config.name)
        otp = vmhub.otp.request(org_id, resource_name)
        csr_pem, private_key_pem = pki_util.generate_CSR(resource_name)
        ret = vmhub.otp.redeem(resource_name, otp, csr_pem, ca_lable="omnissa")
        key_file = f"vmhub_{resource_name}.key"
        cert_file = f"vmhub_{resource_name}.crt"
        ca_file = f"vmhub_{resource_name}.ca"
        with open(key_file, "w") as f:
            f.write(private_key_pem)
        with open(cert_file, "w") as f:
            pem = base64.b64decode(ret.clientCrt).decode("utf-8")
            f.write(pem)
        with open(ca_file, "w") as f:
            pem = base64.b64decode(ret.caCrt).decode("utf-8")
            f.write(pem)

        print("---- Testing SSL connection (via openssl) -----")
        cmd = f"openssl s_client -showcerts -connect {ret.mqttServerHost}:{ret.mqttServerPort} -CAfile {ca_file} -cert {cert_file} -key {key_file}"
        cp = exec(cmd, raise_on_error=False)

        print("---- Testing pub/sub (via mqtt client) -----")
        mqtt_helper.test_mqtt_pubsub(
            host=ret.mqttServerHost, ca_certs=ca_file, cert_file=cert_file, key_file=key_file, resource_id=resource_name
        )


def _verify_cert_chain(cert_chain_file: str):
    print(f"---- Verifying certificate chain: {cert_chain_file} -----")

    # read the cert chain file
    with open(cert_chain_file, "r") as f:
        client_cert_chain = f.read()

    # the cert chain is in PEM format, with leaf at the top, and the reset below.
    # split the chain into two parts: the leaf and the rest
    separator = "-----END CERTIFICATE-----"
    certs = client_cert_chain.split(separator)
    # remove the last empty part if it exists
    if certs[-1].strip() == "":
        certs.pop()
    # add the separator back to each cert
    for i in range(len(certs)):
        certs[i] = certs[i] + separator
    leaf_cert = certs[0]
    rest_certs = certs[1:]
    # write the leaf cert to a temporary file
    with open("leaf_cert.pem", "w") as f:
        f.write(leaf_cert)
    with open("chain.pem", "w") as f:
        f.write("".join(rest_certs))
    indent = "  * "
    for cert in reversed(certs):
        with open("temp.pem", "w") as f:
            f.write(cert)
        # print the CN name of the cert
        cert_info = subprocess.run(
            "openssl x509 -noout -subject -serial -hash -in temp.pem".split(" "),
            capture_output=True,
            text=True,
        )
        # Split output into lines and print each
        stdout = cert_info.stdout.strip()
        subject = ""
        serial = ""
        hash = ""
        for line in stdout.splitlines():
            if line.startswith("subject="):
                subject = line[len("subject=") :]
            elif line.startswith("serial="):
                serial = line[len("serial=") :]
            elif line.strip() and not line.startswith("subject=") and not line.startswith("serial="):
                hash = line.strip()
            else:
                raise ValueError(f"Unexpected line format: {line}")
        print(indent, subject, f"(serial={serial}, hash={hash})")
        indent = "  " + indent

    cmd = "openssl verify -verbose -CAfile chain.pem leaf_cert.pem"
    cp = exec(cmd, raise_on_error=False)
    if cp.returncode != 0:
        print("❌ Certificate verification failed", file=sys.stderr)
    else:
        print("✅ Certificate verification succeeded")
