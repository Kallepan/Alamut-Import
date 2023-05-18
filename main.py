import pandas as pd
import requests as req
import urllib3

import os
import json
import time
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

# Should probably be in an env file or something
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgwMjkyMzMyLCJpYXQiOjE2ODAyNDkxMzIsImp0aSI6ImZhMzlkZjU2YjU2YjRjNWY4OGFhZjVkNjMwZjFmYWI4IiwidXNlcl9pZCI6MX0.21ulAbeHrChTpT1ppG3I6hAlLMlv34x8aLYpiIr_FAE"


# import the variants, GRCh37, and GRCh38
def import_variants() -> pd.DataFrame:
    variants = pd.read_csv(os.path.join('data', "final.txt"), sep='\t', encoding="utf-8", header=0, encoding_errors='ignore')
    variants = variants.loc[(variants["Assembly"] == "GRCh38") | (variants["Assembly"] == "GRCh37")]

    return variants

def get_grch37() -> pd.DataFrame:
    grch37 = pd.read_csv(os.path.join('data', "GRCh37.csv"), sep=';', header=0)

    return grch37

def get_grch38() -> pd.DataFrame:
    grch38 = pd.read_csv(os.path.join('data', "GRCh38.csv"), sep=';', header=0)

    return grch38




def main():
    variants = import_variants()
    grch37 = get_grch37()
    grch38 = get_grch38()

    variants.reset_index()

    faulty_reqs = []
    for i, variant in variants.iterrows():
        # Find out which genomic reference transcript is the correct one by filtering for GRCh37 or GRCh38 
        active_assembly = grch37 if variant["Assembly"] == "GRCh37" else grch38

        transcript = active_assembly.loc[active_assembly["chromosome"] == variant["Chromosome"]]["refseq"].values[0]

        # Add the genomic_ref transcript to the variant
        variant["genome_ref"] = transcript

        # Extract status from Classification
        # Basically just a mapping from the classification to the status taken from the frontend (See constants.STATUS_ENCODING)
        status = 0
        if variant["Classification"] == "Pathogenic" or variant["Classification"] == "Likely pathogenic":
            status = 3
        if variant["Classification"] == "Benign" or variant["Classification"] == "Likely benign":
            status = 1
        if variant["Classification"] == "Uncertain significance":
            status = 2

        # Build post request from variant
        # important: To generate the primary key genomic_reference, accession_number, and genomic_change are required
        data = json.dumps({
            "gene": variant["Gene"],
            "comment": f"{variant['Notes']}".replace("\\n", "\n"),
            "mrna_reference": variant["Transcript"],
            "aa_change": variant["pNomen"],
            "cDNA_change": variant["cNomen"],
            "status": status,
            "genomic_reference": variant["genome_ref"].split(".")[0],
            "accession_number": variant["genome_ref"].split(".")[1],
            "genomic_change": variant["gNomen"],
        })
        
        # Send post request
        res = req.post(
            "https://vargen.labmed.de/api/v1/variants/", 
            data=data, 
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {TOKEN}' 
            },
            verify=False # this is there just to allow self-signed certificates (important for local development)
        )
        time.sleep(0.1)

        # Debug info to see which variant is currently being processed
        print(i, f"{variant['Gene']}: {variant['gNomen']}, {variant['Transcript']}", res.status_code)
 
        if res.status_code != 201:
            faulty_reqs.append(variant)

    print(faulty_reqs)
    pd.DataFrame(faulty_reqs).to_csv(os.path.join('data', "faulty_reqs.csv"), sep=';', header=True, index=False)

if __name__ == '__main__':
    main()