import { Connection } from "../stores/connectionStore";
import { Operation } from "../features/canvas/OperationHistory.ts";
import { DroppedLego } from "../stores/droppedLegoStore.ts";

export class InjectTwoLegged {
  static operationCode = "injectTwoLegged";

  constructor(
    private connections: Connection[],
    private droppedLegos: DroppedLego[]
  ) {}

  public async apply(
    lego: DroppedLego,
    connection: Connection,
    oldLego: DroppedLego | undefined = undefined
  ): Promise<{
    connections: Connection[];
    droppedLegos: DroppedLego[];
    operation: Operation;
  }> {
    const isExistingLego = oldLego ? true : false;

    // Create new connections
    const newConnections = [
      new Connection(connection.from, {
        legoId: lego.instance_id,
        leg_index: 0
      }),
      new Connection({ legoId: lego.instance_id, leg_index: 1 }, connection.to)
    ];

    const externalConnections = this.connections.filter(
      (conn) => !connection.equals(conn)
    );

    // Add the new connections
    const finalConnections = [...externalConnections, ...newConnections];
    const legosToUpdate: { oldLego: DroppedLego; newLego: DroppedLego }[] = [];
    // Handle the lego
    let updatedLegos: DroppedLego[];
    let legosToAdd: DroppedLego[] = [];
    if (isExistingLego) {
      // Update the position of the existing lego
      legosToAdd = [];
      updatedLegos = this.droppedLegos.map((l) => {
        if (l.instance_id === lego.instance_id) {
          legosToUpdate.push({
            oldLego: oldLego!,
            newLego: lego
          });
          return lego;
        }
        return l;
      });
    } else {
      legosToAdd = [lego];
      // Add the new lego
      updatedLegos = [...this.droppedLegos, lego];
    }

    return {
      connections: finalConnections,
      droppedLegos: updatedLegos,
      operation: {
        type: "injectTwoLegged",
        data: {
          connectionsToAdd: newConnections,
          connectionsToRemove: [connection],
          legosToUpdate: legosToUpdate,
          legosToAdd: legosToAdd
        }
      }
    };
  }
}
