import React, { useMemo } from "react";
import { Connection } from "../../stores/connectionStore";
import { DroppedLego } from "../../stores/droppedLegoStore";
import { LegStyle } from "./LegoStyles";
import { useCanvasStore } from "../../stores/canvasStateStore";
import {
  getZoomAwareStrokeWidth,
  getSmartLegoSize,
  getLevelOfDetail
} from "../../utils/coordinateTransforms";
import { CanvasPoint, LogicalPoint } from "../../types/coordinates";
import { useVisibleLegoIds } from "../../hooks/useVisibleLegos";
import { DraggingStage } from "../../stores/legoDragState";

export const ConnectionsLayer: React.FC<{ bodyOrder: "front" | "behind" }> = ({
  bodyOrder
}) => {
  const connections = useCanvasStore((state) => state.connections);
  const hideConnectedLegs = useCanvasStore((state) => state.hideConnectedLegs);
  const addOperation = useCanvasStore((state) => state.addOperation);
  const removeConnections = useCanvasStore((state) => state.removeConnections);
  const connectedLegos = useCanvasStore((state) => state.connectedLegos);
  const legDragState = useCanvasStore((state) => state.legDragState);
  const setHoveredConnection = useCanvasStore(
    (state) => state.setHoveredConnection
  );
  const visibleLegoIds = useVisibleLegoIds();
  const isDraggedLego = useCanvasStore((state) => state.isDraggedLego);
  const legoDragState = useCanvasStore((state) => state.legoDragState);
  const groupDragState = useCanvasStore((state) => state.groupDragState);
  const resizeProxyLegos = useCanvasStore((state) => state.resizeProxyLegos);

  // Get zoom level for smart scaling
  const viewport = useCanvasStore((state) => state.viewport);
  const zoomLevel = viewport.zoomLevel;

  const handleConnectionDoubleClick = (
    e: React.MouseEvent,
    connection: Connection
  ) => {
    e.preventDefault();
    e.stopPropagation();

    // Add to history before removing
    addOperation({
      type: "disconnect",
      data: { connectionsToRemove: [connection] }
    });

    // Remove the connection and update URL state with the new connections
    removeConnections([connection]);
  };

  // Memoize lego lookup map for performance
  const legoMap = useMemo(() => {
    const map = new Map<string, DroppedLego>();
    connectedLegos.forEach((lego) => map.set(lego.instance_id, lego));
    return map;
  }, [connectedLegos]);

  // Pre-compute connected legs map for O(1) lookup instead of O(n) per connection
  const connectedLegsMap = useMemo(() => {
    const map = new Map<string, boolean>();
    connections.forEach((conn) => {
      map.set(`${conn.from.legoId}-${conn.from.leg_index}`, true);
      map.set(`${conn.to.legoId}-${conn.to.leg_index}`, true);
    });
    return map;
  }, [connections]);

  // Pre-compute leg styles to avoid repeated calculations
  const legStylesMap = useMemo(() => {
    const map = new Map<
      string,
      { style: LegStyle; color: string; isHighlighted: boolean }
    >();
    connectedLegos.forEach((lego) => {
      const numLegs = lego.numberOfLegs;
      for (let i = 0; i < numLegs; i++) {
        const legStyle = lego.style!.legStyles[i];
        const legColor = lego.style!.getLegColor(i);
        map.set(`${lego.instance_id}-${i}`, {
          style: legStyle,
          color: legColor,
          isHighlighted: legStyle.is_highlighted
        });
      }
    });
    return map;
  }, [connectedLegos]);

  // Memoize rendered connections with optimized calculations
  const renderedConnections = useMemo(() => {
    return connections.map((conn) => {
      const fromLego = legoMap.get(conn.from.legoId);
      const toLego = legoMap.get(conn.to.legoId);
      if (!fromLego || !toLego) return null;
      if (
        !visibleLegoIds.includes(conn.from.legoId) ||
        !visibleLegoIds.includes(conn.to.legoId)
      )
        return null;

      if (isDraggedLego(conn.from.legoId) || isDraggedLego(conn.to.legoId))
        return null;

      // Don't display connections if they belong to legos that are being resized
      if (resizeProxyLegos && resizeProxyLegos.length > 0) {
        const resizeLegoIds = resizeProxyLegos.map((lego) => lego.instance_id);
        if (
          resizeLegoIds.includes(conn.from.legoId) ||
          resizeLegoIds.includes(conn.to.legoId)
        ) {
          return null;
        }
      }

      // Create a stable key based on the connection's properties
      const [firstId, firstLeg, secondId, secondLeg] =
        conn.from.legoId < conn.to.legoId
          ? [
              conn.from.legoId,
              conn.from.leg_index,
              conn.to.legoId,
              conn.to.leg_index
            ]
          : [
              conn.to.legoId,
              conn.to.leg_index,
              conn.from.legoId,
              conn.from.leg_index
            ];
      const connKey = `${firstId}-${firstLeg}-${secondId}-${secondLeg}`;

      const fromLegStyle = fromLego.style!.legStyles[conn.from.leg_index];
      const toLegStyle = toLego.style!.legStyles[conn.to.leg_index];

      const fromPos = fromLegStyle.position;
      const toPos = toLegStyle.position;

      const connectionBodyOrder =
        fromLegStyle.bodyOrder == "front" || toLegStyle.bodyOrder == "front"
          ? "front"
          : "behind";

      if (connectionBodyOrder != bodyOrder) return null;

      // Use pre-computed maps for O(1) lookup
      const fromLegConnected = connectedLegsMap.has(
        `${fromLego.instance_id}-${conn.from.leg_index}`
      );
      const toLegConnected = connectedLegsMap.has(
        `${toLego.instance_id}-${conn.to.leg_index}`
      );

      // Get pre-computed leg styles
      const fromLegData = legStylesMap.get(
        `${fromLego.instance_id}-${conn.from.leg_index}`
      );
      const toLegData = legStylesMap.get(
        `${toLego.instance_id}-${conn.to.leg_index}`
      );

      if (!fromLegData || !toLegData) return null;

      const { color: fromLegColor, isHighlighted: fromLegHighlighted } =
        fromLegData;
      const { isHighlighted: toLegHighlighted } = toLegData;

      const fromOriginalSize = fromLego.style!.size;
      const fromSmartSize = getSmartLegoSize(fromOriginalSize, zoomLevel);
      const fromLod = getLevelOfDetail(fromSmartSize, zoomLevel);
      const toOriginalSize = toLego.style!.size;
      const toSmartSize = getSmartLegoSize(toOriginalSize, zoomLevel);
      const toLod = getLevelOfDetail(toSmartSize, zoomLevel);

      const fromShowLegs = fromLod.showLegs;
      const toShowLegs = toLod.showLegs;

      // Use the new connection highlight states from the store
      const colorsMatch = useCanvasStore
        .getState()
        .getConnectionHighlightState(connKey);

      // Determine if legs should be hidden
      const hideFromLeg =
        !fromShowLegs ||
        (hideConnectedLegs &&
          fromLegConnected &&
          !fromLego.alwaysShowLegs &&
          (!fromLegHighlighted ? !toLegHighlighted : colorsMatch));

      const hideToLeg =
        !toShowLegs ||
        (hideConnectedLegs &&
          toLegConnected &&
          !toLego.alwaysShowLegs &&
          (!toLegHighlighted ? !fromLegHighlighted : colorsMatch));

      // Apply zoom transformations to connection points using new coordinate system
      const fromPoint = viewport
        .fromLogicalToCanvas(
          new LogicalPoint(
            fromLego.logicalPosition.x,
            fromLego.logicalPosition.y
          )
        )
        .plus(
          hideFromLeg
            ? new CanvasPoint(fromPos.startX, fromPos.startY).factor(
                fromSmartSize / fromOriginalSize
              )
            : new CanvasPoint(fromPos.endX, fromPos.endY)
        );

      const toPoint = viewport
        .fromLogicalToCanvas(
          new LogicalPoint(toLego.logicalPosition.x, toLego.logicalPosition.y)
        )
        .plus(
          hideToLeg
            ? new CanvasPoint(toPos.startX, toPos.startY).factor(
                toSmartSize / toOriginalSize
              )
            : new CanvasPoint(toPos.endX, toPos.endY)
        );
      // Calculate control points for the curve - scale with zoom for better topology
      const baseControlPointDistance = 25;
      const controlPointDistance =
        baseControlPointDistance * Math.min(1, zoomLevel * 0.8 + 0.2); // Scale control points
      const cp1 = {
        x: fromPoint.x + Math.cos(fromPos.angle) * controlPointDistance,
        y: fromPoint.y + Math.sin(fromPos.angle) * controlPointDistance
      };
      const cp2 = {
        x: toPoint.x + Math.cos(toPos.angle) * controlPointDistance,
        y: toPoint.y + Math.sin(toPos.angle) * controlPointDistance
      };

      const pathString = `M ${fromPoint.x} ${fromPoint.y} C ${cp1.x} ${cp1.y}, ${cp2.x} ${cp2.y}, ${toPoint.x} ${toPoint.y}`;

      // Calculate midpoint for warning icon
      const midPoint = {
        x: (fromPoint.x + toPoint.x) / 2,
        y: (fromPoint.y + toPoint.y) / 2
      };

      const sharedColor = colorsMatch ? fromLegColor : "yellow";
      const connectorColor = colorsMatch ? sharedColor : "yellow";

      return (
        <g key={connKey}>
          {/* Invisible wider path for easier clicking */}
          <path
            d={pathString}
            stroke="transparent"
            strokeWidth="10"
            fill="none"
            style={{
              cursor: "pointer"
            }}
            onDoubleClick={(e) => handleConnectionDoubleClick(e, conn)}
            onMouseEnter={(e) => {
              // Find and update the visible path
              const visiblePath = e.currentTarget.nextSibling as SVGPathElement;
              if (visiblePath) {
                visiblePath.style.stroke = connectorColor;
                visiblePath.style.strokeWidth = "3";
                visiblePath.style.filter =
                  "drop-shadow(0 0 2px rgba(66, 153, 225, 0.5))";
                setHoveredConnection(conn);
              }
            }}
            onMouseLeave={(e) => {
              // Reset the visible path
              const visiblePath = e.currentTarget.nextSibling as SVGPathElement;
              if (visiblePath) {
                visiblePath.style.stroke = connectorColor;
                visiblePath.style.strokeWidth = "2";
                visiblePath.style.filter = "none";
                setHoveredConnection(null);
              }
            }}
          />
          {/* Visible path */}
          <path
            d={pathString}
            stroke={connectorColor}
            fill="none"
            style={{
              pointerEvents: "none",
              stroke: connectorColor
            }}
          />
          {/* Warning sign if operators don't match */}
          {!colorsMatch && fromLod.showText && toLod.showText && (
            <text
              x={midPoint.x}
              y={midPoint.y}
              fontSize="16"
              fill="#FF0000"
              textAnchor="middle"
              dominantBaseline="middle"
              style={{ pointerEvents: "none" }}
            >
              ⚠
            </text>
          )}
        </g>
      );
    });
  }, [
    connections,
    legoMap,
    connectedLegsMap,
    visibleLegoIds,
    legStylesMap,
    hideConnectedLegs,
    zoomLevel,
    viewport,
    legoDragState.draggingStage === DraggingStage.DRAGGING,
    groupDragState,
    resizeProxyLegos
  ]);

  // Memoize temporary drag line
  const tempDragLine = useMemo(() => {
    if (!legDragState?.isDragging) return null;

    const fromLego = legoMap.get(legDragState.legoId);
    if (!fromLego) return null;

    // Calculate position using shared function with smart scaling
    const fromPos = fromLego.style!.legStyles[legDragState.leg_index].position;
    // Calculate scale factor for smart sizing
    const fromBasePoint = new LogicalPoint(
      fromLego.logicalPosition.x,
      fromLego.logicalPosition.y
    );

    // Apply zoom transformations to drag line using new coordinate system
    const fromPoint = viewport
      .fromLogicalToCanvas(fromBasePoint)
      .plus(new CanvasPoint(fromPos.endX, fromPos.endY));

    const dragEndPoint = viewport.fromWindowToCanvas(
      legDragState.currentMouseWindowPoint
    );

    const legStyle = fromLego.style!.legStyles[legDragState.leg_index];
    const baseControlPointDistance = 30;
    const controlPointDistance =
      baseControlPointDistance * Math.min(1, zoomLevel * 0.8 + 0.2);
    const cp1 = {
      x: fromPoint.x + Math.cos(legStyle.angle) * controlPointDistance,
      y: fromPoint.y + Math.sin(legStyle.angle) * controlPointDistance
    };
    const cp2 = {
      x: dragEndPoint.x,
      y: dragEndPoint.y
    };

    const pathString = `M ${fromPoint.x} ${fromPoint.y} C ${cp1.x} ${cp1.y}, ${cp2.x} ${cp2.y}, ${dragEndPoint.x} ${dragEndPoint.y}`;

    // Scale stroke width for drag line too using central system
    const dragStrokeWidth = getZoomAwareStrokeWidth(2, zoomLevel);

    return (
      <g key="temp-drag-line">
        <path
          d={pathString}
          stroke="#3182CE"
          strokeWidth={dragStrokeWidth}
          strokeDasharray="4"
          fill="none"
          opacity={0.5}
          style={{ pointerEvents: "none" }}
        />
      </g>
    );
  }, [legDragState, legoMap, zoomLevel, viewport]);

  return (
    <>
      {/* Existing connections */}
      <g style={{ pointerEvents: "all" }}>{renderedConnections}</g>

      {/* Temporary line while dragging */}
      {tempDragLine}
    </>
  );
};

ConnectionsLayer.displayName = "ConnectionsLayer";
