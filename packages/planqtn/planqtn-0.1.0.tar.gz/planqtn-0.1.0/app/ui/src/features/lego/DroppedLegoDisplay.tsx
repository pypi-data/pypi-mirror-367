import { DroppedLego } from "../../stores/droppedLegoStore.ts";
import { LegPosition, LegStyle } from "./LegoStyles.ts";
import { useMemo, memo } from "react";
import { useCanvasStore } from "../../stores/canvasStateStore.ts";
import { DraggingStage } from "../../stores/legoDragState.ts";
import { Connection } from "../../stores/connectionStore";
import {
  getSmartLegoSize,
  getLevelOfDetail
} from "../../utils/coordinateTransforms.ts";
import { useShallow } from "zustand/react/shallow";
import { WindowPoint } from "../../types/coordinates.ts";
import { SVG_COLORS } from "../../lib/PauliColors.ts";
import { SvgLegoStyle } from "./SvgLegoStyle.ts";

const LEG_ENDPOINT_RADIUS = 5;

// Add shared function for leg position calculations

export function getLegoBoundingBox(
  lego: DroppedLego,
  demoMode: boolean,
  zoomLevel: number = 1
): {
  top: number;
  left: number;
  width: number;
  height: number;
} {
  // Use smart zoom size calculation
  const originalSize = lego.style!.size;
  const size = demoMode
    ? originalSize
    : getSmartLegoSize(originalSize, zoomLevel);

  const endpointFn = (pos: LegPosition) => {
    return demoMode
      ? { x: pos.endX, y: pos.endY }
      : { x: pos.labelX, y: pos.labelY };
  };

  // Calculate SVG dimensions to accommodate all legs
  const maxEndpointX = Math.max(
    ...lego.style!.legStyles.map((legStyle) => endpointFn(legStyle.position).x),
    size / 2
  );
  const minEndpointX = Math.min(
    ...lego.style!.legStyles.map((legStyle) => endpointFn(legStyle.position).x),
    0
  );

  const maxEndpointY = Math.max(
    ...lego.style!.legStyles.map((legStyle) => endpointFn(legStyle.position).y),
    +size / 2
  );
  const minEndpointY = Math.min(
    ...lego.style!.legStyles.map((legStyle) => endpointFn(legStyle.position).y),
    -size / 2
  );

  return {
    top: minEndpointY,
    left: minEndpointX,
    width: maxEndpointX - minEndpointX,
    height: maxEndpointY - minEndpointY
  };
}

// New function for calculating body bounding box specifically
export function getLegoBodyBoundingBox(
  lego: DroppedLego,
  demoMode: boolean,
  zoomLevel: number = 1
): {
  top: number;
  left: number;
  width: number;
  height: number;
} {
  // Use smart zoom size calculation
  const originalSize = lego.style!.size;
  const size = demoMode
    ? originalSize
    : getSmartLegoSize(originalSize, zoomLevel);

  // Handle regular legos (non-SVG)
  const numRegularLegs = lego.style!.legStyles.filter(
    (leg) => leg.type !== "gauge"
  ).length;

  if (numRegularLegs <= 2) {
    // Square/rectangle body
    return {
      top: -size / 2,
      left: -size / 2,
      width: size,
      height: size
    };
  } else {
    // Circular or polygonal body - all fit within a circle of radius size/2
    const diameter = size;
    return {
      top: -diameter / 2,
      left: -diameter / 2,
      width: diameter,
      height: diameter
    };
  }
}

interface DroppedLegoDisplayProps {
  legoInstanceId: string;
  demoLego?: DroppedLego;
  forceSmartSizing?: boolean;
  bodyOnly?: boolean;
}

