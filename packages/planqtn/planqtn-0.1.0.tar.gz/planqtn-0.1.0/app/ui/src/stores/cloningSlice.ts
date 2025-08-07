import { StateCreator } from "zustand";
import { CanvasStore } from "./canvasStateStore";
import { DroppedLego } from "./droppedLegoStore";
import { DraggingStage } from "./legoDragState";
import { Connection } from "./connectionStore";
import { CanvasPoint, LogicalPoint, WindowPoint } from "../types/coordinates";

const cloneOffsetCanvas = new CanvasPoint(20, 20);

export interface CloningSlice {
  handleClone: (lego: DroppedLego, x: number, y: number) => void;
  cloneMapping: Map<string, string>; // new instance ID -> original instance ID
  clearCloneMapping: () => void;
  cloneLegos: (
    legosToClone: DroppedLego[],
    connections: Connection[]
  ) => { newLegos: DroppedLego[]; newConnections: Connection[] };
}

export const useCloningSlice: StateCreator<
  CanvasStore,
  [["zustand/immer", never]],
  [],
  CloningSlice
> = (set, get) => ({
  cloneMapping: new Map(),

  clearCloneMapping: () => {
    set((state) => {
      state.cloneMapping = new Map();
    });
  },

  cloneLegos: (legosToClone: DroppedLego[], connections: Connection[]) => {
    // Get a single starting ID for all new legos
    const startingId = parseInt(get().newInstanceId());

    const viewport = get().viewport;
    // Create a mapping from old instance IDs to new ones
    const instanceIdMap = new Map<string, string>();
    const newLegos = legosToClone.map((l, idx) => {
      const newId = String(startingId + idx);
      instanceIdMap.set(l.instance_id, newId);
      return l.with({
        instance_id: newId,
        logicalPosition: viewport.fromCanvasToLogical(
          viewport
            .fromLogicalToCanvas(l.logicalPosition)
            .plus(cloneOffsetCanvas)
        )
      });
    });

    // Store the reverse mapping (new ID -> original ID) for drag proxy use
    set((state) => {
      const cloneMapping = new Map();
      instanceIdMap.forEach((newId, originalId) => {
        cloneMapping.set(newId, originalId);
      });
      state.cloneMapping = cloneMapping;
    });

    // Clone connections between the selected legos
    const newConnections = connections
      .filter(
        (conn) =>
          legosToClone.some((l) => l.instance_id === conn.from.legoId) &&
          legosToClone.some((l) => l.instance_id === conn.to.legoId)
      )
      .map(
        (conn) =>
          new Connection(
            {
              legoId: instanceIdMap.get(conn.from.legoId)!,
              leg_index: conn.from.leg_index
            },
            {
              legoId: instanceIdMap.get(conn.to.legoId)!,
              leg_index: conn.to.leg_index
            }
          )
      );

    // Add new legos and connections
    get().addDroppedLegos(newLegos);
    get().addConnections(newConnections);

    // Add to history
    get().addOperation({
      type: "add",
      data: {
        legosToAdd: newLegos,
        connectionsToAdd: newConnections
      }
    });

    return { newLegos, newConnections };
  },

  handleClone: (clickedLego, x, y) => {
    const tensorNetwork = get().tensorNetwork;
    const connections = get().connections;
    const isSelected =
      tensorNetwork &&
      tensorNetwork?.legos.some(
        (l) => l.instance_id === clickedLego.instance_id
      );

    // Check if we're cloning multiple legos
    const legosToClone = isSelected ? tensorNetwork?.legos : [clickedLego];

    const { newLegos } = get().cloneLegos(legosToClone, connections);
    // Set up drag state for the group
    const positions: { [instance_id: string]: LogicalPoint } = {};
    newLegos.forEach((l) => {
      positions[l.instance_id] = l.logicalPosition;
    });

    if (newLegos.length > 1) {
      get().setGroupDragState({
        legoInstanceIds: newLegos.map((l) => l.instance_id),
        originalPositions: positions
      });
    }
    const viewport = get().viewport;

    get().setLegoDragState({
      draggingStage: DraggingStage.MAYBE_DRAGGING,
      draggedLegoInstanceId: newLegos[0].instance_id,
      startMouseWindowPoint: new WindowPoint(x, y).plus(cloneOffsetCanvas),
      startLegoLogicalPoint: viewport.fromCanvasToLogical(
        viewport
          .fromLogicalToCanvas(clickedLego.logicalPosition)
          .plus(cloneOffsetCanvas)
      )
    });
  }
});
