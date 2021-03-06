from typing import Iterator

from pysam import VariantFile, VariantRecord
from sys import argv

env = {
    "__builtins__": None,
    "__file__": None,
    "__name__": None,
    "globals": None,
    "locals": None
}


def filter_vcf(vcf: VariantFile, expression: str) -> Iterator[VariantRecord]:
    header = vcf.header
    for name in header.info:
        vars()[name] = None

    for rec in header.records: 
        if rec.get("ID") == "ANN": 
            ann_names = list(map(str.strip, rec.get("Description").split("'")[1].split("|"))) 

    for record in vcf:
        for key in record.info:
            vars()[key] = record.info[key]
        # TODO properly restrict env and locals
        ann = vars()["ANN"]
        ANNO = dict(zip(ann_names, zip(*[list(map(str.strip, a.split('|'))) for a in ann])))
        available_vars = locals()
        if eval(expression, env, available_vars):
            yield record


if __name__ == "__main__":
    expression = argv[2]
    with VariantFile(argv[1]) as vcf:
        with VariantFile('-', 'w', header=vcf.header) as out:
            for record in filter_vcf(vcf, expression):
                out.write(record)
