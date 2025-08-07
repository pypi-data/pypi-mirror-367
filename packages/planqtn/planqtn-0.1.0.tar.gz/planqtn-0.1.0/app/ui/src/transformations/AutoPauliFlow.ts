import { cloneDeep } from "lodash";
import { Connection } from "../stores/connectionStore";
import { DroppedLego } from "../stores/droppedLegoStore.ts";
import { findConnectedComponent } from "../lib/TensorNetwork.ts";

/**
 * Core function that can be called directly with parameters (for tests)
 * Automatically highlights (selects rows of) legos in the network when there is only one possible option.
 * @param changedLego - The lego that was changed
 * @param droppedLegos - All dropped legos
 * @param connections - All connections
 * @param setDroppedLegos - Function to update dropped legos
 */
export function simpleAutoFlow(
  changedLego: DroppedLego,
  droppedLegos: DroppedLego[],
  connections: Connection[],
  setDroppedLegos: (legos: DroppedLego[]) => void
): void {
  if (!changedLego) {
    return;
  }

  const selectedTensorNetwork = findConnectedComponent(
    changedLego,
    droppedLegos,
    connections
  );

  let count = 0;
  let changed = true;
  let tnLegos = cloneDeep(selectedTensorNetwork.legos);
  const seenLegos = new Set<string>();
  const updatedLegosMap: Map<string, number[]> = new Map();
  let updateNeeded = false;

  // count variable shouldn't be needed, but it is a safety measure to prevent infinite loops - can remove later
  while (changed && count < 50) {
    changed = false;
    count++;

    for (const lego of tnLegos) {
      if (lego.instance_id === changedLego?.instance_id) {
        continue;
      }
      const neighborConns = connections.filter(
        (conn) =>
          conn.from.legoId === lego.instance_id ||
          conn.to.legoId === lego.instance_id
      );

      if (neighborConns.length === 0) {
        continue;
      }
      for (const neighborConn of neighborConns) {
        const neighborLego = tnLegos.find(
          (l: DroppedLego) =>
            (l.instance_id === neighborConn.from.legoId ||
              l.instance_id === neighborConn.to.legoId) &&
            l.instance_id != lego.instance_id
        );
        if (!neighborLego) {
          continue;
        }

        const neighborLegIndex =
          neighborConn.from.legoId == neighborLego.instance_id
            ? neighborConn.from.leg_index
            : neighborConn.to.leg_index;

        const legoLegIndex =
          neighborConn.from.legoId == lego.instance_id
            ? neighborConn.from.leg_index
            : neighborConn.to.leg_index;

        const legoLegHighlightOp = getHighlightOp(lego, legoLegIndex);
        const neighborLegHighlightOp = getHighlightOp(
          neighborLego,
          neighborLegIndex
        );
        const { xRowIndices, zRowIndices } = findRowIndices(lego, legoLegIndex);

        // Skip if lego and neighbor already have the same operation
        if (
          neighborLegHighlightOp[0] === legoLegHighlightOp[0] &&
          neighborLegHighlightOp[1] === legoLegHighlightOp[1]
        ) {
          seenLegos.add(lego.instance_id);
          continue;
        }
        if (!isSimpleLego(lego)) {
          continue;
        }

        let newRows: number[] | null = null;
        if (
          neighborLegHighlightOp[0] === 1 &&
          neighborLegHighlightOp[1] === 0 &&
          xRowIndices.length === 1
        ) {
          newRows = [xRowIndices[0]];
        } else if (
          neighborLegHighlightOp[0] === 0 &&
          neighborLegHighlightOp[1] === 1 &&
          zRowIndices.length === 1
        ) {
          newRows = [zRowIndices[0]];
        } else if (
          neighborLegHighlightOp[0] === 1 &&
          neighborLegHighlightOp[1] === 1 &&
          xRowIndices.length === 1 &&
          zRowIndices.length === 1
        ) {
          newRows =
            zRowIndices[0] != xRowIndices[0]
              ? [xRowIndices[0], zRowIndices[0]]
              : [xRowIndices[0]];
        } else if (
          !(legoLegHighlightOp[0] === 0 && legoLegHighlightOp[1] === 0)
        ) {
          newRows = [];
        }

        if (newRows !== null) {
          // ensure the lego has not been changed already
          if (
            !seenLegos.has(lego.instance_id) ||
            // lego can only be changed again if highlighting an unhighlighted lego
            (newRows?.length > 0 && lego.selectedMatrixRows.length === 0) ||
            // or can be changed again if neighbor of changedLego --> it has priority
            (lego.selectedMatrixRows.length > 0 &&
              neighborLego.instance_id === changedLego?.instance_id &&
              newRows?.length > 0)
          ) {
            tnLegos = updateLego(tnLegos, lego.instance_id, newRows);
            updatedLegosMap.set(lego.instance_id, newRows);
            seenLegos.add(lego.instance_id);
            changed = true;
            updateNeeded = true;
          }
        }
      }
    }
  }

  if (updateNeeded) {
    // Apply all changes at once to make sure all updates are done
    setDroppedLegos(
      droppedLegos.map((l) =>
        updatedLegosMap.has(l.instance_id)
          ? l.with({ selectedMatrixRows: updatedLegosMap.get(l.instance_id)! })
          : l
      )
    );
  }
}