// Memoized component for static leg lines only
const StaticLegsLayer = memo<{
  legStyles: LegStyle[];
  shouldHideLeg: boolean[];
  bodyOrder: "front" | "behind";
  scaleStart: number;
}>(({ legStyles, shouldHideLeg, bodyOrder, scaleStart }) => {
  return (
    <>
      {/* Static leg lines - rendered first, conditionally hidden */}
      {legStyles.map((legStyle, leg_index) =>
        shouldHideLeg[leg_index] || legStyle.bodyOrder !== bodyOrder ? null : (
          <line
            key={`static-leg-${leg_index}`}
            x1={legStyle.position.startX * scaleStart}
            y1={legStyle.position.startY * scaleStart}
            x2={legStyle.position.endX}
            y2={legStyle.position.endY}
            stroke={SVG_COLORS.I} // Default gray color for static rendering
            strokeWidth="2"
            strokeDasharray={
              legStyle.lineStyle === "dashed" ? "5,5" : undefined
            }
            style={{ pointerEvents: "none" }}
          />
        )
      )}
    </>
  );
});

StaticLegsLayer.displayName = "StaticLegsLayer";

const DynamicLegHighlightLayer = memo<{
  legStyles: LegStyle[];
  shouldHideLeg: boolean[];
  bodyOrder: "front" | "behind";
  scaleStart: number;
  lego: DroppedLego;
}>(({ legStyles, shouldHideLeg, bodyOrder, scaleStart, lego }) => {
  // Calculate dynamic leg colors based on current highlightedLegConstraints
  const getLegColor = (leg_index: number): string => {
    // Check if this leg has a global highlight constraint
    const globalHighlight = lego.highlightedLegConstraints.find(
      (constraint) => constraint.legIndex === leg_index
    );

    if (globalHighlight) {
      return SVG_COLORS[globalHighlight.operator];
    }

    // Check if this leg has a local highlight (from leg connection states)
    const localHighlightPauliOperator =
      lego.style!.getLegHighlightPauliOperator(leg_index);
    if (localHighlightPauliOperator !== "I") {
      return SVG_COLORS[localHighlightPauliOperator];
    }

    // Default to the static leg style color
    return legStyles[leg_index]?.color || SVG_COLORS.I;
  };

  return (
    <>
      {legStyles.map((legStyle, leg_index) => {
        const legColor = getLegColor(leg_index);
        const shouldHide = shouldHideLeg[leg_index];

        if (
          legColor === SVG_COLORS.I ||
          shouldHide ||
          legStyle.bodyOrder !== bodyOrder
        ) {
          return null;
        }

        return (
          <g key={`highlight-leg-${leg_index}`}>
            <line
              x1={legStyle.position.startX * scaleStart}
              y1={legStyle.position.startY * scaleStart}
              x2={legStyle.position.endX}
              y2={legStyle.position.endY}
              stroke={legColor}
              strokeWidth={4}
              strokeDasharray={
                legStyle.lineStyle === "dashed" ? "5,5" : undefined
              }
              style={{ pointerEvents: "none" }}
            />
          </g>
        );
      })}
    </>
  );
});

DynamicLegHighlightLayer.displayName = "DynamicLegHighlightLayer";

