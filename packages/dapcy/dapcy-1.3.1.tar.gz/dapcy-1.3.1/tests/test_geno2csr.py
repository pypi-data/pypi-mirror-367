import numpy as np
import pytest
from scipy.sparse import csr_matrix
import numpy as np
import pytest
from scipy.sparse import csr_matrix
from unittest.mock import patch, MagicMock
from .geno2csr import bed_to_csr, load_zarr, vcf_to_csr


def test_bed_to_csr_basic():
    geno_matrix = np.array([[0, 1, np.nan], [2, np.nan, 1]])
    expected_matrix = np.array([[0, 1, -1], [2, -1, 1]])

    mock_bed = MagicMock()
    mock_bed.read.return_value = geno_matrix

    with patch("dapcy.geno2csr.open_bed", return_value=mock_bed) as mock_open_bed:
        xs = bed_to_csr("fake.bed")
        mock_open_bed.assert_called_once_with("fake.bed")
        assert isinstance(xs, csr_matrix)
        np.testing.assert_array_equal(xs.toarray(), expected_matrix)


def test_bed_to_csr_empty():
    geno_matrix = np.empty((0, 0))
    mock_bed = MagicMock()
    mock_bed.read.return_value = geno_matrix

    with patch("dapcy.geno2csr.open_bed", return_value=mock_bed):
        xs = bed_to_csr("empty.bed")
        assert isinstance(xs, csr_matrix)
        assert xs.shape == (0, 0)


def test_bed_to_csr_all_nan():
    geno_matrix = np.full((2, 2), np.nan)
    expected_matrix = np.full((2, 2), -1)
    mock_bed = MagicMock()
    mock_bed.read.return_value = geno_matrix

    with patch("dapcy.geno2csr.open_bed", return_value=mock_bed):
        xs = bed_to_csr("allnan.bed")
        assert isinstance(xs, csr_matrix)
        np.testing.assert_array_equal(xs.toarray(), expected_matrix)


def test_load_zarr_returns_csr_matrix():
    # Mock sgkit and its return values
    mock_ds_zarr = MagicMock()
    mock_values = np.array([[0, 1], [2, 3]])
    with (
        patch("dapcy.geno2csr.sg.load_dataset", return_value=mock_ds_zarr),
        patch(
            "dapcy.geno2csr.sg.convert_call_to_index",
            return_value={"call_genotype_index": MagicMock(values=mock_values)},
        ),
    ):
        xs = load_zarr("fake.zarr")
        assert isinstance(xs, csr_matrix)
        np.testing.assert_array_equal(xs.toarray(), mock_values.T)


def test_vcf_to_csr_calls_bio2zarr_and_returns_csr():
    mock_ds_zarr = MagicMock()
    mock_values = np.array([[0, 1], [2, 3]])
    with (
        patch("dapcy.geno2csr.v2z.convert") as mock_convert,
        patch("dapcy.geno2csr.sg.load_dataset", return_value=mock_ds_zarr),
        patch(
            "dapcy.geno2csr.sg.convert_call_to_index",
            return_value={"call_genotype_index": MagicMock(values=mock_values)},
        ),
    ):
        xs = vcf_to_csr("fake.vcf", "fake.zarr")
        mock_convert.assert_called_once()
        assert isinstance(xs, csr_matrix)
        np.testing.assert_array_equal(xs.toarray(), mock_values.T)


@pytest.mark.parametrize(
    "geno_matrix",
    [
        np.array([[0, 0], [0, 0]]),
        np.array([[1, 2], [3, 4]]),
        np.array([[np.nan, 1], [2, np.nan]]),
    ],
)
def test_bed_to_csr_various(geno_matrix):
    expected_matrix = np.nan_to_num(geno_matrix, nan=-1)
    mock_bed = MagicMock()
    mock_bed.read.return_value = geno_matrix
    with patch("dapcy.geno2csr.open_bed", return_value=mock_bed):
        xs = bed_to_csr("various.bed")
        assert isinstance(xs, csr_matrix)
        np.testing.assert_array_equal(xs.toarray(), expected_matrix)
