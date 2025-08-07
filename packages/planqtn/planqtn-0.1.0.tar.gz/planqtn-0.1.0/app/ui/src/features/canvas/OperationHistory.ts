import { Connection } from "../../stores/connectionStore";
import { DroppedLego } from "../../stores/droppedLegoStore.ts";
import * as _ from "lodash";

export type OperationType =
  | "add"
  | "remove"
  | "move"
  | "connect"
  | "disconnect"
  | "fuse"
  | "unfuseToLegs"
  | "unfuseInto2Legos"
  | "colorChange"
  | "pullOutOppositeLeg"
  | "injectTwoLegged"
  | "bialgebra"
  | "inverseBialgebra"
  | "hopf"
  | "addStopper"
  | "connectGraphNodesWithCenterLego"
  | "completeGraphViaHadamards";

export type Operation = {
  type: OperationType;
  data: {
    legosToAdd?: DroppedLego[];
    legosToRemove?: DroppedLego[];
    legosToUpdate?: { oldLego: DroppedLego; newLego: DroppedLego }[];
    connectionsToAdd?: Connection[];
    connectionsToRemove?: Connection[];
  };
};

export class OperationHistory {
  redoHistory: Operation[] = [];
  constructor(private operations: Operation[]) {}

  public addOperation(operation: Operation) {
    this.operations.push(operation);
    // console.log("addOperation", "operation", operation, "operations", this.operations);
    this.redoHistory = [];
  }

  public undo(
    connections: Connection[],
    droppedLegos: DroppedLego[]
  ): { connections: Connection[]; droppedLegos: DroppedLego[] } {
    if (this.operations.length === 0) return { connections, droppedLegos };

    const lastOperation = this.operations[this.operations.length - 1];

    // console.log("undo", "lastOperation", lastOperation);
    // console.log("undo", "current legos", droppedLegos);
    // Move the operation to redo history before undoing
    this.redoHistory.push(lastOperation);
    this.operations = this.operations.slice(0, -1);

    let newConnections: Connection[] = _.cloneDeep(connections);
    let newDroppedLegos: DroppedLego[] = _.cloneDeep(droppedLegos);

    newConnections = newConnections.filter(
      (conn) =>
        !lastOperation.data?.connectionsToAdd?.some((removeMe) =>
          removeMe.equals(conn)
        )
    );
    newConnections = [
      ...newConnections,
      ...(lastOperation.data?.connectionsToRemove || [])
    ];
    // we remove the ones that were added
    newDroppedLegos = newDroppedLegos.filter(
      (lego) =>
        !lastOperation.data?.legosToAdd?.some(
          (removeMe) => removeMe.instance_id === lego.instance_id
        )
    );
    // we add the ones that were removed
    newDroppedLegos = [
      ...newDroppedLegos,
      ...(lastOperation.data?.legosToRemove || [])
    ];
    // we update the ones that were updated
    newDroppedLegos = newDroppedLegos.map((lego) => {
      const update = lastOperation.data?.legosToUpdate?.find(
        (updateMe) => updateMe.newLego.instance_id === lego.instance_id
      );
      if (update) {
        return update.oldLego;
      }
      return lego;
    });
    // console.log("undo new droppedLegos", newDroppedLegos);

    return { connections: newConnections, droppedLegos: newDroppedLegos };
  }

  public redo(
    connections: Connection[],
    droppedLegos: DroppedLego[]
  ): { connections: Connection[]; droppedLegos: DroppedLego[] } {
    if (this.redoHistory.length === 0) return { connections, droppedLegos };

    const nextOperation = this.redoHistory[this.redoHistory.length - 1];
    let newConnections: Connection[] = _.cloneDeep(connections);
    let newDroppedLegos: DroppedLego[] = _.cloneDeep(droppedLegos);
    this.operations.push(nextOperation);
    this.redoHistory = this.redoHistory.slice(0, -1);

    newConnections = newConnections.filter(
      (conn) =>
        !nextOperation.data?.connectionsToRemove?.some((removeMe) =>
          removeMe.equals(conn)
        )
    );
    newConnections = [
      ...newConnections,
      ...(nextOperation.data?.connectionsToAdd || [])
    ];
    newDroppedLegos = newDroppedLegos.filter(
      (lego) =>
        !nextOperation.data?.legosToRemove?.some(
          (removeMe) => removeMe.instance_id === lego.instance_id
        )
    );
    newDroppedLegos = [
      ...newDroppedLegos,
      ...(nextOperation.data?.legosToAdd || [])
    ];
    newDroppedLegos = newDroppedLegos.map((lego) => {
      const update = nextOperation.data?.legosToUpdate?.find(
        (updateMe) => updateMe.oldLego.instance_id === lego.instance_id
      );
      if (update) {
        return update.newLego;
      }
      return lego;
    });

    return { connections: newConnections, droppedLegos: newDroppedLegos };
  }
}
