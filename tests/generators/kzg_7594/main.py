"""
KZG test vectors generator for EIP-7594
"""

from typing import Tuple, Iterable, Any, Callable, Dict

from eth_utils import encode_hex

from eth2spec.eip7594 import spec
from eth2spec.gen_helpers.gen_base import gen_runner, gen_typing
from eth2spec.test.helpers.constants import EIP7594
from eth2spec.test.helpers.typing import SpecForkName
from eth2spec.test.utils.kzg_tests import (
    CELL_RANDOM_VALID1,
    CELL_RANDOM_VALID2,
    G1,
    INVALID_BLOBS,
    INVALID_G1_POINTS,
    INVALID_INDIVIDUAL_CELL_BYTES,
    VALID_BLOBS,
    VALID_CELLS_AND_PROOFS,
    VALID_COMMITMENTS,
    VALID_INDIVIDUAL_RANDOM_CELL_BYTES,
    bls_add_one,
    encode_hex_list,
    expect_exception,
    make_id,
)
from eth2spec.utils import bls


###############################################################################
# Test cases for compute_cells_and_kzg_proofs
###############################################################################

def case_compute_cells_and_kzg_proofs():
    # Valid cases
    for blob in VALID_BLOBS:
        cells, proofs = spec.compute_cells_and_kzg_proofs(blob)
        # Save cells & proofs here to save on time.
        VALID_CELLS_AND_PROOFS.append((cells, proofs))
        identifier = make_id(blob)
        yield f'compute_cells_and_kzg_proofs_case_valid_{identifier}', {
            'input': {
                'blob': encode_hex(blob),
            },
            'output': (encode_hex_list(cells), encode_hex_list(proofs))
        }

    # Edge case: Invalid blobs
    for blob in INVALID_BLOBS:
        expect_exception(spec.compute_cells_and_kzg_proofs, blob)
        identifier = make_id(blob)
        yield f'compute_cells_and_kzg_proofs_case_invalid_blob_{identifier}', {
            'input': {
                'blob': encode_hex(blob)
            },
            'output': None
        }


###############################################################################
# Test cases for verify_cell_kzg_proof
###############################################################################

