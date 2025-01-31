#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys

from deeptools.SES_scaleFactor import estimateScaleFactor
from deeptools.parserCommon import numberOfProcessors
try:  # keep python 3.7 support.
    from importlib.metadata import version
except ModuleNotFoundError:
    from importlib_metadata import version

debug = 0


def parseArguments(args=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Given two BAM files, this estimates scaling factors '
        '(bigger to smaller).',
        usage='estimateScaleFactor -b sample1.bam sample2.bam\n'
        'help: estimateScaleFactor -h / estimateScaleFactor --help'
    )

    # define the arguments
    parser.add_argument('--bamfiles', '-b',
                        metavar='list of bam files',
                        help='List of indexed BAM files, space delineated',
                        nargs='+',
                        required=True)

    parser.add_argument('--ignoreForNormalization', '-ignore',
                        help='A comma-separated list of chromosome names, '
                        'limited by quotes, '
                        'containing those '
                        'chromosomes that should be excluded '
                        'during normalization computations. For example, '
                        '--ignoreForNormalization "chrX, chrM" ')

    parser.add_argument('--sampleWindowLength', '-l',
                        help='Length in bases for a window used to '
                        'sample the genome and compute the size or scaling '
                        'factors',
                        default=1000,
                        type=int)

    parser.add_argument('--numberOfSamples', '-n',
                        help='Number of samplings taken from the genome '
                        'to compute the scaling factors',
                        default=100000,
                        type=int)

    parser.add_argument('--normalizationLength', '-nl',
                        help='By default, data is normalized to 1 '
                        'fragment per 100 bases. The expected value is an '
                        'integer. For example, if normalizationLength '
                        'is 1000, then the resulting scaling factor '
                        'will cause the average coverage of the BAM file to '
                        'have on  average 1 fragment per kilobase',
                        type=int,
                        default=10)

    parser.add_argument('--skipZeros',
                        help='If set, then zero counts that happen for *all* '
                        'BAM files given are ignored. This will result in a '
                        'reduced number of read counts than that specified '
                        'in --numberOfSamples',
                        action='store_true',
                        required=False)

    parser.add_argument('--numberOfProcessors', '-p',
                        help='Number of processors to use. The default is '
                        'to use half the maximum number of processors.',
                        metavar="INT",
                        type=numberOfProcessors,
                        default="max/2",
                        required=False)

    parser.add_argument('--verbose', '-v',
                        help='Set to see processing messages.',
                        action='store_true')

    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {}'.format(version('deeptools')))

    args = parser.parse_args(args)
    if args.ignoreForNormalization:
        args.ignoreForNormalization = [
            x.strip() for x in args.ignoreForNormalization.split(',')
        ]
    else:
        args.ignoreForNormalization = []
    return args


def main(args=None):
    """
    The algorithm samples the genome a number of times as specified
    by the --numberOfSamples parameter to estimate scaling factors of
    between to samples

    """
    args = parseArguments().parse_args(args)
    if len(args.bamfiles) > 2:
        print("SES method to estimate scale factors only works for two samples")
        exit(0)

    sys.stderr.write("{:,} number of samples will be computed.\n".format(args.numberOfSamples))
    sizeFactorsDict = estimateScaleFactor(args.bamfiles, args.sampleWindowLength,
                                          args.numberOfSamples,
                                          args.normalizationLength,
                                          numberOfProcessors=args.numberOfProcessors,
                                          chrsToSkip=args.ignoreForNormalization,
                                          verbose=args.verbose)

    for k, v in sizeFactorsDict.items():
        print("{}: {}".format(k, v))
