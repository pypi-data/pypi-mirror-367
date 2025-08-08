#! /usr/bin/env python3

import argparse
import json
import os
import re
import subprocess
from importlib.metadata import PackageNotFoundError, version

import yaml

from es_cloud_secret_manager.aws_secret_manager import AwsSecretManager
from es_cloud_secret_manager.gcp_secret_manager import GcpSecretManager


def get_version():
    """Get the version of the package.

    First tries to get it using importlib.metadata (for installed packages),
    then falls back to reading from pyproject.toml (for development).
    """
    try:
        # Try to get version from installed package metadata
        return version("es-cloud-secret-manager")
    except PackageNotFoundError:
        # Fall back to reading from pyproject.toml during development
        try:
            import toml
            pyproject_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(__file__)),
                "pyproject.toml")
            data = toml.load(pyproject_path)
            return data.get("project", {}).get("version", "unknown")
        except (FileNotFoundError, KeyError):
            return "unknown"


def prettify_yaml_file(file_path):
    subprocess.run(
        f"type sponge && type yq && yq -P <{file_path} | sponge {file_path}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def get_secret_manager(args):
    if args.provider == "aws":
        return AwsSecretManager(args.aws_region)
    elif args.provider == "gcp":
        return GcpSecretManager(args.gcp_project)
    else:
        raise ValueError(f"Provider {args.provider} not supported")


def build_secret_id(args):
    return f"{args.secret}"


def build_secret_path(args):
    secret_path = args.secret_path
    secret_path = f"{secret_path.replace(
        '{provider}', args.provider)}"
    secret_path = f"{secret_path.replace(
        '{aws-region}', args.aws_region if args.provider == 'aws' else '')}"
    secret_path = f"{secret_path.replace(
        '{gcp-project}', args.gcp_project if args.provider == 'gcp' else '')}"
    secret_path = f"{secret_path.replace(
        '{project}', args.project if args.project is not None else '')}"
    return os.path.realpath(secret_path)


def build_fake_store_path(args):
    return f"{args.secret_path.replace('{provider}', args.provider)}/fake-store"


def build_fake_store_filename(args):
    if args.project is None:
        return "fake-store.yaml"
    return f"{args.project}.yaml"


def init_secrets(args):
    secret_path = build_secret_path(args)
    os.makedirs(build_secret_path(args), exist_ok=True)
    for secret_id in args.secret:
        secret_content = "{}"
        secret_extension = "json"
        if args.format == "yaml":
            secret_content = ""
            secret_extension = "yaml"
        secret_file = os.path.realpath(
            f"{secret_path}/{secret_id}.{secret_extension}")
        if os.path.exists(secret_file):
            print(f"Secret {secret_id} already exists into {secret_file}")
            continue
        with open(secret_file, "w", encoding="utf8") as file:
            file.write(secret_content)
        print(f"Initializing secret {secret_id} into {secret_file}")


def import_secrets(args):
    secret_manager = get_secret_manager(args)
    secret_path = build_secret_path(args)
    os.makedirs(build_secret_path(args), exist_ok=True)
    for secret_id in args.secret:
        if secret_manager.secret_exists(secret_id):
            secret_content = secret_manager.access_secret(secret_id)
            secret_extension = "yaml" if args.format == "yaml" else "json"
            secret_file = os.path.realpath(
                f"{secret_path}/{secret_id}.{secret_extension}")
            if secret_extension == "yaml":
                secret_content = yaml.dump(
                    json.loads(secret_content),
                    indent=2,
                    default_flow_style=False,
                    default_style="|",
                )
            with open(secret_file, "w", encoding="utf8") as file:
                file.write(secret_content)
            if secret_extension == "yaml":
                prettify_yaml_file(secret_file)

            print(f"Importing secret {secret_id} into {secret_file}")
        else:
            print(f"Secret {secret_id} not found in {args.project}")


def create_secrets(args):
    secret_manager = get_secret_manager(args)
    for secret_id in args.secret:
        if secret_manager.secret_exists(secret_id):
            raise ValueError(f"Secret already exists: '{secret_id}'")
        secret_manager.create_secret(secret_id, "{}")