const LegEndpointLayer = memo<{
  lego: DroppedLego;
  legStyles: LegStyle[];
  shouldHideLeg: boolean[];
  bodyOrder: "front" | "behind";
}>(({ lego, legStyles, shouldHideLeg, bodyOrder }) => {
  const canvasRef = useCanvasStore((state) => state.canvasRef);

  const storeHandleLegMouseDown = useCanvasStore(
    (state) => state.handleLegMouseDown
  );
  const storeHandleLegClick = useCanvasStore((state) => state.handleLegClick);
  const storeHandleLegMouseUp = useCanvasStore(
    (state) => state.handleLegMouseUp
  );

  const handleLegMouseDown = (
    e: React.MouseEvent,
    legoId: string,
    leg_index: number
  ) => {
    if (!canvasRef) return;

    e.preventDefault();
    e.stopPropagation();

    storeHandleLegMouseDown(
      legoId,
      leg_index,
      WindowPoint.fromMouseEvent(e as unknown as MouseEvent)
    );
  };

  const handleLegClick = (legoId: string, leg_index: number) => {
    storeHandleLegClick(legoId, leg_index);
  };

  const handleLegMouseUp = (e: React.MouseEvent, i: number) => {
    e.stopPropagation();
    storeHandleLegMouseUp(lego.instance_id, i);
  };

  // Calculate dynamic leg colors based on current highlightedLegConstraints
  const getLegColor = (leg_index: number): string => {
    // Check if this leg has a global highlight constraint
    const globalHighlight = lego.highlightedLegConstraints.find(
      (constraint) => constraint.legIndex === leg_index
    );

    if (globalHighlight) {
      return SVG_COLORS[globalHighlight.operator];
    }

    // Check if this leg has a local highlight (from leg connection states)
    const localHighlightPauliOperator =
      lego.style!.getLegHighlightPauliOperator(leg_index);
    if (localHighlightPauliOperator !== "I") {
      return SVG_COLORS[localHighlightPauliOperator];
    }

    // Default to the static leg style color
    return legStyles[leg_index]?.color || SVG_COLORS.I;
  };

  return (
    <>
      {legStyles.map((legStyle, leg_index) => {
        const isLogical = lego.logical_legs.includes(leg_index);
        const legColor = getLegColor(leg_index);

        const shouldHide = shouldHideLeg[leg_index];

        if (shouldHide || legStyle.bodyOrder !== bodyOrder) {
          return null;
        }

        return (
          <g key={`interactive-leg-${leg_index}`}>
            {/* Logical leg interactive line - rendered on top for clicks */}
            {isLogical && (
              <line
                x1={legStyle.position.startX}
                y1={legStyle.position.startY}
                x2={legStyle.position.endX}
                y2={legStyle.position.endY}
                stroke="transparent"
                strokeWidth={5}
                className="logical-leg-interactive"
                style={{
                  cursor: "pointer",
                  pointerEvents: "visibleStroke",
                  color: legColor // Set the current color for CSS inheritance
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleLegClick(lego.instance_id, leg_index);
                }}
              />
            )}

            {/* Draggable Endpoint */}
            <circle
              cx={legStyle.position.endX}
              cy={legStyle.position.endY}
              r={LEG_ENDPOINT_RADIUS}
              className="leg-endpoint"
              fill={"white"}
              stroke={legColor}
              strokeWidth="2"
              style={{
                cursor: "pointer",
                pointerEvents: "all",
                transition: "stroke 0.2s, fill 0.2s"
              }}
              onMouseDown={(e) => {
                e.stopPropagation();
                handleLegMouseDown(e, lego.instance_id, leg_index);
              }}
              onMouseUp={(e) => {
                e.stopPropagation();
                handleLegMouseUp(e, leg_index);
              }}
            />
          </g>
        );
      })}
    </>
  );
});

LegEndpointLayer.displayName = "LegEndpointLayer";

