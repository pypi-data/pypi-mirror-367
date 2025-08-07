"""Symplectic parity check matrix utilities."""

from galois import GF2
import numpy as np
import scipy

from planqtn.linalg import gauss


def bring_col_to_front(h: GF2, col: int, target_col: int) -> None:
    """Move a column to a target position by swapping adjacent columns.

    Moves the specified column to the target position by performing
    adjacent column swaps. This operation modifies the matrix in-place.

    Args:
        h: Parity check matrix to modify.
        col: Index of the column to move.
        target_col: Target position for the column.
    """
    for c in range(col - 1, target_col - 1, -1):
        h[:, [c, c + 1]] = h[:, [c + 1, c]]


def _normalize_emtpy_matrices_to_zero(h: GF2) -> GF2:
    if len(h) == 0 or h.shape == (0, 0) or h.shape == (1, 0):
        h = GF2([[0]])
    return h


def tensor_product(h1: GF2, h2: GF2) -> GF2:
    """Compute the tensor product of two parity check matrices.

    Args:
        h1: First parity check matrix
        h2: Second parity check matrix

    Returns:
        The tensor product of h1 and h2 as a new parity check matrix
    """
    h1 = _normalize_emtpy_matrices_to_zero(h1)
    h2 = _normalize_emtpy_matrices_to_zero(h2)

    r1, n1 = h1.shape
    r2, n2 = h2.shape
    n1 //= 2
    n2 //= 2

    is_scalar_1 = n1 == 0
    is_scalar_2 = n2 == 0

    if is_scalar_1:
        if h1[0][0] == 0:
            return GF2([[0]])
        return h2
    if is_scalar_2:
        if h2[0][0] == 0:
            return GF2([[0]])
        return h1

    # if all the rows of h1 are zero and only has a single row, then this is a tensor of free qubits
    if len(h1) == 1 and np.all(h1[0] == 0):
        # then we'll just add n1 number of cols to h2 with zeros to each half of the matrix
        return GF2(
            np.hstack((np.zeros((r2, n1)), h2[:, :n2], np.zeros((r2, n1)), h2[:, n2:]))
        )

    # if all the rows of h2 are zero and only has a single row, then this is a tensor of free qubits
    if len(h2) == 1 and np.all(h2[0] == 0):
        # then we'll just add n2 number of cols to h1 with zeros to each half of the matrix
        return GF2(
            np.hstack((h1[:, :n1], np.zeros((r1, n2)), h1[:, n1:], np.zeros((r1, n2))))
        )

    h = GF2(
        np.hstack(
            (
                # X
                scipy.linalg.block_diag(h1[:, :n1], h2[:, :n2]),
                # Z
                scipy.linalg.block_diag(h1[:, n1:], h2[:, n2:]),
            )
        )
    )

    assert h.shape == (
        r1 + r2,
        2 * (n1 + n2),
    ), f"{h.shape} != {(r1 + r2, 2 * (n1 + n2))}"

    return h


def conjoin(h1: GF2, h2: GF2, leg1: int = 0, leg2: int = 0) -> GF2:
    """Conjoin two parity check matrices via single trace on one leg.

    Creates the tensor product of two parity check matrices and then performs
    a single trace operation between the specified legs.

    Args:
        h1: First parity check matrix.
        h2: Second parity check matrix.
        leg1: Leg from the first matrix to contract (default: 0).
        leg2: Leg from the second matrix to contract (default: 0).

    Returns:
        GF2: The conjoined parity check matrix.
    """
    h1 = _normalize_emtpy_matrices_to_zero(h1)
    h2 = _normalize_emtpy_matrices_to_zero(h2)
    n1 = h1.shape[1] // 2
    h = tensor_product(h1, h2)
    h = self_trace(h, leg1, n1 + leg2)
    return h


def self_trace(h: GF2, leg1: int = 0, leg2: int = 1) -> GF2:
    """Perform self-tracing by contracting two legs within a parity check matrix.

    Contracts two legs within the same parity check matrix, effectively performing
    a partial trace operation. This corresponds to measuring ZZ and XX operators
    on the specified legs.

    Args:
        h: Parity check matrix to trace.
        leg1: First leg to contract (default: 0).
        leg2: Second leg to contract (default: 1).

    Returns:
        GF2: New parity check matrix with contracted legs removed.
    """
    r, n = h.shape
    n //= 2

    legs = [leg1, leg2, leg1 + n, leg2 + n]

    mx: GF2 = gauss(h, col_subset=legs)

    pivot_rows = [np.flatnonzero(mx[:, leg]).tolist() for leg in legs]

    pivot_rows = [-1 if len(pivots) == 0 else pivots[0] for pivots in pivot_rows]

    kept_rows = list(range(r))

    # interpret the self trace as measuring ZZ and XX

    # measuring ZZ - if x1 and x2 are the same then we have nothing to do, ZZ commutes with
    # all generators otherwise we have to pick one of them to be the main row, the other will be
    # removed
    if pivot_rows[0] != pivot_rows[1] and pivot_rows[0] != -1 and pivot_rows[1] != -1:
        mx[pivot_rows[0]] += mx[pivot_rows[1]]
        kept_rows.remove(pivot_rows[1])
    # now, if one of the legs is all zero (pivot row is -1 for those), then we can't make the
    # two legs match with any combination of the generators, thus we'll remove the offending
    # remaining row
    elif pivot_rows[0] == -1 and pivot_rows[1] != -1:
        kept_rows.remove(pivot_rows[1])
    elif pivot_rows[0] != -1 and pivot_rows[1] == -1:
        kept_rows.remove(pivot_rows[0])

    # measuring XX - if z1 and z2 are the same then we have nothing to do, XX commutes with all
    # generators otherwise we have to pick one of them to be the main row, the other will be removed
    if pivot_rows[2] != pivot_rows[3] and pivot_rows[2] != -1 and pivot_rows[3] != -1:
        mx[pivot_rows[2]] += mx[pivot_rows[3]]
        kept_rows.remove(pivot_rows[3])

    # now, if one of the legs is all zero (pivot row is -1 for those), then we can't make the two
    # legs match with any combination of the generators, thus we'll remove the offending
    # remaining row
    elif pivot_rows[2] == -1 and pivot_rows[3] != -1:
        kept_rows.remove(pivot_rows[3])

    elif pivot_rows[2] != -1 and pivot_rows[3] == -1:
        kept_rows.remove(pivot_rows[2])

    kept_cols = np.array([col for col in range(2 * n) if col not in legs])

    if len(kept_cols) == 0:
        # we have a scalar lego, if there were no rows left, then we have 0, otherwise we
        # normalize to 1
        if len(kept_rows) == 0:
            return GF2([[0]])
        return GF2([[1]])

    if len(kept_rows) == 0:
        return GF2([GF2.Zeros(len(kept_cols))])
    mx = mx[np.array(kept_rows)][:, kept_cols]

    # print("after removals:")
    # print(mx)
    mx = gauss(mx, noswaps=True)
    kept_rows = list(range(len(mx)))
    for row_idx, row in enumerate(mx):
        if np.count_nonzero(row) == 0:
            kept_rows.remove(row_idx)
    mx = mx[np.array(kept_rows)]
    return mx
