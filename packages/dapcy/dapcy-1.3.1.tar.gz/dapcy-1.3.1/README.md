[![GitLab Release](https://img.shields.io/gitlab/v/release/uhasselt-bioinfo%2Fdapcy)](https://gitlab.com/uhasselt-bioinfo/dapcy/-/releases) [![GitLab Last Commit](https://img.shields.io/gitlab/last-commit/uhasselt-bioinfo%2Fdapcy)](https://gitlab.com/uhasselt-bioinfo/dapcy/-/commits/main) [![PyPI - Version](https://img.shields.io/pypi/v/dapcy)](https://pypi.org/project/dapcy/) [![Conda Version](https://img.shields.io/conda/vn/bioconda/dapcy)](https://anaconda.org/bioconda/dapcy) [![GitLab License](https://img.shields.io/gitlab/license/uhasselt-bioinfo%2Fdapcy)](https://gitlab.com/uhasselt-bioinfo/dapcy/-/blob/main/LICENSE)

# DAPCy

DAPCy is a Python package that enhances the Discriminant Analysis of Principal Components (DAPC) method for population genetics ([Jombart et al. 2010](https://bmcgenomdata.biomedcentral.com/articles/10.1186/1471-2156-11-94)). Using the scikit-learn library, DAPCy efficiently handles large genomic datasets. It supports VCF and BED files, utilizes compressed sparse matrices, and employs truncated SVD for dimensionality reduction. The package also includes k-fold cross-validation for robust model evaluation and offers tools for clustering and visualizing genetic data. DAPCy is designed to be more computationally efficient and memory-friendly than the original R implementation, making it ideal for population analysis with large genomic datasets.

## Installation

DAPCy is available via `pip` (on [PyPi](https://pypi.org/project/dapcy/)) or `conda`/`mamba` (on the [bioconda channel](https://anaconda.org/bioconda/dapcy)). It should ideally be installed inside a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/).

> Note: DAPCy support for VCF is currently not available natively on Windows platforms due to its dependency on [`bio2zarr`](https://github.com/sgkit-dev/bio2zarr) (which in turn depends on [`Cyvcf2`](https://github.com/brentp/cyvcf2)). We suggest Windows users to install the package inside a [WSL environment](https://learn.microsoft.com/en-us/windows/wsl/install) if they need to import VCF files. Note that using a Zarr file as an input is still possible on Windows.

> Note: While Python >= 3.13 is supported, conda users need to use Python ≤ 3.12 until upstream packages are updated to avoid pinned version conflicts in environments (due to cyvcf2 and/or bed-reader not having conda builds >= 3.12).

`pip`:

```
python -m venv <my-env>
source <my-env>/bin/activate
pip install dapcy
```

`conda`/`mamba`:

```
conda create --name <my-env>
conda activate <my-env>
conda install -c bioconda dapcy
```

## Documentation and tutorial

For more information on how to use DAPCy, please refer to the documentation: [https://uhasselt-bioinfo.gitlab.io/dapcy/reference/](https://uhasselt-bioinfo.gitlab.io/dapcy/reference/).

### Tutorial: The _Plasmodium falciparum_ Pf7 dataset from the MalariaGEN Consortium

We have created a tutorial on how to use the package, using the [_Plasmodium falciparum_ Pf7 dataset](https://wellcomeopenresearch.org/articles/8-22/v1) as a case study and made it available [here](https://uhasselt-bioinfo.gitlab.io/dapcy/tutorial/). You can also download the [associated Jupyter notebook](https://gitlab.com/uhasselt-bioinfo/dapcy/-/raw/main/docs/tutorial.ipynb?ref_type=heads&inline=false) from this repository to play around with the code yourself. All files used in the tutorial can be found in this [Zenodo archive](https://zenodo.org/doi/10.5281/zenodo.12804434).

We have also provided a simple [example script](https://gitlab.com/uhasselt-bioinfo/dapcy/-/tree/main/example_script?ref_type=heads) in the git repository.

## Citation

If you use DAPCy in your own work, you can cite:

> Alejandro Correa Rojo, Pieter Moris, Hanne Meuwissen, Pieter Monsieurs, Dirk Valkenborg, DAPCy: a Python package for the discriminant analysis of principal components method for population genetic analyses, Bioinformatics Advances, Volume 5, Issue 1, 2025, vbaf143, https://doi.org/10.1093/bioadv/vbaf143

## Release notes

See [https://uhasselt-bioinfo.gitlab.io/dapcy/about/release_notes/](https://uhasselt-bioinfo.gitlab.io/dapcy/about/release_notes/).

## Contributors

- [Alejandro Correa Rojo](https://orcid.org/0000-0002-5244-6384)
- [Pieter Moris](https://orcid.org/0000-0003-4242-4939)
- Hanne Meuwissen
- [Pieter Monsieurs](https://orcid.org/0000-0003-2214-6652)
- [Dirk Valkenborg](https://orcid.org/0000-0002-1877-3496)