def case_verify_cell_kzg_proof():
    # Valid cases
    for i in range(len(VALID_BLOBS)):
        cells, proofs = VALID_CELLS_AND_PROOFS[i]
        commitment = VALID_COMMITMENTS[i]
        cell_index = (2 ** i - 1) % spec.CELLS_PER_EXT_BLOB
        cell = cells[cell_index]
        proof = proofs[cell_index]
        assert spec.verify_cell_kzg_proof(commitment, cell_index, cell, proof)
        identifier = make_id(commitment, cell_index, cell, proof)
        yield f'verify_cell_kzg_proof_case_valid_{identifier}', {
            'input': {
                'commitment': encode_hex(commitment),
                'cell_index': cell_index,
                'cell': encode_hex(cell),
                'proof': encode_hex(proof),
            },
            'output': True
        }

    # Incorrect commitment
    for i in range(len(VALID_BLOBS)):
        cells, proofs = VALID_CELLS_AND_PROOFS[i]
        commitment = bls_add_one(VALID_COMMITMENTS[i])
        cell_index = 99 % spec.CELLS_PER_EXT_BLOB
        cell = cells[cell_index]
        proof = proofs[cell_index]
        assert not spec.verify_cell_kzg_proof(commitment, cell_index, cell, proof)
        identifier = make_id(commitment, cell_index, cell, proof)
        yield f'verify_cell_kzg_proof_case_incorrect_commitment_{identifier}', {
            'input': {
                'commitment': encode_hex(commitment),
                'cell_index': cell_index,
                'cell': encode_hex(cell),
                'proof': encode_hex(proof),
            },
            'output': False
        }

    # Incorrect cell
    for i in range(len(VALID_INDIVIDUAL_RANDOM_CELL_BYTES)):
        cell_index = 16 % spec.CELLS_PER_EXT_BLOB
        commitment = VALID_COMMITMENTS[i]
        cells, proofs = VALID_CELLS_AND_PROOFS[i]
        cell = VALID_INDIVIDUAL_RANDOM_CELL_BYTES[i]
        proof = proofs[cell_index]
        assert not spec.verify_cell_kzg_proof(commitment, cell_index, cell, proof)
        identifier = make_id(commitment, cell_index, cell, proof)
        yield f'verify_cell_kzg_proof_case_incorrect_cell_{identifier}', {
            'input': {
                'commitment': encode_hex(commitment),
                'cell_index': cell_index,
                'cell': encode_hex(cell),
                'proof': encode_hex(proof),
            },
            'output': False
        }

    # Incorrect proof
    for i in range(len(VALID_BLOBS)):
        cell_index = 91 % spec.CELLS_PER_EXT_BLOB
        commitment = VALID_COMMITMENTS[i]
        cells, proofs = VALID_CELLS_AND_PROOFS[i]
        cell = cells[cell_index]
        proof = bls_add_one(proofs[cell_index])
        assert not spec.verify_cell_kzg_proof(commitment, cell_index, cell, proof)
        identifier = make_id(commitment, cell_index, cell, proof)
        yield f'verify_cell_kzg_proof_case_incorrect_proof_{identifier}', {
            'input': {
                'commitment': encode_hex(commitment),
                'cell_index': cell_index,
                'cell': encode_hex(cell),
                'proof': encode_hex(proof),
            },
            'output': False
        }

    # Edge case: Invalid commitment
    for commitment in INVALID_G1_POINTS:
        cells, proofs = VALID_CELLS_AND_PROOFS[0]
        cell_index = 81 % spec.CELLS_PER_EXT_BLOB
        cell = cells[cell_index]
        proof = proofs[cell_index]
        expect_exception(spec.verify_cell_kzg_proof, commitment, cell_index, cell, proof)
        identifier = make_id(commitment, cell_index, cell, proof)
        yield f'verify_cell_kzg_proof_case_invalid_commitment_{identifier}', {
            'input': {
                'commitment': encode_hex(commitment),
                'cell_index': cell_index,
                'cell': encode_hex(cell),
                'proof': encode_hex(proof),
            },
            'output': None
        }

    # Edge case: Invalid cell_index
    for cell_index in [spec.CELLS_PER_EXT_BLOB, spec.CELLS_PER_EXT_BLOB + 1]:
        cells, proofs = VALID_CELLS_AND_PROOFS[1]
        commitment = VALID_COMMITMENTS[1]
        cell = cells[0]
        proof = proofs[0]
        expect_exception(spec.verify_cell_kzg_proof, commitment, cell_index, cell, proof)
        identifier = make_id(commitment, cell_index, cell, proof)
        yield f'verify_cell_kzg_proof_case_invalid_cell_index_{identifier}', {
            'input': {
                'commitment': encode_hex(commitment),
                'cell_index': cell_index,
                'cell': encode_hex(cell),
                'proof': encode_hex(proof),
            },
            'output': None
        }

    # Edge case: Invalid cell
    for cell in INVALID_INDIVIDUAL_CELL_BYTES:
        cell_index = 32 % spec.CELLS_PER_EXT_BLOB
        commitment = VALID_COMMITMENTS[2]
        cells, proofs = VALID_CELLS_AND_PROOFS[2]
        proof = proofs[cell_index]
        expect_exception(spec.verify_cell_kzg_proof, commitment, cell_index, cell, proof)
        identifier = make_id(commitment, cell_index, cell, proof)
        yield f'verify_cell_kzg_proof_case_invalid_cell_{identifier}', {
            'input': {
                'commitment': encode_hex(commitment),
                'cell_index': cell_index,
                'cell': encode_hex(cell),
                'proof': encode_hex(proof),
            },
            'output': None
        }

    # Edge case: Invalid proof
    for proof in INVALID_G1_POINTS:
        cells, _ = VALID_CELLS_AND_PROOFS[3]
        commitment = VALID_COMMITMENTS[3]
        cell_index = 36 % spec.CELLS_PER_EXT_BLOB
        cell = cells[cell_index]
        expect_exception(spec.verify_cell_kzg_proof, commitment, cell_index, cell, proof)
        identifier = make_id(commitment, cell_index, cell, proof)
        yield f'verify_cell_kzg_proof_case_invalid_proof_{identifier}', {
            'input': {
                'commitment': encode_hex(commitment),
                'cell_index': cell_index,
                'cell': encode_hex(cell),
                'proof': encode_hex(proof),
            },
            'output': None
        }


###############################################################################
# Test cases for verify_cell_kzg_proof_batch
###############################################################################

