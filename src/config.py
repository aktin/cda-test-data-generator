import argparse
from dataclasses import dataclass


@dataclass
class Config:
    n: int
    cleanup: bool
    xlsx: str
    xslt: str
    output_dir: str

    @classmethod
    def from_args(cls):
        parser = argparse.ArgumentParser(prog='cda-test-data-generator', description='Process Excel to CDA.')
        parser.add_argument('--n', type=int, required=True, help='Number of patients to generate.')
        parser.add_argument('--cleanup', action='store_true', help='Remove intermediate CSV file after processing.')
        parser.add_argument('--xlsx', type=str, required=True, help='Filepath to the input Excel file.')
        parser.add_argument('--xslt', type=str, required=True, help='Filepath to the input XSLT file.')
        parser.add_argument('--o', type=str, required=False, default='../output/',
                            help='Output directory for generated files.')

        args = parser.parse_args()
        return cls(
            n=args.n,
            cleanup=args.cleanup,
            xlsx=args.xlsx,
            xslt=args.xslt,
            output_dir=args.o
        )