def export_secrets(args):
    secret_manager = get_secret_manager(args)
    secret_path = build_secret_path(args)
    if not os.path.exists(secret_path):
        raise FileNotFoundError(f"Folder {secret_path} does not exist")
    for secret_id in args.secret:
        secret_extension = "yaml" if args.format == "yaml" else "json"
        secret_file = os.path.realpath(
            f"{secret_path}/{secret_id}.{secret_extension}")
        if not os.path.exists(secret_file):
            raise FileNotFoundError(f"File {secret_file} does not exist")
        secret_content = None
        with open(secret_file, "r", encoding="utf8") as file:
            if secret_extension == "yaml":
                yaml_object = yaml.safe_load(file)
                secret_content = json.dumps(yaml_object)
            else:
                secret_content = file.read()
        if not secret_content:
            raise ValueError(f"Unable to retrieve content of {secret_file}")
        print(f"Exporting secret {secret_id} from {secret_file}")
        secret_manager.update_secret_from_content(secret_id, secret_content)


def fake_store(args):
    secret_path = build_secret_path(args)
    fake_store_path = build_fake_store_path(args)
    fake_store_filename = f"{fake_store_path}/{
        build_fake_store_filename(args)}"
    if not os.path.exists(build_secret_path(args)):
        raise FileNotFoundError(f"Folder {secret_path} does not exist")
    os.makedirs(f"{fake_store_path}", exist_ok=True)
    secrets = []
    for secret in args.secret:
        secret_extension = "yaml" if args.format == "yaml" else "json"
        secret_file = os.path.realpath(
            f"{secret_path}/{secret}.{secret_extension}")
        if not os.path.exists(secret_file):
            raise FileNotFoundError(f"File {secret_file} does not exist")
        secret_content = None
        with open(secret_file, "r", encoding="utf8") as file:
            if secret_extension == "yaml":
                yaml_object = yaml.safe_load(file)
                secret_content = json.dumps(yaml_object, indent=2)
            else:
                secret_content = file.read()
        if not secret_content:
            raise ValueError(f"Unable to retrieve content of {secret_file}")
        secrets.append({"key": secret if args.store_key_regexp is None else re.sub(
            args.store_key_regexp, args.store_key_replace, secret), "value": secret_content})
    with open(fake_store_filename, "w", encoding="utf8") as file:
        file.write(
            yaml.dump(
                {
                    "apiVersion": "external-secrets.io/v1beta1",
                    "kind": "ClusterSecretStore",
                    "metadata": {"name": "fake-store"},
                    "spec": {"provider": {"fake": {"data": secrets}}},
                },
                indent=2,
                default_flow_style=False,
                default_style="|",
            )
        )
    prettify_yaml_file(fake_store_filename)
    print(f"Fake store created at {fake_store_filename}")


def list_secrets(args):
    secret_manager = get_secret_manager(args)
    for secret_id in args.secret:
        secret_manager.list_versions(secret_id)


def details_secrets(args):
    secret_manager = get_secret_manager(args)
    for secret_id in args.secret:
        secret_manager.list_versions(secret_id)


def delete_secret_version(args):
    secret_manager = get_secret_manager(args)
    secret_manager.delete_version(build_secret_id(args), args.version)


