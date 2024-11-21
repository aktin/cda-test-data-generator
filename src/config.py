import argparse
from dataclasses import dataclass

@dataclass
class Config:
    """
    Configuration class to hold command-line arguments.

    Attributes:
        n (int): Number of patients to generate.
        cleanup (bool): Flag to indicate whether to remove intermediate CSV file after processing.
        xlsx (str): Filepath to the input Excel file.
        xslt (str): Filepath to the input XSLT file.
        output_dir (str): Output directory for generated files.
    """
    number: int
    cleanup: bool
    xlsx: str
    xslt: str
    output_dir: str

    @classmethod
    def from_args(cls):
        """
        Parse command-line arguments and create a Config instance.

        Returns:
            Config: An instance of the Config class populated with command-line arguments.
        """
        parser = argparse.ArgumentParser(prog='cda-test-data-generator', description='Process Excel to CDA.')
        parser.add_argument('--number', type=int, required=True, help='Number of patients to generate.')
        parser.add_argument('--cleanup', action='store_true', help='Remove intermediate CSV file after processing.')
        parser.add_argument('--xlsx', type=str, required=True, help='Filepath to the input Excel file.')
        parser.add_argument('--xslt', type=str, required=True, help='Filepath to the input XSLT file.')
        parser.add_argument('--output', type=str, required=False, default='.',
                            help='Output directory for generated files.')

        args = parser.parse_args()
        return cls(
            number=args.number,
            cleanup=args.cleanup,
            xlsx=args.xlsx,
            xslt=args.xslt,
            output_dir=args.output
        )

# Create a Config instance from command-line arguments
config = Config.from_args()