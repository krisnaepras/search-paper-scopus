"""Utility to generate a self-signed TLS certificate via OpenSSL.

Usage examples:

- Basic certificate for localhost:
    python scripts/generate_ssl.py --common-name localhost --san localhost 127.0.0.1

- Custom organization and output directory:
    python scripts/generate_ssl.py --common-name api.pasco.id \
        --organization "PaSco Labs" --output-dir certs --name pasco

The script requires the OpenSSL executable to be available on PATH.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a self-signed SSL/TLS certificate using OpenSSL",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--common-name", required=True, help="Primary domain (CN) for the certificate")
    parser.add_argument(
        "--san",
        nargs="*",
        default=[],
        metavar="SAN",
        help=(
            "Optional Subject Alternative Names. "
            "Use plain values for DNS entries (e.g., example.com) or prefix with DNS:/IP: explicitly."
        ),
    )
    parser.add_argument("--country", default="ID", help="Country code (C)")
    parser.add_argument("--state", default="Jakarta", help="State or province (ST)")
    parser.add_argument("--locality", default="Jakarta", help="Locality or city (L)")
    parser.add_argument("--organization", default="PaSco", help="Organization name (O)")
    parser.add_argument(
        "--organizational-unit",
        default="Engineering",
        help="Organizational unit (OU)",
    )
    parser.add_argument("--email", default="support@pasco.local", help="Contact email (emailAddress)")
    parser.add_argument("--days", type=int, default=365, help="Certificate validity in days")
    parser.add_argument("--key-size", type=int, default=2048, help="RSA key size")
    parser.add_argument(
        "--output-dir",
        default="certs",
        help="Directory to write the certificate and key",
    )
    parser.add_argument("--name", default="server", help="Base filename for the key/certificate")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files without prompting",
    )

    return parser.parse_args()


def locate_openssl() -> Path:
    openssl_path = shutil.which("openssl")
    if not openssl_path:
        print("Error: OpenSSL executable not found on PATH. Install OpenSSL first.", file=sys.stderr)
        sys.exit(1)
    return Path(openssl_path)


def build_config(args: argparse.Namespace, san_entries: list[str]) -> str:
    dn_lines = [
        ("C", args.country),
        ("ST", args.state),
        ("L", args.locality),
        ("O", args.organization),
        ("OU", args.organizational_unit),
        ("CN", args.common_name),
        ("emailAddress", args.email),
    ]

    dn_block = "\n".join(f"{key} = {value}" for key, value in dn_lines if value)

    req_block = textwrap.dedent(
        f"""
        [ req ]
        default_bits = {args.key_size}
        default_md = sha256
        prompt = no
        distinguished_name = dn
        {'req_extensions = req_ext' if san_entries else ''}
        """
    ).strip()

    config_parts = [req_block, "", "[ dn ]", dn_block]

    if san_entries:
        san_line = ", ".join(san_entries)
        req_ext_block = textwrap.dedent(
            f"""
            
            [ req_ext ]
            subjectAltName = {san_line}
            """
        ).rstrip()
        config_parts.append(req_ext_block)

    return "\n".join(part for part in config_parts if part)


def normalize_san_entries(raw_entries: list[str]) -> list[str]:
    normalized = []
    for entry in raw_entries:
        if not entry:
            continue
        if ":" in entry:
            prefix, value = entry.split(":", 1)
            prefix = prefix.strip().upper()
            value = value.strip()
            if prefix not in {"DNS", "IP"}:
                raise ValueError(f"Unsupported SAN type '{prefix}'. Use DNS or IP.")
            normalized.append(f"{prefix}:{value}")
        else:
            normalized.append(f"DNS:{entry.strip()}")
    return normalized


def generate_certificate(args: argparse.Namespace) -> None:
    openssl_bin = locate_openssl()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    key_path = output_dir / f"{args.name}.key"
    cert_path = output_dir / f"{args.name}.crt"

    if not args.force:
        for path in (key_path, cert_path):
            if path.exists():
                print(f"Error: {path} already exists. Use --force to overwrite.", file=sys.stderr)
                sys.exit(1)

    san_entries = normalize_san_entries(args.san)
    config_text = build_config(args, san_entries)

    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as config_file:
        config_file.write(config_text)
        config_path = Path(config_file.name)

    cmd = [
        str(openssl_bin),
        "req",
        "-x509",
        "-nodes",
        "-days",
        str(args.days),
        "-newkey",
        f"rsa:{args.key_size}",
        "-keyout",
        str(key_path),
        "-out",
        str(cert_path),
        "-config",
        str(config_path),
    ]

    if san_entries:
        cmd.extend(["-extensions", "req_ext"])

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print("OpenSSL failed:", exc, file=sys.stderr)
        sys.exit(exc.returncode)
    finally:
        try:
            config_path.unlink()
        except OSError:
            pass

    print(f"Certificate generated: {cert_path}")
    print(f"Private key generated: {key_path}")
    print()
    print("Next steps:")
    print("  - Configure your server to use the generated key and certificate")
    print("  - Distribute the certificate to clients (if needed)")
    print("  - Regenerate before expiration or adjust --days as required")


def main() -> None:
    args = parse_args()
    try:
        generate_certificate(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