def case_verify_cell_kzg_proof_batch():
    # Valid cases
    for i in range(len(VALID_BLOBS)):
        cells, proofs = VALID_CELLS_AND_PROOFS[i]
        row_commitments = [VALID_COMMITMENTS[i]]
        row_indices = [0] * spec.CELLS_PER_EXT_BLOB
        column_indices = list(range(spec.CELLS_PER_EXT_BLOB))
        assert spec.verify_cell_kzg_proof_batch(row_commitments, row_indices, column_indices, cells, proofs)
        identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
        yield f'verify_cell_kzg_proof_batch_case_valid_{identifier}', {
            'input': {
                'row_commitments': encode_hex_list(row_commitments),
                'row_indices': row_indices,
                'column_indices': column_indices,
                'cells': encode_hex_list(cells),
                'proofs': encode_hex_list(proofs),
            },
            'output': True
        }

    # Valid: zero cells
    cells, row_commitments, row_indices, column_indices, proofs = [], [], [], [], []
    assert spec.verify_cell_kzg_proof_batch(row_commitments, row_indices, column_indices, cells, proofs)
    identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
    yield f'verify_cell_kzg_proof_batch_case_valid_zero_cells_{identifier}', {
        'input': {
            'row_commitments': encode_hex_list(row_commitments),
            'row_indices': row_indices,
            'column_indices': column_indices,
            'cells': encode_hex_list(cells),
            'proofs': encode_hex_list(proofs),
        },
        'output': True
    }

    # Valid: Verify cells from multiple blobs
    cells0, proofs0 = VALID_CELLS_AND_PROOFS[0]
    cells1, proofs1 = VALID_CELLS_AND_PROOFS[1]
    row_commitments = VALID_COMMITMENTS[:2]
    row_indices = [0, 1]
    column_indices = [0, 0]
    cells = [cells0[0], cells1[0]]
    proofs = [proofs0[0], proofs1[0]]
    assert spec.verify_cell_kzg_proof_batch(row_commitments, row_indices, column_indices, cells, proofs)
    identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
    yield f'verify_cell_kzg_proof_batch_case_valid_multiple_blobs_{identifier}', {
        'input': {
            'row_commitments': encode_hex_list(row_commitments),
            'row_indices': row_indices,
            'column_indices': column_indices,
            'cells': encode_hex_list(cells),
            'proofs': encode_hex_list(proofs),
        },
        'output': True
    }

    # Valid: Unused row commitments
    cells, proofs = VALID_CELLS_AND_PROOFS[2]
    cells, proofs = cells[:3], proofs[:3]
    # Provide list of all commitments
    row_commitments = VALID_COMMITMENTS
    row_indices = [2] * len(cells)
    column_indices = list(range(len(cells)))
    assert spec.verify_cell_kzg_proof_batch(row_commitments, row_indices, column_indices, cells, proofs)
    identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
    yield f'verify_cell_kzg_proof_batch_case_valid_unused_row_commitments_{identifier}', {
        'input': {
            'row_commitments': encode_hex_list(row_commitments),
            'row_indices': row_indices,
            'column_indices': column_indices,
            'cells': encode_hex_list(cells),
            'proofs': encode_hex_list(proofs),
        },
        'output': True
    }

    # Valid: Same cell multiple times
    row_commitments = [VALID_COMMITMENTS[3]]
    num_duplicates = 3
    row_indices = [0] * num_duplicates
    column_indices = [0] * num_duplicates
    cells = [VALID_CELLS_AND_PROOFS[3][0][0]] * num_duplicates
    proofs = [VALID_CELLS_AND_PROOFS[3][1][0]] * num_duplicates
    assert spec.verify_cell_kzg_proof_batch(row_commitments, row_indices, column_indices, cells, proofs)
    identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
    yield f'verify_cell_kzg_proof_batch_case_valid_same_cell_multiple_times_{identifier}', {
        'input': {
            'row_commitments': encode_hex_list(row_commitments),
            'row_indices': row_indices,
            'column_indices': column_indices,
            'cells': encode_hex_list(cells),
            'proofs': encode_hex_list(proofs),
        },
        'output': True
    }

    # Incorrect row commitment
    cells, proofs = VALID_CELLS_AND_PROOFS[5]
    cells, proofs = cells[:1], proofs[:1]
    # Change commitment so it's wrong
    row_commitments = [bls_add_one(VALID_COMMITMENTS[5])]
    row_indices = [0] * len(cells)
    column_indices = list(range(len(cells)))
    assert not spec.verify_cell_kzg_proof_batch(row_commitments, row_indices, column_indices, cells, proofs)
    identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
    yield f'verify_cell_kzg_proof_batch_case_incorrect_row_commitment_{identifier}', {
        'input': {
            'row_commitments': encode_hex_list(row_commitments),
            'row_indices': row_indices,
            'column_indices': column_indices,
            'cells': encode_hex_list(cells),
            'proofs': encode_hex_list(proofs),
        },
        'output': False
    }

    # Incorrect cell
    cells, proofs = VALID_CELLS_AND_PROOFS[6]
    cells, proofs = cells[:1], proofs[:1]
    row_commitments = [VALID_COMMITMENTS[6]]
    row_indices = [0] * len(cells)
    column_indices = list(range(len(cells)))
    # Change last cell so it's wrong
    cells[-1] = CELL_RANDOM_VALID2
    assert not spec.verify_cell_kzg_proof_batch(row_commitments, row_indices, column_indices, cells, proofs)
    identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
    yield f'verify_cell_kzg_proof_batch_case_incorrect_cell_{identifier}', {
        'input': {
            'row_commitments': encode_hex_list(row_commitments),
            'row_indices': row_indices,
            'column_indices': column_indices,
            'cells': encode_hex_list(cells),
            'proofs': encode_hex_list(proofs),
        },
        'output': False
    }

    # Incorrect proof
    cells, proofs = VALID_CELLS_AND_PROOFS[0]
    cells, proofs = cells[:1], proofs[:1]
    row_commitments = [VALID_COMMITMENTS[0]]
    row_indices = [0] * len(cells)
    column_indices = list(range(len(cells)))
    # Change last proof so it's wrong
    proofs[-1] = bls_add_one(proofs[-1])
    assert not spec.verify_cell_kzg_proof_batch(row_commitments, row_indices, column_indices, cells, proofs)
    identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
    yield f'verify_cell_kzg_proof_batch_case_incorrect_proof_{identifier}', {
        'input': {
            'row_commitments': encode_hex_list(row_commitments),
            'row_indices': row_indices,
            'column_indices': column_indices,
            'cells': encode_hex_list(cells),
            'proofs': encode_hex_list(proofs),
        },
        'output': False
    }

    # Edge case: Invalid row commitment
    for i, commitment in enumerate(INVALID_G1_POINTS):
        cells, proofs = VALID_CELLS_AND_PROOFS[i % len(INVALID_G1_POINTS)]
        cells, proofs = cells[:1], proofs[:1]
        # Set row_commitments to the invalid commitment
        row_commitments = [commitment]
        row_indices = [0] * len(cells)
        column_indices = list(range(len(cells)))
        expect_exception(spec.verify_cell_kzg_proof_batch, row_commitments, row_indices, column_indices, cells, proofs)
        identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
        yield f'verify_cell_kzg_proof_batch_case_invalid_row_commitment_{identifier}', {
            'input': {
                'row_commitments': encode_hex_list(row_commitments),
                'row_indices': row_indices,
                'column_indices': column_indices,
                'cells': encode_hex_list(cells),
                'proofs': encode_hex_list(proofs),
            },
            'output': None
        }

    # Edge case: Invalid row_index
    cells, proofs = VALID_CELLS_AND_PROOFS[0]
    cells, proofs = cells[:1], proofs[:1]
    row_commitments = [VALID_COMMITMENTS[0]]
    row_indices = [0] * len(cells)
    # Set first row index to an invalid value
    row_indices[0] = 1
    column_indices = list(range(len(cells)))
    expect_exception(spec.verify_cell_kzg_proof_batch, row_commitments, row_indices, column_indices, cells, proofs)
    identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
    yield f'verify_cell_kzg_proof_batch_case_invalid_row_index_{identifier}', {
        'input': {
            'row_commitments': encode_hex_list(row_commitments),
            'row_indices': row_indices,
            'column_indices': column_indices,
            'cells': encode_hex_list(cells),
            'proofs': encode_hex_list(proofs),
        },
        'output': None
    }

    # Edge case: Invalid column_index
    cells, proofs = VALID_CELLS_AND_PROOFS[1]
    cells, proofs = cells[:1], proofs[:1]
    row_commitments = [VALID_COMMITMENTS[1]]
    row_indices = [0] * len(cells)
    column_indices = list(range(len(cells)))
    # Set first column index to an invalid value
    column_indices[0] = spec.CELLS_PER_EXT_BLOB
    expect_exception(spec.verify_cell_kzg_proof_batch, row_commitments, row_indices, column_indices, cells, proofs)
    identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
    yield f'verify_cell_kzg_proof_batch_case_invalid_column_index_{identifier}', {
        'input': {
            'row_commitments': encode_hex_list(row_commitments),
            'row_indices': row_indices,
            'column_indices': column_indices,
            'cells': encode_hex_list(cells),
            'proofs': encode_hex_list(proofs),
        },
        'output': None
    }

    # Edge case: Invalid cell
    for i, cell in enumerate(INVALID_INDIVIDUAL_CELL_BYTES):
        cells, proofs = VALID_CELLS_AND_PROOFS[i % len(INVALID_INDIVIDUAL_CELL_BYTES)]
        cells, proofs = cells[:1], proofs[:1]
        row_commitments = [VALID_COMMITMENTS[i % len(INVALID_INDIVIDUAL_CELL_BYTES)]]
        row_indices = [0] * len(cells)
        column_indices = list(range(len(cells)))
        # Set first cell to the invalid cell
        cells[0] = cell
        expect_exception(spec.verify_cell_kzg_proof_batch, row_commitments, row_indices, column_indices, cells, proofs)
        identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
        yield f'verify_cell_kzg_proof_batch_case_invalid_cell_{identifier}', {
            'input': {
                'row_commitments': encode_hex_list(row_commitments),
                'row_indices': row_indices,
                'column_indices': column_indices,
                'cells': encode_hex_list(cells),
                'proofs': encode_hex_list(proofs),
            },
            'output': None
        }

    # Edge case: Invalid proof
    for i, proof in enumerate(INVALID_G1_POINTS):
        cells, proofs = VALID_CELLS_AND_PROOFS[i % len(INVALID_G1_POINTS)]
        cells, proofs = cells[:1], proofs[:1]
        row_commitments = [VALID_COMMITMENTS[i % len(INVALID_G1_POINTS)]]
        row_indices = [0] * len(cells)
        column_indices = list(range(len(cells)))
        # Set first proof to the invalid proof
        proofs[0] = proof
        expect_exception(spec.verify_cell_kzg_proof_batch, row_commitments, row_indices, column_indices, cells, proofs)
        identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
        yield f'verify_cell_kzg_proof_batch_case_invalid_proof_{identifier}', {
            'input': {
                'row_commitments': encode_hex_list(row_commitments),
                'row_indices': row_indices,
                'column_indices': column_indices,
                'cells': encode_hex_list(cells),
                'proofs': encode_hex_list(proofs),
            },
            'output': None
        }

        # Edge case: Missing a row commitment
        cells, proofs = VALID_CELLS_AND_PROOFS[0]
        cells, proofs = cells[:1], proofs[:1]
        # Do not include the row commitment
        row_commitments = []
        row_indices = [0] * len(cells)
        column_indices = list(range(len(cells)))
        expect_exception(spec.verify_cell_kzg_proof_batch, row_commitments, row_indices, column_indices, cells, proofs)
        identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
        yield f'verify_cell_kzg_proof_batch_case_invalid_missing_row_commitment_{identifier}', {
            'input': {
                'row_commitments': encode_hex_list(row_commitments),
                'row_indices': row_indices,
                'column_indices': column_indices,
                'cells': encode_hex_list(cells),
                'proofs': encode_hex_list(proofs),
            },
            'output': None
        }

        # Edge case: Missing a row index
        cells, proofs = VALID_CELLS_AND_PROOFS[1]
        cells, proofs = cells[:2], proofs[:2]
        row_commitments = [VALID_COMMITMENTS[1]]
        # Leave off one of the row indices
        row_indices = [0] * (len(cells) - 1)
        column_indices = list(range(len(cells)))
        expect_exception(spec.verify_cell_kzg_proof_batch, row_commitments, row_indices, column_indices, cells, proofs)
        identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
        yield f'verify_cell_kzg_proof_batch_case_invalid_missing_row_index_{identifier}', {
            'input': {
                'row_commitments': encode_hex_list(row_commitments),
                'row_indices': row_indices,
                'column_indices': column_indices,
                'cells': encode_hex_list(cells),
                'proofs': encode_hex_list(proofs),
            },
            'output': None
        }

        # Edge case: Missing a column index
        cells, proofs = VALID_CELLS_AND_PROOFS[2]
        cells, proofs = cells[:2], proofs[:2]
        row_commitments = [VALID_COMMITMENTS[2]]
        row_indices = [0] * len(cells)
        # Leave off one of the column indices
        column_indices = list(range(len(cells) - 1))
        expect_exception(spec.verify_cell_kzg_proof_batch, row_commitments, row_indices, column_indices, cells, proofs)
        identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
        yield f'verify_cell_kzg_proof_batch_case_invalid_missing_column_index_{identifier}', {
            'input': {
                'row_commitments': encode_hex_list(row_commitments),
                'row_indices': row_indices,
                'column_indices': column_indices,
                'cells': encode_hex_list(cells),
                'proofs': encode_hex_list(proofs),
            },
            'output': None
        }

        # Edge case: Missing a cell
        cells, proofs = VALID_CELLS_AND_PROOFS[3]
        cells, proofs = cells[:2], proofs[:2]
        row_commitments = [VALID_COMMITMENTS[3]]
        row_indices = [0] * len(cells)
        column_indices = list(range(len(cells)))
        # Remove the last proof
        cells = cells[:-1]
        expect_exception(spec.verify_cell_kzg_proof_batch, row_commitments, row_indices, column_indices, cells, proofs)
        identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
        yield f'verify_cell_kzg_proof_batch_case_invalid_missing_cell_{identifier}', {
            'input': {
                'row_commitments': encode_hex_list(row_commitments),
                'row_indices': row_indices,
                'column_indices': column_indices,
                'cells': encode_hex_list(cells),
                'proofs': encode_hex_list(proofs),
            },
            'output': None
        }

        # Edge case: Missing a proof
        cells, proofs = VALID_CELLS_AND_PROOFS[4]
        cells, proofs = cells[:2], proofs[:2]
        row_commitments = [VALID_COMMITMENTS[4]]
        row_indices = [0] * len(cells)
        column_indices = list(range(len(cells)))
        # Remove the last proof
        proofs = proofs[:-1]
        expect_exception(spec.verify_cell_kzg_proof_batch, row_commitments, row_indices, column_indices, cells, proofs)
        identifier = make_id(row_commitments, row_indices, column_indices, cells, proofs)
        yield f'verify_cell_kzg_proof_batch_case_invalid_missing_proof_{identifier}', {
            'input': {
                'row_commitments': encode_hex_list(row_commitments),
                'row_indices': row_indices,
                'column_indices': column_indices,
                'cells': encode_hex_list(cells),
                'proofs': encode_hex_list(proofs),
            },
            'output': None
        }