// Memoized component for lego body
const LegoBodyLayer = memo<{
  lego: DroppedLego;
  size: number;
  numRegularLegs: number;
  isSelected: boolean;
}>(({ lego, size, numRegularLegs, isSelected }) => {
  // Calculate polygon vertices - only for regular legs
  const vertices = useMemo(() => {
    return Array.from({ length: numRegularLegs }, (_, i) => {
      // Start from the top (- Math.PI / 2) and go clockwise
      const angle = -Math.PI / 2 + (2 * Math.PI * i) / numRegularLegs;
      return {
        x: (size / 2) * Math.cos(angle),
        y: (size / 2) * Math.sin(angle)
      };
    });
  }, [numRegularLegs, size]);

  return (
    <>
      {/* Lego Body */}
      {numRegularLegs <= 2 ? (
        <g
          transform={`translate(-${size / 2}, -${size / 2})`}
          id={`lego-${lego.instance_id}-body`}
        >
          <rect
            x="0"
            y="0"
            width={size}
            height={size}
            rx={
              typeof lego.style!.borderRadius === "string" &&
              lego.style!.borderRadius === "full"
                ? size / 2
                : typeof lego.style!.borderRadius === "number"
                  ? lego.style!.borderRadius
                  : 0
            }
            ry={
              typeof lego.style!.borderRadius === "string" &&
              lego.style!.borderRadius === "full"
                ? size / 2
                : typeof lego.style!.borderRadius === "number"
                  ? lego.style!.borderRadius
                  : 0
            }
            fill={
              isSelected
                ? lego.style!.getSelectedBackgroundColorForSvg()
                : lego.style!.getBackgroundColorForSvg()
            }
            stroke={
              isSelected
                ? lego.style!.getSelectedBorderColorForSvg()
                : lego.style!.getBorderColorForSvg()
            }
            strokeWidth="2"
          />
        </g>
      ) : (
        <g>
          {numRegularLegs > 8 ? (
            // Create a circle for many vertices
            <circle
              id={`lego-${lego.instance_id}-body`}
              cx="0"
              cy="0"
              r={size / 2}
              fill={
                isSelected
                  ? lego.style!.getSelectedBackgroundColorForSvg()
                  : lego.style!.getBackgroundColorForSvg()
              }
              stroke={
                isSelected
                  ? lego.style!.getSelectedBorderColorForSvg()
                  : lego.style!.getBorderColorForSvg()
              }
              strokeWidth="2"
            />
          ) : (
            // Create a polygon for 3-8 vertices
            <path
              id={`lego-${lego.instance_id}-body`}
              d={
                vertices.reduce((path, _, i) => {
                  const command = i === 0 ? "M" : "L";
                  const x =
                    (size / 2) *
                    Math.cos(-Math.PI / 2 + (2 * Math.PI * i) / numRegularLegs);
                  const y =
                    (size / 2) *
                    Math.sin(-Math.PI / 2 + (2 * Math.PI * i) / numRegularLegs);
                  return `${path} ${command} ${x} ${y}`;
                }, "") + " Z"
              }
              fill={
                isSelected
                  ? lego.style!.getSelectedBackgroundColorForSvg()
                  : lego.style!.getBackgroundColorForSvg()
              }
              stroke={
                isSelected
                  ? lego.style!.getSelectedBorderColorForSvg()
                  : lego.style!.getBorderColorForSvg()
              }
              strokeWidth="2"
            />
          )}
        </g>
      )}
    </>
  );
});

LegoBodyLayer.displayName = "LegoBodyLayer";

// Memoized component for SVG lego body
const SvgLegoBodyLayer = memo<{
  lego: DroppedLego;
  size: number;
  originalSize: number;
  isSelected: boolean;
}>(({ lego, size, originalSize }) => {
  const svgBodyElement = (lego.style as SvgLegoStyle).getSvgBodyElement();

  return (
    <>
      {/* Custom SVG body */}
      <g
        id={`lego-${lego.instance_id}-body`}
        transform={`scale(${size / originalSize})`}
        dangerouslySetInnerHTML={{ __html: svgBodyElement }}
      />
    </>
  );
});

SvgLegoBodyLayer.displayName = "SvgLegoBodyLayer";

