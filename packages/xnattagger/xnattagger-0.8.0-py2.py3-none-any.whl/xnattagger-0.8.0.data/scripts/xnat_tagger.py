#!python

import os
import re
import sys
import json
import yaml
import yaxil
import string
import logging
import requests
import collections
import argparse as ap
from io import StringIO
from yaml.representer import Representer
from yaxil.exceptions import NoExperimentsError
from xnattagger import Tagger
import xnattagger.config as config 

logger = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=logging.INFO)

yaml.add_representer(collections.defaultdict, Representer.represent_dict)


def main():
    # Parse command line arguments
    parser = ap.ArgumentParser()
    parser.add_argument('--xnat-alias', required=True,
        help='XNAT alias')
    parser.add_argument('--project',
        help='XNAT project')
    parser.add_argument('-c', '--cache', action='store_true',
        help='Speed up development by caching yaxil.scans output')
    parser.add_argument('-o', '--output-file',
        help='Output summary of updates')
    parser.add_argument('--dry-run', action='store_true',
        help='Do not execute updates')
    parser.add_argument('--confirm', action='store_true',
        help='Prompt user to confirm every update')
    parser.add_argument('--config', required=True,
        help='Filters configuration file') 
    parser.add_argument('--target-modality', nargs='+', required=True, type=str.lower)
    parser.add_argument('--label', required=True,
        help='Label of XNAT MR Session')
    args = parser.parse_args()

    with open(args.config) as fo:
        configs = yaml.load(fo, Loader=yaml.SafeLoader)['xnat-tagger']

    tagger = Tagger(
        args.xnat_alias,
        configs,
        args.target_modality,
        args.label,
        cache=args.cache
    )
    tagger.generate_updates()

    if args.output_file:
        with open(args.output_file, 'w') as fo:
            js = json.dumps(tagger.updates, indent=2)
            fo.write(js)
    if not args.dry_run:
        tagger.apply_updates()

if __name__ == '__main__':
    main()