def diff_secrets(args):
    secret_path = build_secret_path(args)
    secret_manager = get_secret_manager(args)
    version = args.version
    compare_version = args.compare_version
    for secret_id in args.secret:
        print(
            f"Comparing secret {secret_id} version {
                version} with version {compare_version}"
        )
        if not secret_manager.secret_exists(secret_id):
            raise ValueError(f"Secret '{secret_id}' does not exist")
        secret_content = secret_manager.access_secret(secret_id, version)
        secret_extension = "yaml" if args.format == "yaml" else "json"
        compare_secret_file = os.path.realpath(
            f"{secret_path}/{secret_id}.{version}.{secret_extension}")
        if secret_extension == "yaml":
            secret_content = yaml.dump(
                json.loads(secret_content),
                indent=2,
                default_flow_style=False,
                default_style="|",
            )
        with open(compare_secret_file, "w", encoding="utf8") as file:
            file.write(secret_content)
        if secret_extension == "yaml":
            prettify_yaml_file(compare_secret_file)

        secret_file = os.path.realpath(
            f"{secret_path}/{secret_id}.{secret_extension}")
        if compare_version != "local":
            secret_file = f"{
                secret_path}/{secret_id}.{compare_version}.{secret_extension}"
            secret_content = secret_manager.access_secret(
                secret_id, compare_version)
            if secret_extension == "yaml":
                secret_content = yaml.dump(
                    json.loads(secret_content),
                    indent=2,
                    default_flow_style=False,
                    default_style="|",
                )
            with open(secret_file, "w", encoding="utf8") as file:
                file.write(secret_content)
            if secret_extension == "yaml":
                prettify_yaml_file(secret_file)

        print(f"Diff between {compare_secret_file} and {secret_file}")
        result = subprocess.run(
            f"diff --color=always -U 4 {compare_secret_file} {secret_file}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(result.stdout)


def add_common_args(parser):
    parser.add_argument(
        "--secret",
        type=str,
        nargs="+",
        required=True,
        help="Name of the secret(s) to handle",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="yaml",
        help="Use given format to store secret amongs json, yaml (default=yaml)",
    )


def main() -> None:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # create the top-level parser
    parser = argparse.ArgumentParser(
        # prog="es-cloud-secret-manager",
        description="""Tool to create/initialize/import/export/list/diff/delete secrets from/to AWS/GCP Secret Manager and generate fake store manifest for testing""",
        epilog="""
Examples:
  - %(prog)s aws --help
  - %(prog)s gcp --help
    """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug mode"
    )
    parser.add_argument(
        "--version", action="version", version=f"{get_version()}"
    )
    parser.add_argument(
        "--secret-path",
        type=str,
        default=f"{
            os.environ['HOME']}/.cloud-secrets/{'{provider}'}/{'{aws-region}{gcp-project}'}",
        help=f"path where to import/export secrets with few placeholders ({'{provider}, {aws-region}, {gcp-project}, {project}'}) (default={
            os.environ['HOME']}/.cloud-secrets/{'{provider}'}/{'{aws-region|gcp-project}'}",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project of the secret, would only be used to determine the secret path",
    )

    provider_subparsers = parser.add_subparsers(
        title="provider", help="provider help")

    # AWS provider
    aws_provider_parser = provider_subparsers.add_parser(
        "aws",
        description="Handling secret from AWS",
        help="Amazon AWS Secret Manager helper",
        epilog="""
Examples:
  - %(prog)s --region eu-west-1 create --secret secret-project-application-test
  - %(prog)s --region eu-west-1 initialize --secret secret-project-application-test
  - %(prog)s --region eu-west-1 import --secret secret-project-application-test
  - %(prog)s --region eu-west-1 export --secret secret-project-application-test
  - %(prog)s --region eu-west-1 fake --secret secret-project-application-test
  - %(prog)s --region eu-west-1 list --secret secret-project-application-test
  - %(prog)s --region eu-west-1 details --secret secret-project-application-test
  - %(prog)s --region eu-west-1 delete --secret secret-project-application-test --version 84e8c4e5-27c7-4nov-z9f5-50c398fe4911
  - %(prog)s --region eu-west-1 diff --secret secret-project-application-test
    """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    aws_provider_parser.set_defaults(provider="aws")
    aws_provider_parser.add_argument(
        "--aws-region",
        type=str,
        required=True,
        default=None,
        help="AWS region where the secrets are stored",
    )

    # GCP provider
    gcp_provider_parser = provider_subparsers.add_parser(
        "gcp",
        description="Handling secret from GCP",
        help="Google GCP Secret Manager helper",
        epilog="""
Examples:
  - %(prog)s --gcp-project project create --secret secret-project-application-test
  - %(prog)s --gcp-project project initialize --secret secret-project-application-test
  - %(prog)s --gcp-project project import --secret secret-project-application-test
  - %(prog)s --gcp-project project export --secret secret-project-application-test
  - %(prog)s --gcp-project project fake --secret secret-project-application-test
  - %(prog)s --gcp-project project list --secret secret-project-application-test
  - %(prog)s --gcp-project project details --secret secret-project-application-test
  - %(prog)s --gcp-project project delete --secret secret-project-application-test --version 1
  - %(prog)s --gcp-project project diff --secret secret-project-application-test
    """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    gcp_provider_parser.set_defaults(provider="gcp")
    gcp_provider_parser.add_argument(
        "--gcp-project",
        type=str,
        required=True,
        default=None,
        help="GCP project where the secrets are stored",
    )

    for provider in [aws_provider_parser, gcp_provider_parser]:
        subparsers = provider.add_subparsers(
            title="sub-commands", help="sub-command help"
        )

        # Create
        create_parser = subparsers.add_parser(
            "create",
            help="Create new secrets",
            description="Create new secrets",
            epilog="""
Examples:
  - %(prog)s [option,...] <provider> [provider_option,...] create --secret <secret_name [secret_name,...]>
    """,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        create_parser.set_defaults(func=create_secrets)
        add_common_args(create_parser)

        # Initialize
        initialize_parser = subparsers.add_parser(
            "initialize",
            help="Simply create empty secret file locally (to be done when there is no secret version yet)",
            description="Simply create empty secret file locally (to be done when there is no secret version yet)",
            epilog="""
Examples:
  - %(prog)s [option,...] <provider> [provider_option,...] initialize --secret <secret_name [secret_name,...]>
    """,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        initialize_parser.set_defaults(func=init_secrets)
        add_common_args(initialize_parser)

        # Import
        import_parser = subparsers.add_parser(
            "import",
            help="Retrieve secret from the vault and store it locally",
            description="Retrieve secret from the vault and store it locally",
            epilog="""
Examples:
  - %(prog)s [option,...] <provider> [provider_option,...] import --secret <secret_name [secret_name,...]>
    """,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        import_parser.set_defaults(func=import_secrets)
        add_common_args(import_parser)

        # Export
        export_parser = subparsers.add_parser(
            "export",
            help="Use the local file and export it to the vault",
            description="Use the local file and export it to the vault",
            epilog="""
Examples:
  - %(prog)s [option,...] <provider> [provider_option,...] export --secret <secret_name [secret_name,...]>
    """,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        export_parser.set_defaults(func=export_secrets)
        add_common_args(export_parser)

        # Fake store
        fake_parser = subparsers.add_parser(
            "fake",
            help="Use the local file and create a fake store with it",
            description="Use the local file and create a fake store with it",
            epilog="""
Examples:
  - %(prog)s [option,...] <provider> [provider_option,...] fake --secret <secret_name [secret_name,...]>
    """,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        fake_parser.set_defaults(func=fake_store)
        add_common_args(fake_parser)
        fake_parser.add_argument(
            "--store-key-regexp",
            type=str,
            default=None,
            help="Regexp to extract the key of the secret to use in the fake store, from the secret name, eg. 'secret-project-(.*)-test'",
        )
        fake_parser.add_argument(
            "--store-key-replace",
            type=str,
            default='\\1',
            help="Replacement to use from the regexp, default('\\1')",
        )

        # List
        list_parser = subparsers.add_parser(
            "list",
            help="List secret versions from the vault",
            description="List secret versions from the vault",
            epilog="""
Examples:
  - %(prog)s [option,...] <provider> [provider_option,...] list --secret <secret_name [secret_name,...]>
    """,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        list_parser.set_defaults(func=list_secrets)
        add_common_args(list_parser)

        # Details
        detail_parser = subparsers.add_parser(
            "details",
            help="List secret with more details",
            description="List secret with more details",
            epilog="""
Examples:
  - %(prog)s [option,...] <provider> [provider_option,...] details --secret <secret_name [secret_name,...]>
    """,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        detail_parser.set_defaults(func=details_secrets)
        add_common_args(detail_parser)

        # Delete
        delete_parser = subparsers.add_parser(
            "delete",
            help="Delete secret version in the vault",
            description="Delete secret version in the vault",
            epilog="""
Examples:
  - %(prog)s [option,...] <provider> [provider_option,...] delete --secret <secret_name> --version <version id>
    """,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        delete_parser.set_defaults(func=delete_secret_version)
        delete_parser.add_argument(
            "--secret",
            type=str,
            required=True,
            help="Secret to delete version from",
        )
        delete_parser.add_argument(
            "--version",
            type=str,
            required=True,
            help="Version to delete",
        )

        # Diff
        diff_parser = subparsers.add_parser(
            "diff",
            description="Show diff secret between versions",
            epilog="""
Examples:
  - %(prog)s [option,...] <provider> [provider_option,...] diff --secret <secret_name [secret_name,...]>
    """,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        diff_parser.set_defaults(func=diff_secrets)
        add_common_args(diff_parser)
        diff_parser.add_argument(
            "--version",
            type=str,
            default="latest",
            help="Version to select for diff (default=latest)",
        )
        diff_parser.add_argument(
            "--compare-version",
            type=str,
            default="local",
            help="Version to compare to (default=local)",
        )

    args = parser.parse_args()
    # print(args)
    if "func" in args:
        if args.debug:
            args.func(args)
        else:
            try:
                args.func(args)
            except Exception as e:
                print(f"Error: {e}")
                exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