export const DroppedLegoDisplay: React.FC<DroppedLegoDisplayProps> = memo(
  ({ legoInstanceId, demoLego, forceSmartSizing, bodyOnly = false }) => {
    const lego =
      demoLego ||
      useCanvasStore(
        (state) =>
          state.droppedLegos.find((l) => l.instance_id === legoInstanceId)!
      );

    // Check if this lego should use SVG-based rendering for the body
    const isSvgLego = lego.isSvgLego;

    // Get zoom level for smart scaling
    const viewport = useCanvasStore((state) => state.viewport);
    const zoomLevel = viewport.zoomLevel;

    const canvasPosition = viewport.fromLogicalToCanvas(lego.logicalPosition);

    // Use smart zoom position for calculations with central coordinate system
    const basePosition = useMemo(() => {
      if (demoLego) {
        return { x: lego.logicalPosition.x, y: lego.logicalPosition.y };
      }
      return canvasPosition;
    }, [lego.logicalPosition, demoLego, canvasPosition]);

    const legConnectionStates = useCanvasStore(
      useShallow((state) =>
        lego ? state.legConnectionStates[lego.instance_id] || [] : []
      )
    );

    // Optimize store subscriptions to prevent unnecessary rerenders
    const legoConnections = useCanvasStore(
      useShallow((state) =>
        lego ? state.legoConnectionMap[lego.instance_id] || [] : []
      )
    );

    const hideConnectedLegs = useCanvasStore(
      (state) => state.hideConnectedLegs
    );

    // Only subscribe to the specific drag state properties that matter for this lego
    const isThisLegoBeingDragged = useCanvasStore((state) => {
      if (state.legoDragState.draggedLegoInstanceId === "") return false;
      const draggedLego = state.droppedLegos.find(
        (l) => l.instance_id === state.legoDragState.draggedLegoInstanceId
      );
      return (
        draggedLego?.instance_id === lego.instance_id &&
        state.legoDragState.draggingStage === DraggingStage.DRAGGING
      );
    });

    // Optimize tensor network subscription to only trigger when this lego's selection changes
    const isSelected = useCanvasStore((state) => {
      return (
        (lego &&
          state.tensorNetwork?.legos.some(
            (l) => l.instance_id === lego.instance_id
          )) ||
        false
      );
    });

    const legHiddenStates = useCanvasStore(
      useShallow((state) =>
        lego ? state.legHideStates[lego.instance_id] || [] : []
      )
    );

    const storeHandleLegoClick = useCanvasStore(
      (state) => state.handleLegoClick
    );
    const storeHandleLegoMouseDown = useCanvasStore(
      (state) => state.handleLegoMouseDown
    );

    const staticShouldHideLeg = useMemo(
      () => legHiddenStates,
      [legHiddenStates]
    );

    const hideIds = useCanvasStore((state) => state.hideIds);
    const hideTypeIds = useCanvasStore((state) => state.hideTypeIds);
    const hideDanglingLegs = useCanvasStore((state) => state.hideDanglingLegs);
    const hideLegLabels = useCanvasStore((state) => state.hideLegLabels);

    // Early return AFTER all hooks are called
    if (!lego) return null;

    // Now we can safely use lego without null checks
    const originalSize = lego.style!.size;
    const smartSize =
      demoLego && !forceSmartSizing
        ? originalSize
        : getSmartLegoSize(originalSize, zoomLevel);
    const size = smartSize;

    // Calculate level of detail based on effective size
    const lod = getLevelOfDetail(smartSize, zoomLevel);

    const numAllLegs = lego.numberOfLegs;
    const numLogicalLegs = lego.logical_legs.length;
    const numGaugeLegs = lego.gauge_legs.length;
    const numRegularLegs = numAllLegs - numLogicalLegs - numGaugeLegs;

    // Check if this specific lego is being dragged
    const isThisLegoDragged = isThisLegoBeingDragged;

    // Helper function to generate connection key (same as in ConnectionsLayer)
    const getConnectionKey = (conn: Connection) => {
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
      return `${firstId}-${firstLeg}-${secondId}-${secondLeg}`;
    };

    const isScalarLego = (lego: DroppedLego) => {
      return (
        lego.parity_check_matrix.length === 1 &&
        lego.parity_check_matrix[0].length === 1
      );
    };

    const handleLegoClick = (e: React.MouseEvent<SVGSVGElement>) => {
      storeHandleLegoClick(lego, e.ctrlKey, e.metaKey);
    };

    const handleLegoMouseDown = (e: React.MouseEvent<SVGSVGElement>) => {
      e.preventDefault();
      e.stopPropagation();
      storeHandleLegoMouseDown(
        lego.instance_id,
        e.clientX,
        e.clientY,
        e.shiftKey
      );
    };

    return (
      <>
        <g
          width={size}
          height={size}
          id={`lego-${lego.instance_id}`}
          style={{
            overflow: "visible",
            pointerEvents: demoLego ? "none" : "all",
            width: `${size}px`,
            height: `${size}px`,
            cursor: isThisLegoDragged ? "grabbing" : "grab",
            userSelect: "none",
            zIndex: 0,
            opacity: isThisLegoDragged ? 0.5 : 1,
            filter: isSelected
              ? "drop-shadow(0px 0px 10px rgba(37, 0, 245, 0.5))"
              : "none"
          }}
          className="lego-svg"
          transform={
            demoLego ? "" : `translate(${basePosition.x}, ${basePosition.y})`
          }
          onClick={handleLegoClick}
          onMouseDown={handleLegoMouseDown}
        >
          {lego.scalarValue !== null ? (
            <g>
              {lod.showText && (
                <circle
                  cx={0}
                  cy={0}
                  r={size / 4}
                  fill="#f0f0f0"
                  stroke="#333"
                  strokeWidth="2"
                />
              )}
              <text
                x={0}
                y={0}
                fontSize="14"
                fontWeight="bold"
                fill="#333"
                textAnchor="middle"
                dominantBaseline="middle"
                style={{
                  filter: "drop-shadow(1px 1px 2px rgba(0, 0, 0, 0.5))"
                }}
              >
                {lego.scalarValue}
              </text>
            </g>
          ) : (
            <>
              {/* Layer 1: Static leg lines (gray background) - with LOD */}
              {!bodyOnly && lod.showLegs && (
                <StaticLegsLayer
                  legStyles={lego.style!.legStyles}
                  shouldHideLeg={staticShouldHideLeg}
                  bodyOrder="behind"
                  scaleStart={size / originalSize}
                />
              )}

              {/* Layer 2: Dynamic leg highlights (colored lines behind lego body) - with LOD */}
              {!bodyOnly && lod.showLegs && (
                <DynamicLegHighlightLayer
                  legStyles={lego.style!.legStyles}
                  shouldHideLeg={staticShouldHideLeg}
                  bodyOrder="behind"
                  scaleStart={size / originalSize}
                  lego={lego}
                />
              )}

              {/* Layer 3: Interactive leg endpoints and logical leg interactions - with LOD */}
              {!bodyOnly && lod.showLegs && (
                <LegEndpointLayer
                  lego={lego}
                  legStyles={lego.style!.legStyles}
                  shouldHideLeg={staticShouldHideLeg}
                  bodyOrder="behind"
                />
              )}

              {/* Layer 4: Lego body */}
              {isSvgLego ? (
                <SvgLegoBodyLayer
                  lego={lego}
                  size={size}
                  originalSize={originalSize}
                  isSelected={isSelected || false}
                />
              ) : (
                <LegoBodyLayer
                  lego={lego}
                  size={size}
                  numRegularLegs={numRegularLegs}
                  isSelected={isSelected || false}
                />
              )}

              {/* Layer 1: Static leg lines (gray background) - with LOD */}
              {!bodyOnly && lod.showLegs && (
                <StaticLegsLayer
                  legStyles={lego.style!.legStyles}
                  shouldHideLeg={staticShouldHideLeg}
                  bodyOrder="front"
                  scaleStart={size / originalSize}
                />
              )}

              {/* Layer 2: Dynamic leg highlights (colored lines behind lego body) - with LOD */}
              {!bodyOnly && lod.showLegs && (
                <DynamicLegHighlightLayer
                  legStyles={lego.style!.legStyles}
                  shouldHideLeg={staticShouldHideLeg}
                  bodyOrder="front"
                  scaleStart={size / originalSize}
                  lego={lego}
                />
              )}

              {/* Layer 3: Interactive leg endpoints and logical leg interactions - with LOD */}
              {!bodyOnly && lod.showLegs && (
                <LegEndpointLayer
                  lego={lego}
                  legStyles={lego.style!.legStyles}
                  shouldHideLeg={staticShouldHideLeg}
                  bodyOrder="front"
                />
              )}

              {/* Text content - selection-aware with LOD */}
              {!demoLego && lod.showText && (
                <g>
                  {numRegularLegs <= 2 ? (
                    <g transform={`translate(-${size / 2}, -${size / 2})`}>
                      {lod.showShortName &&
                      lego.style!.displayShortName &&
                      !hideTypeIds ? (
                        <g>
                          <text
                            x={size / 2}
                            y={size / 2 - 6}
                            fontSize="12"
                            fontWeight="bold"
                            textAnchor="middle"
                            dominantBaseline="middle"
                            fill={isSelected ? "white" : "#000000"}
                          >
                            {lego.short_name}
                          </text>
                          <text
                            x={size / 2}
                            y={size / 2 + 6}
                            fontSize="12"
                            textAnchor="middle"
                            dominantBaseline="middle"
                            fill={isSelected ? "white" : "#000000"}
                          >
                            {lego.instance_id}
                          </text>
                        </g>
                      ) : !hideIds ? (
                        <text
                          x={size / 2}
                          y={size / 2}
                          fontSize="12"
                          fontWeight="bold"
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fill={isSelected ? "white" : "#000000"}
                        >
                          {lego.instance_id}
                        </text>
                      ) : null}
                    </g>
                  ) : (
                    <text
                      x="0"
                      y={lego.logical_legs.length > 0 ? 5 : 0}
                      fontSize="10"
                      fontWeight="bold"
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fill={isSelected ? "white" : "#000000"}
                      style={{ pointerEvents: "none" }}
                    >
                      {lod.showShortName &&
                      lego.style!.displayShortName &&
                      !hideTypeIds ? (
                        <>
                          {lego.short_name}
                          {!hideIds && (
                            <tspan x="0" dy="12">
                              {lego.instance_id}
                            </tspan>
                          )}
                        </>
                      ) : !hideIds ? (
                        lego.instance_id
                      ) : null}
                    </text>
                  )}
                </g>
              )}

              {/* Leg Labels - dynamic visibility with LOD */}
              {!bodyOnly &&
                !isScalarLego(lego) &&
                !demoLego &&
                lod.showLegLabels &&
                lego.style!.legStyles.map((legStyle, leg_index) => {
                  // If the leg is hidden, don't render the label
                  if (legHiddenStates[leg_index]) return null;

                  // Check if leg is connected using pre-calculated states
                  const isLegConnectedToSomething =
                    legConnectionStates[leg_index] || false;

                  // If hideDanglingLegs is true and leg is not connected, skip rendering
                  if (
                    (hideDanglingLegs && !isLegConnectedToSomething) ||
                    hideLegLabels
                  )
                    return null;

                  // If leg is not connected, always show the label (unless hiding dangling legs)
                  if (!isLegConnectedToSomething) {
                    return (
                      <text
                        key={`${lego.instance_id}-label-${leg_index}`}
                        x={legStyle.position.labelX}
                        y={legStyle.position.labelY}
                        fontSize="12"
                        fill="#666666"
                        textAnchor="middle"
                        dominantBaseline="middle"
                        style={{ pointerEvents: "none" }}
                      >
                        {leg_index}
                      </text>
                    );
                  }

                  // Find the connected leg's style
                  const connection = legoConnections.find(
                    (c) =>
                      (c.from.legoId === lego.instance_id &&
                        c.from.leg_index === leg_index) ||
                      (c.to.legoId === lego.instance_id &&
                        c.to.leg_index === leg_index)
                  );

                  if (!connection) return null;

                  // Use the new connection highlight states from the store
                  const connectionKey = getConnectionKey(connection);
                  const colorsMatch = useCanvasStore
                    .getState()
                    .getConnectionHighlightState(connectionKey);

                  // Hide label if conditions are met
                  const shouldHideLabel =
                    hideConnectedLegs && !lego.alwaysShowLegs && colorsMatch;

                  if (shouldHideLabel) return null;

                  return (
                    <text
                      key={`${lego.instance_id}-label-${leg_index}`}
                      x={legStyle.position.labelX}
                      y={legStyle.position.labelY}
                      fontSize="12"
                      fill="#666666"
                      textAnchor="middle"
                      dominantBaseline="middle"
                      style={{ pointerEvents: "none" }}
                    >
                      {leg_index}
                    </text>
                  );
                })}
            </>
          )}
        </g>
      </>
    );
  }
);

DroppedLegoDisplay.displayName = "DroppedLegoDisplay";
export default DroppedLegoDisplay;