###############################################################################
# Test cases for recover_cells_and_kzg_proofs
###############################################################################

def case_recover_cells_and_kzg_proofs():
    # Valid: No missing cells
    cells, proofs = VALID_CELLS_AND_PROOFS[0]
    cell_indices = list(range(spec.CELLS_PER_EXT_BLOB))
    recovered_cells, recovered_proofs = spec.recover_cells_and_kzg_proofs(cell_indices, cells, proofs)
    assert recovered_cells == cells
    assert recovered_proofs == proofs
    identifier = make_id(cell_indices, cells, proofs)
    yield f'recover_cells_and_kzg_proofs_case_valid_no_missing_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(cells),
            'proofs': encode_hex_list(proofs),
        },
        'output': (encode_hex_list(recovered_cells), encode_hex_list(recovered_proofs))
    }

    # Valid: Half missing cells (every other cell)
    cells, proofs = VALID_CELLS_AND_PROOFS[1]
    cell_indices = list(range(0, spec.CELLS_PER_EXT_BLOB, 2))
    partial_cells = [cells[cell_index] for cell_index in cell_indices]
    partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
    recovered_cells, recovered_proofs = spec.recover_cells_and_kzg_proofs(cell_indices, partial_cells, partial_proofs)
    assert recovered_cells == cells
    assert recovered_proofs == proofs
    identifier = make_id(cell_indices, partial_cells, partial_proofs)
    yield f'recover_cells_and_kzg_proofs_case_valid_half_missing_every_other_cell_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(partial_cells),
            'proofs': encode_hex_list(partial_proofs),
        },
        'output': (encode_hex_list(recovered_cells), encode_hex_list(recovered_proofs))
    }

    # Valid: Half missing cells (first half)
    cells, proofs = VALID_CELLS_AND_PROOFS[2]
    cell_indices = list(range(0, spec.CELLS_PER_EXT_BLOB // 2))
    partial_cells = [cells[cell_index] for cell_index in cell_indices]
    partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
    recovered_cells, recovered_proofs = spec.recover_cells_and_kzg_proofs(cell_indices, partial_cells, partial_proofs)
    assert recovered_cells == cells
    assert recovered_proofs == proofs
    identifier = make_id(cell_indices, partial_cells)
    yield f'recover_cells_and_kzg_proofs_case_valid_half_missing_first_half_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(partial_cells),
            'proofs': encode_hex_list(partial_proofs),
        },
        'output': (encode_hex_list(recovered_cells), encode_hex_list(recovered_proofs))
    }

    # Valid: Half missing cells (second half)
    cells, proofs = VALID_CELLS_AND_PROOFS[3]
    cell_indices = list(range(spec.CELLS_PER_EXT_BLOB // 2, spec.CELLS_PER_EXT_BLOB))
    partial_cells = [cells[cell_index] for cell_index in cell_indices]
    partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
    recovered_cells, recovered_proofs = spec.recover_cells_and_kzg_proofs(cell_indices, partial_cells, partial_proofs)
    assert recovered_cells == cells
    assert recovered_proofs == proofs
    identifier = make_id(cell_indices, partial_cells)
    yield f'recover_cells_and_kzg_proofs_case_valid_half_missing_second_half_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(partial_cells),
            'proofs': encode_hex_list(partial_proofs),
        },
        'output': (encode_hex_list(recovered_cells), encode_hex_list(recovered_proofs))
    }

    # Edge case: All cells are missing
    cell_indices, partial_cells = [], []
    expect_exception(spec.recover_cells_and_kzg_proofs, cell_indices, partial_cells)
    identifier = make_id(cell_indices, partial_cells)
    yield f'recover_cells_and_kzg_proofs_case_invalid_all_cells_are_missing_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(partial_cells),
            'proofs': encode_hex_list(partial_proofs),
        },
        'output': None
    }

    # Edge case: More than half missing
    cells, proofs = VALID_CELLS_AND_PROOFS[4]
    cell_indices = list(range(spec.CELLS_PER_EXT_BLOB // 2 - 1))
    partial_cells = [cells[cell_index] for cell_index in cell_indices]
    partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
    expect_exception(spec.recover_cells_and_kzg_proofs, cell_indices, partial_cells, partial_proofs)
    identifier = make_id(cell_indices, partial_cells, partial_proofs)
    yield f'recover_cells_and_kzg_proofs_case_invalid_more_than_half_missing_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(partial_cells),
            'proofs': encode_hex_list(partial_proofs),
        },
        'output': None
    }

    # Edge case: More cells provided than CELLS_PER_EXT_BLOB
    cells, proofs = VALID_CELLS_AND_PROOFS[5]
    cell_indices = list(range(spec.CELLS_PER_EXT_BLOB)) + [0]
    partial_cells = [cells[cell_index] for cell_index in cell_indices]
    partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
    expect_exception(spec.recover_cells_and_kzg_proofs, cell_indices, partial_cells, partial_proofs)
    identifier = make_id(cell_indices, partial_cells, partial_proofs)
    yield f'recover_cells_and_kzg_proofs_case_invalid_more_cells_than_cells_per_ext_blob_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(partial_cells),
            'proofs': encode_hex_list(partial_proofs),
        },
        'output': None
    }

    # Edge case: Invalid cell_index
    cells, proofs = VALID_CELLS_AND_PROOFS[6]
    cell_indices = list(range(spec.CELLS_PER_EXT_BLOB // 2))
    partial_cells = [cells[cell_index] for cell_index in cell_indices]
    partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
    # Replace first cell_index with an invalid value
    cell_indices[0] = spec.CELLS_PER_EXT_BLOB
    expect_exception(spec.recover_cells_and_kzg_proofs, cell_indices, partial_cells, partial_proofs)
    identifier = make_id(cell_indices, partial_cells, partial_proofs)
    yield f'recover_cells_and_kzg_proofs_case_invalid_cell_index_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(partial_cells),
            'proofs': encode_hex_list(partial_proofs),
        },
        'output': None
    }

    # Edge case: Invalid cell
    for cell in INVALID_INDIVIDUAL_CELL_BYTES:
        cells, proofs = VALID_CELLS_AND_PROOFS[6]
        cell_indices = list(range(spec.CELLS_PER_EXT_BLOB // 2))
        partial_cells = [cells[cell_index] for cell_index in cell_indices]
        partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
        # Replace first cell with an invalid value
        partial_cells[0] = cell
        expect_exception(spec.recover_cells_and_kzg_proofs, cell_indices, partial_cells, partial_proofs)
        identifier = make_id(cell_indices, partial_cells, partial_proofs)
        yield f'recover_cells_and_kzg_proofs_case_invalid_cell_{identifier}', {
            'input': {
                'cell_indices': cell_indices,
                'cells': encode_hex_list(partial_cells),
                'proofs': encode_hex_list(partial_proofs),
            },
            'output': None
        }

    # Edge case: Invalid proof
    for proof in INVALID_G1_POINTS:
        cells, proofs = VALID_CELLS_AND_PROOFS[0]
        cell_indices = list(range(spec.CELLS_PER_EXT_BLOB // 2))
        partial_cells = [cells[cell_index] for cell_index in cell_indices]
        partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
        # Replace first proof with an invalid value
        partial_proofs[0] = proof
        expect_exception(spec.recover_cells_and_kzg_proofs, cell_indices, partial_cells, partial_proofs)
        identifier = make_id(cell_indices, partial_cells, partial_proofs)
        yield f'recover_cells_and_kzg_proofs_case_invalid_proof_{identifier}', {
            'input': {
                'cell_indices': cell_indices,
                'cells': encode_hex_list(partial_cells),
                'proofs': encode_hex_list(partial_proofs),
            },
            'output': None
        }

    # Edge case: More cell_indices than cells
    cells, proofs = VALID_CELLS_AND_PROOFS[0]
    cell_indices = list(range(0, spec.CELLS_PER_EXT_BLOB, 2))
    partial_cells = [cells[cell_index] for cell_index in cell_indices]
    partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
    # Add another cell_index
    cell_indices.append(spec.CELLS_PER_EXT_BLOB - 1)
    expect_exception(spec.recover_cells_and_kzg_proofs, cell_indices, partial_cells, partial_proofs)
    identifier = make_id(cell_indices, partial_cells, partial_proofs)
    yield f'recover_cells_and_kzg_proofs_case_invalid_more_cell_indices_than_cells_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(partial_cells),
            'proofs': encode_hex_list(partial_proofs),
        },
        'output': None
    }

    # Edge case: More cells than cell_indices
    cells, proofs = VALID_CELLS_AND_PROOFS[1]
    cell_indices = list(range(0, spec.CELLS_PER_EXT_BLOB, 2))
    partial_cells = [cells[cell_index] for cell_index in cell_indices]
    partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
    # Add another cell
    partial_cells.append(CELL_RANDOM_VALID1)
    expect_exception(spec.recover_cells_and_kzg_proofs, cell_indices, partial_cells, partial_proofs)
    identifier = make_id(cell_indices, partial_cells, partial_proofs)
    yield f'recover_cells_and_kzg_proofs_case_invalid_more_cells_than_cell_indices_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(partial_cells),
            'proofs': encode_hex_list(partial_proofs),
        },
        'output': None
    }

    # Edge case: More proofs than cell_indices
    cells, proofs = VALID_CELLS_AND_PROOFS[1]
    cell_indices = list(range(0, spec.CELLS_PER_EXT_BLOB, 2))
    partial_cells = [cells[cell_index] for cell_index in cell_indices]
    partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
    # Add another proof
    partial_proofs.append(G1)
    expect_exception(spec.recover_cells_and_kzg_proofs, cell_indices, partial_cells, partial_proofs)
    identifier = make_id(cell_indices, partial_cells, partial_proofs)
    yield f'recover_cells_and_kzg_proofs_case_invalid_more_proofs_than_cell_indices_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(partial_cells),
            'proofs': encode_hex_list(partial_proofs),
        },
        'output': None
    }

    # Edge case: Duplicate cell_index
    cells, proofs = VALID_CELLS_AND_PROOFS[2]
    # There will be 65 cells, where 64 are unique and 1 is a duplicate.
    # Depending on the implementation, 63 & 1 might not fail for the right
    # reason. For example, if the implementation assigns cells in an array
    # via index, this would result in 63 cells and the test would fail due
    # to insufficient cell count, not because of a duplicate cell.
    cell_indices = list(range(spec.CELLS_PER_EXT_BLOB // 2 + 1))
    partial_cells = [cells[cell_index] for cell_index in cell_indices]
    partial_proofs = [proofs[cell_index] for cell_index in cell_indices]
    # Replace first cell_index with the second cell_index
    cell_indices[0] = cell_indices[1]
    expect_exception(spec.recover_cells_and_kzg_proofs, cell_indices, partial_cells, partial_proofs)
    identifier = make_id(cell_indices, partial_cells, partial_proofs)
    yield f'recover_cells_and_kzg_proofs_case_invalid_duplicate_cell_index_{identifier}', {
        'input': {
            'cell_indices': cell_indices,
            'cells': encode_hex_list(partial_cells),
            'proofs': encode_hex_list(partial_proofs),
        },
        'output': None
    }


###############################################################################
# Main logic
###############################################################################

def create_provider(fork_name: SpecForkName,
                    handler_name: str,
                    test_case_fn: Callable[[], Iterable[Tuple[str, Dict[str, Any]]]]) -> gen_typing.TestProvider:
    def prepare_fn() -> None:
        # Nothing to load / change in spec. Maybe in future forks.
        # Put the tests into the general config category, to not require any particular configuration.
        return

    def cases_fn() -> Iterable[gen_typing.TestCase]:
        for data in test_case_fn():
            (case_name, case_content) = data
            yield gen_typing.TestCase(
                fork_name=fork_name,
                preset_name='general',
                runner_name='kzg',
                handler_name=handler_name,
                suite_name='kzg-mainnet',
                case_name=case_name,
                case_fn=lambda: [('data', 'data', case_content)]
            )

    return gen_typing.TestProvider(prepare=prepare_fn, make_cases=cases_fn)


if __name__ == "__main__":
    bls.use_arkworks()
    gen_runner.run_generator("kzg_7594", [
        # EIP-7594
        create_provider(EIP7594, 'compute_cells_and_kzg_proofs', case_compute_cells_and_kzg_proofs),
        create_provider(EIP7594, 'verify_cell_kzg_proof', case_verify_cell_kzg_proof),
        create_provider(EIP7594, 'verify_cell_kzg_proof_batch', case_verify_cell_kzg_proof_batch),
        create_provider(EIP7594, 'recover_cells_and_kzg_proofs', case_recover_cells_and_kzg_proofs),
    ])
