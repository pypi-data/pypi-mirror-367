import React, { useCallback, forwardRef, useImperativeHandle } from "react";
import { Box } from "@chakra-ui/react";
import { DroppedLego } from "../../stores/droppedLegoStore.ts";
import { TensorNetwork } from "../../lib/TensorNetwork.ts";
import { useCanvasStore } from "../../stores/canvasStateStore.ts";
import { CanvasPoint } from "../../types/coordinates.ts";

export interface SelectionManagerRef {
  handleMouseDown: (e: MouseEvent) => void;
}

export const SelectionManager = forwardRef<SelectionManagerRef>((_, ref) => {
  const {
    tensorNetwork,
    setTensorNetwork,
    droppedLegos,
    connections,
    selectionBox,
    setSelectionBox,
    canvasRef
  } = useCanvasStore();

  const viewport = useCanvasStore((state) => state.viewport);

  // Helper function to handle selection box logic
  const handleSelectionBoxUpdate = useCallback(
    (
      left: number,
      right: number,
      top: number,
      bottom: number,
      e: React.MouseEvent,
      isFinalized: boolean = false
    ) => {
      // Convert HTML selection box coordinates to canvas coordinates for lego comparison
      const logicalSelectionBoxTopLeft = viewport.fromCanvasToLogical(
        new CanvasPoint(left, top)
      );
      const logicalSelectionBoxBottomRight = viewport.fromCanvasToLogical(
        new CanvasPoint(right, bottom)
      );

      // Find Legos within the selection box (in canvas coordinates)
      const selectedLegos = droppedLegos.filter((lego: DroppedLego) => {
        return (
          lego.logicalPosition.x >= logicalSelectionBoxTopLeft.x &&
          lego.logicalPosition.x <= logicalSelectionBoxBottomRight.x &&
          lego.logicalPosition.y >= logicalSelectionBoxTopLeft.y &&
          lego.logicalPosition.y <= logicalSelectionBoxBottomRight.y
        );
      });

      // Only update tensorNetwork when selection is finalized (mouseup)
      if (!isFinalized) {
        return; // Don't update tensorNetwork during dragging
      }

      // Update selection state based on the selected Legos
      if (selectedLegos.length === 1) {
        if (e.ctrlKey || e.metaKey) {
          // If Ctrl is pressed, add to existing selection
          if (tensorNetwork) {
            const newLegos = [...tensorNetwork.legos, ...selectedLegos];
            const newConnections = connections.filter(
              (conn) =>
                newLegos.some((l) => l.instance_id === conn.from.legoId) &&
                newLegos.some((l) => l.instance_id === conn.to.legoId)
            );
            const newNetwork = new TensorNetwork({
              legos: newLegos,
              connections: newConnections
            });
            setTensorNetwork(newNetwork);
          } else {
            const newNetwork = new TensorNetwork({
              legos: selectedLegos,
              connections: []
            });
            setTensorNetwork(newNetwork);
          }
        } else {
          setTensorNetwork(
            new TensorNetwork({ legos: selectedLegos, connections: [] })
          );
        }
      } else if (selectedLegos.length > 1) {
        if (e.ctrlKey || e.metaKey) {
          // If Ctrl is pressed, add to existing selection
          if (tensorNetwork) {
            const newLegos = [...tensorNetwork.legos, ...selectedLegos];
            const newConnections = connections.filter(
              (conn) =>
                newLegos.some((l) => l.instance_id === conn.from.legoId) &&
                newLegos.some((l) => l.instance_id === conn.to.legoId)
            );
            const newNetwork = new TensorNetwork({
              legos: newLegos,
              connections: newConnections
            });
            setTensorNetwork(newNetwork);
          } else {
            const selectedLegoIds = new Set(
              selectedLegos.map((lego: DroppedLego) => lego.instance_id)
            );
            const internalConnections = connections.filter(
              (conn) =>
                selectedLegoIds.has(conn.from.legoId) &&
                selectedLegoIds.has(conn.to.legoId)
            );
            const newNetwork = new TensorNetwork({
              legos: selectedLegos,
              connections: internalConnections
            });
            setTensorNetwork(newNetwork);
          }
        } else {
          // Create a tensor network from the selected legos
          const selectedLegoIds = new Set(
            selectedLegos.map((lego: DroppedLego) => lego.instance_id)
          );
          const internalConnections = connections.filter(
            (conn) =>
              selectedLegoIds.has(conn.from.legoId) &&
              selectedLegoIds.has(conn.to.legoId)
          );
          const newNetwork = new TensorNetwork({
            legos: selectedLegos,
            connections: internalConnections
          });
          setTensorNetwork(newNetwork);
        }
      } else {
        if (!(e.ctrlKey || e.metaKey)) {
          if (tensorNetwork) {
            setTensorNetwork(null);
          }
        }
      }
    },
    [droppedLegos, connections, tensorNetwork, setTensorNetwork, viewport]
  );

  // Mouse event handlers
  const handleMouseDown = useCallback(
    (e: MouseEvent) => {
      const rect = canvasRef?.current?.getBoundingClientRect();
      if (!rect) return;

      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      setSelectionBox({
        isSelecting: true,
        startX: x,
        startY: y,
        currentX: x,
        currentY: y,
        justFinished: false
      });
    },
    [canvasRef, setSelectionBox]
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!selectionBox.isSelecting) return;

      const rect = canvasRef?.current?.getBoundingClientRect();
      if (!rect) return;

      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      setSelectionBox({
        ...selectionBox,
        currentX: x,
        currentY: y
      });
    },
    [selectionBox, canvasRef, setSelectionBox]
  );

  const handleMouseUp = useCallback(
    (e: React.MouseEvent) => {
      if (!selectionBox.isSelecting) return;

      const left = Math.min(selectionBox.startX, selectionBox.currentX);
      const right = Math.max(selectionBox.startX, selectionBox.currentX);
      const top = Math.min(selectionBox.startY, selectionBox.currentY);
      const bottom = Math.max(selectionBox.startY, selectionBox.currentY);

      // Finalize the selection
      handleSelectionBoxUpdate(left, right, top, bottom, e, true);

      setSelectionBox({
        ...selectionBox,
        isSelecting: false,
        justFinished: true
      });
    },
    [selectionBox, handleSelectionBoxUpdate, setSelectionBox]
  );

  // Expose handleMouseDown to parent via ref
  useImperativeHandle(
    ref,
    () => ({
      handleMouseDown
    }),
    [handleMouseDown]
  );

  // Clear justFinished flag after render
  React.useEffect(() => {
    if (selectionBox.justFinished) {
      const timeout = setTimeout(() => {
        setSelectionBox({ ...selectionBox, justFinished: false });
      }, 0);
      return () => clearTimeout(timeout);
    }
  }, [selectionBox, setSelectionBox]);

  return (
    <>
      {/* Selection Box Visual */}
      {selectionBox.isSelecting && (
        <Box
          position="absolute"
          left={`${Math.min(selectionBox.startX, selectionBox.currentX)}px`}
          top={`${Math.min(selectionBox.startY, selectionBox.currentY)}px`}
          width={`${Math.abs(selectionBox.currentX - selectionBox.startX)}px`}
          height={`${Math.abs(selectionBox.currentY - selectionBox.startY)}px`}
          border="2px"
          borderColor="blue.500"
          bg="blue.50"
          opacity={0.3}
          pointerEvents="none"
        />
      )}

      {/* Invisible overlay to capture mouse events during selection */}
      {selectionBox.isSelecting && (
        <Box
          position="absolute"
          top={0}
          left={0}
          width="100%"
          height="100%"
          pointerEvents="all"
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          style={{ zIndex: 1000 }}
        />
      )}
    </>
  );
});

SelectionManager.displayName = "SelectionManager";