/**
 * Helper method to update the given lego in the tensor network
 * @param tnLegos
 * @param targetId
 * @param newRows
 * @param setDroppedLegos
 * @returns new list of legos after the update
 */
const updateLego = (
  tnLegos: DroppedLego[],
  targetId: string,
  newRows: number[]
): DroppedLego[] => {
  const updatedLegos = tnLegos.map((l) =>
    l.instance_id === targetId ? l.with({ selectedMatrixRows: newRows }) : l
  );
  return updatedLegos;
};

/**
 * Helper method to find the current highlight operation of the given lego at leg index.
 * @param lego
 * @param leg_index
 * @returns X and Z parts of the highlight operation
 */
const getHighlightOp = (lego: DroppedLego, leg_index: number) => {
  const nLegoLegs = lego.numberOfLegs;
  const combinedRow = new Array(lego.parity_check_matrix[0].length).fill(0);

  for (const rowIndex of lego.selectedMatrixRows) {
    lego.parity_check_matrix[rowIndex].forEach((val, idx) => {
      combinedRow[idx] = (combinedRow[idx] + val) % 2;
    });
  }
  const xPart = combinedRow[leg_index];
  const zPart = combinedRow[leg_index + nLegoLegs];
  return [xPart, zPart];
};

/**
 * Helper method to find the X and Z rows in the parity check matrix that correspond to the given leg index.
 * @param lego
 * @param leg_index
 * @returns List of X and Z row indices
 */
const findRowIndices = (
  lego: DroppedLego,
  leg_index: number
): { xRowIndices: number[]; zRowIndices: number[] } => {
  const nLegoLegs = lego.numberOfLegs;
  const xRowIndices: number[] = [];
  const zRowIndices: number[] = [];

  lego.parity_check_matrix.forEach((row, idx) => {
    if (row[leg_index] === 1) xRowIndices.push(idx);
    if (row[leg_index + nLegoLegs] === 1) zRowIndices.push(idx);
  });

  return { xRowIndices, zRowIndices };
};

/**
 * Checks if the given lego is simple, i.e. if it has only one possible operation for each leg.
 * @param lego
 * @returns boolean true if the lego is simple, false otherwise
 */
const isSimpleLego = (lego: DroppedLego): boolean => {
  const nLegoLegs = lego.numberOfLegs;
  if (lego.parity_check_matrix.length < 2) {
    return true;
  }
  if (lego.parity_check_matrix.length > 2) {
    return false;
  }
  const [row1, row2] = lego.parity_check_matrix;
  const combinedRow = row1.map((val, i) => (val + row2[i]) % 2);

  const legActions: Set<string>[] = Array.from(
    { length: nLegoLegs },
    () => new Set<string>()
  );

  for (const row of [row1, row2, combinedRow]) {
    for (let i = 0; i < nLegoLegs; i++) {
      const xPart = row[i];
      const zPart = row[i + nLegoLegs];

      const key = `${xPart}${zPart}`;
      if (legActions[i].has(key)) {
        return false;
      }
      legActions[i].add(key);
    }
  }
  return true;
};
