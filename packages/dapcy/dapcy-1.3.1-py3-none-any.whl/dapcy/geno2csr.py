import time

import bio2zarr.vcf as v2z
import numpy as np
import sgkit as sg
from bed_reader import open_bed
from scipy.sparse import csr_matrix


def load_zarr(zarr_file):
    """
    Returns a sparse csr matrix with the allele dosages from a zarr file.
    Parameters:
        zarr_file (str): Path to the input zarr file
    Returns:
        xs (scipy.sparse.csr_matrix): Sparse matrix with allele dosages.
    """

    # Load zarr stores
    print("Loading zarr file...")
    start_time = time.time()
    ds_zarr = sg.load_dataset(zarr_file)

    print("Fetching dosages...")
    ds = sg.convert_call_to_index(ds_zarr)["call_genotype_index"].values

    # Transpose
    ds = np.transpose(ds)

    # Convert dosages values to sparse CSR format
    print("Transforming into sparse CSR...")
    xs = csr_matrix(ds.astype(np.int32))
    print("Done:  %s seconds" % (time.time() - start_time))

    return xs


def vcf_to_csr(
    variant_file: str,
    output_zarr: str,
    variants_chunk_size: int = 10000,
    worker_processes: int = 0,
):
    """
    Returns a sparse csr matrix with the allele dosages
    starting from a VCF input file.
    Relies on intermediate conversion to Zarr by bio2zarr.
    Parameters:
        variant_file (str): Path to the input VCF file
        output_zarr (str): Path to the output Zarr file
        variants_chunk_size (int): Chunk size in the variants dimension
            (defaults to 10000)
        worker_processes (int): Number of worker processes (defaults to 0,
            which implies all available cores)
    Returns:
        xs (scipy.sparse.csr_matrix): Sparse matrix with allele dosages.
    """
    # Convert VCF to Zarr and load with sgkit
    print("Reading VCF...")
    start_time = time.time()

    # Use bio2zarr API to convert VCF to Zarr at specified location
    v2z.convert(
        [variant_file],
        output_zarr,
        variants_chunk_size=variants_chunk_size,
        worker_processes=worker_processes,
    )

    # Load the Zarr stores
    ds_zarr = sg.load_dataset(output_zarr)

    print("Fetching dosages...")
    ds = sg.convert_call_to_index(ds_zarr)["call_genotype_index"].values

    # Transpose
    ds = np.transpose(ds)

    # Convert dosages values to sparse CSR format
    print("Transforming into sparse CSR...")
    xs = csr_matrix(ds.astype(np.int32))

    print("Done:  %s seconds" % (time.time() - start_time))
    return xs


def bed_to_csr(bed_file):
    """
    Returns a sparse csr matrix with the allele counts for bi-allelic alleles from bed file.
    Parameters:
        bed_file (str): Path to the input BED file
    Returns:
        xs (scipy.sparse.csr_matrix): Sparse matrix with allele counts.
    """
    # Read BED file
    print("Reading BED file and extracting genotype matrix")
    start_time = time.time()
    bed = open_bed(bed_file)
    geno = bed.read()
    geno = np.nan_to_num(geno, nan=-1)

    # Transform into CSR
    print("Transforming into sparse CSR...")
    xs = csr_matrix(geno)
    print("Done:  %s seconds" % (time.time() - start_time))

    return xs
