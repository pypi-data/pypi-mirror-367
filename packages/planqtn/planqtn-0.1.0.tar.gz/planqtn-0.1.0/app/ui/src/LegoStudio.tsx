import {
  Box,
  Editable,
  EditableInput,
  EditablePreview,
  Icon,
  useColorModeValue,
  useToast,
  VStack
} from "@chakra-ui/react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger
} from "@/components/ui/tooltip";
import { useCallback, useEffect, useRef, useState } from "react";
import { Panel, PanelGroup } from "react-resizable-panels";

import ErrorPanel from "./components/ErrorPanel";
import FloatingPanelHandler from "./components/FloatingPanelHandler";
import { KeyboardHandler } from "./features/canvas/KeyboardHandler.tsx";
import { ConnectionsLayer } from "./features/lego/ConnectionsLayer.tsx";
import { LegosLayer } from "./features/lego/LegosLayer.tsx";
import {
  SelectionManager,
  SelectionManagerRef
} from "./features/canvas/SelectionManager.tsx";

import { randomPlankterName } from "./lib/RandomPlankterNames";
import { UserMenu } from "./features/auth/UserMenu.tsx";

import { userContextSupabase } from "./config/supabaseClient.ts";
import { useCanvasStore } from "./stores/canvasStateStore";
import { useUserStore } from "./stores/userStore";

import { checkSupabaseStatus } from "./lib/errors.ts";

import { ModalRoot } from "./components/ModalRoot";
import { DragProxy } from "./features/lego/DragProxy.tsx";
import { CanvasMouseHandler } from "./features/canvas/CanvasMouseHandler.tsx";
import { useCanvasDragStateStore } from "./stores/canvasDragStateStore.ts";
import { CanvasMiniMap } from "./features/canvas/CanvasMiniMap";
import { ViewportDebugOverlay } from "./features/canvas/ViewportDebugOverlay.tsx";
import { CanvasMenu } from "./features/canvas/CanvasMenu.tsx";
import { FloatingPanelsToolbar } from "./features/canvas/FloatingPanelsToolbar.tsx";
import { FiShare2, FiFileText } from "react-icons/fi";
import { QuestionIcon } from "@chakra-ui/icons";
import { SubnetToolbarOverlay } from "./features/lego/SubnetToolbarOverlay";
import { FocusBoundingBox } from "./features/canvas/FocusBoundingBox";

const LegoStudioView: React.FC = () => {
  const [currentTitle, setCurrentTitle] = useState<string>("");
  const [fatalError, setFatalError] = useState<Error | null>(null);
  const [canvasSvgRef, setCanvasSvgRef] = useState<SVGSVGElement | null>(null);

  const [altKeyPressed, setAltKeyPressed] = useState(false);
  // const [message, setMessage] = useState<string>("Loading...");

  // Cleanup function to remove old canvas states
  const cleanupOldCanvasStates = useCallback(async () => {
    const oneMonthAgo = Date.now() - 30 * 24 * 60 * 60 * 1000; // 30 days in milliseconds

    try {
      // Find all canvas state keys
      const keysToCheck = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith("canvas-state-")) {
          keysToCheck.push(key);
        }
      }

      // Check each key and remove if older than a month
      for (const key of keysToCheck) {
        try {
          const stored = localStorage.getItem(key);
          if (stored) {
            const parsed = JSON.parse(stored);

            // Check if it has a timestamp and if it's old
            if (parsed.state && parsed.state._timestamp) {
              if (parsed.state._timestamp < oneMonthAgo) {
                localStorage.removeItem(key);
                console.log(`Removed old canvas state: ${key}`);
              }
            } else {
              // Remove states without timestamp (old format)
              localStorage.removeItem(key);
              console.log(`Removed canvas state without timestamp: ${key}`);
            }
          }
        } catch {
          // If we can't parse the stored data, remove it
          localStorage.removeItem(key);
          console.log(`Removed corrupted canvas state: ${key}`);
        }
      }
    } catch (error) {
      console.error("Error during canvas state cleanup:", error);
    }
  }, []);

  const decodeCanvasState = useCanvasStore((state) => state.decodeCanvasState);

  const handleDynamicLegoDrop = useCanvasStore(
    (state) => state.handleDynamicLegoDrop
  );

  const setError = useCanvasStore((state) => state.setError);
  const title = useCanvasStore((state) => state.title);
  const setTitle = useCanvasStore((state) => state.setTitle);

  const setCanvasRef = useCanvasStore((state) => state.setCanvasRef);
  const canvasRef = useCanvasStore((state) => state.canvasRef);

  const selectionManagerRef = useRef<SelectionManagerRef>(null);

  const { canvasDragState } = useCanvasDragStateStore();
  const viewport = useCanvasStore((state) => state.viewport);
  const zoomLevel = viewport.zoomLevel;

  // Use centralized TensorNetwork store

  // Use modal store for network dialogs
  const openLoadingModal = useCanvasStore((state) => state.openLoadingModal);
  const closeLoadingModal = useCanvasStore((state) => state.closeLoadingModal);
  const openAuthDialog = useCanvasStore((state) => state.openAuthDialog);
  const openShareDialog = useCanvasStore((state) => state.openShareDialog);
  const openHelpDialog = useCanvasStore((state) => state.openHelpDialog);

  const panelGroupContainerRef = useRef<HTMLDivElement>(null);

  const { currentUser, setCurrentUser } = useUserStore();

  const supabaseStatusRef = useRef<{ isHealthy: boolean; message: string }>({
    isHealthy: false,
    message: ""
  });

  // Inside the App component, add this line near the other hooks
  const toast = useToast();

  // Initialize title from store or set a default
  useEffect(() => {
    if (!title) {
      // Generate a new random title if none exists in store
      const newTitle = `PlanqTN - ${randomPlankterName()}`;
      setTitle(newTitle);
      document.title = newTitle;
      setCurrentTitle(newTitle);
    } else {
      document.title = title;
      setCurrentTitle(title);
    }
  }, [title, setTitle]);

  // Cleanup old canvas states on component mount
  useEffect(() => {
    cleanupOldCanvasStates();
  }, [cleanupOldCanvasStates]);

  // Handle URL state decoding for sharing feature
  useEffect(() => {
    const handleHashChange = async () => {
      const hashParams = new URLSearchParams(window.location.hash.slice(1));
      const stateParam = hashParams.get("state");
      if (stateParam) {
        try {
          await decodeCanvasState(stateParam);
          // Clear the state parameter from URL after successful decoding
          // so it gets persisted normally and doesn't stay in the URL
          hashParams.delete("state");
          const newHash = hashParams.toString();
          const newUrl = `${window.location.pathname}${window.location.search}${newHash ? `#${newHash}` : ""}`;
          window.history.replaceState(null, "", newUrl);
        } catch (error) {
          // Ensure error is an Error object
          setFatalError(
            error instanceof Error ? error : new Error(String(error))
          );
        }
      }
    };

    // Listen for hash changes
    window.addEventListener("hashchange", handleHashChange);

    // Initial load
    handleHashChange();

    // Cleanup
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, [decodeCanvasState]);

  const handleTitleChange = (newTitle: string) => {
    if (newTitle.trim()) {
      setTitle(newTitle);
      document.title = newTitle;
      setCurrentTitle(newTitle);
    }
  };

  useEffect(() => {
    if (!userContextSupabase) {
      return;
    }
    const {
      data: { subscription }
    } = userContextSupabase.auth.onAuthStateChange((_event, session) => {
      setCurrentUser(session?.user ?? null);
    });
    return () => subscription.unsubscribe();
  }, []);

  // Add Supabase status check on page load
  useEffect(() => {
    if (!userContextSupabase) {
      return;
    }
    const checkStatus = async () => {
      // Use 3 retries to ensure we're not showing errors due to temporary network issues
      const status = await checkSupabaseStatus(userContextSupabase!, 3);
      supabaseStatusRef.current = status;

      if (!status.isHealthy) {
        console.error("Supabase connection issue:", status.message);

        if (currentUser) {
          // User is logged in, show error toast
          toast({
            title: "Backend Connection Issue",
            description: status.message,
            status: "error",
            duration: 10000,
            isClosable: true,
            position: "top"
          });
        }
      }
    };

    checkStatus();

    // Set up periodic checks every 60 seconds
    const intervalId = setInterval(checkStatus, 60000);

    return () => {
      clearInterval(intervalId);
    };
  }, [currentUser]);

  // Update the auth dialog to show Supabase status error if needed
  const handleAuthDialogOpen = async () => {
    if (!userContextSupabase) {
      supabaseStatusRef.current = {
        isHealthy: false,
        message: "No supabase client available"
      };
      return;
    }
    try {
      let status = supabaseStatusRef.current;
      if (!status) {
        openLoadingModal(
          "⚠️There seems to be an issue wtih the backend, checking..."
        );
        const timeoutPromise = new Promise<{
          isHealthy: boolean;
          message: string;
        }>((resolve) => {
          setTimeout(() => {
            resolve({
              isHealthy: false,
              message: "Connection timed out"
            });
          }, 3000);
        });

        // Race between the actual check and the timeout
        status = await Promise.race([
          checkSupabaseStatus(userContextSupabase, 1),
          timeoutPromise
        ]);

        supabaseStatusRef.current = status;
      }
      // Check if Supabase is experiencing connection issues
      if (status && !status.isHealthy) {
        // Show an error toast
        toast({
          title: "Backend Connection Issue",
          description: `Cannot sign in: ${status.message}. Please try again later.`,
          status: "error",
          duration: 10000,
          isClosable: true
        });

        // Still open the dialog to show the connection error message
        openAuthDialog(status.message);
        return;
      }

      // If no connection issues, open the auth dialog normally
      openAuthDialog();
    } finally {
      closeLoadingModal();
    }
  };

  const handleExportSvg = () => {
    try {
      const svgElement = canvasSvgRef?.cloneNode(true) as SVGSVGElement;
      const svgString = svgElement.outerHTML;
      const blob = new Blob([svgString], { type: "image/svg+xml" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "quantum_lego_network.svg";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast({
        title: "Export successful",
        description: "SVG file is being downloaded",
        status: "success",
        duration: 3000,
        isClosable: true
      });
    } catch (error) {
      console.error("Error exporting SVG:", error);
      toast({
        title: "Export failed",
        description: "SVG file could not be generated/downloaded",
        status: "error",
        duration: 3000,
        isClosable: true
      });
    }
  };

  const handleHelpClick = () => {
    openHelpDialog(
      "/docs/planqtn-studio/ui-controls/#the-canvas",
      "Canvas Help"
    );
  };

  function handleTitleKeyDown(
    event: React.KeyboardEvent<HTMLDivElement>
  ): void {
    event.stopPropagation();
  }

  return (
    <>
      <KeyboardHandler onSetAltKeyPressed={setAltKeyPressed} />

      <CanvasMouseHandler
        selectionManagerRef={selectionManagerRef}
        zoomLevel={zoomLevel}
        altKeyPressed={altKeyPressed}
        handleDynamicLegoDrop={handleDynamicLegoDrop}
      />

      <VStack spacing={0} align="stretch" h="100vh">
        {fatalError &&
          (() => {
            throw fatalError;
          })()}
        {/* Main Content */}
        <Box
          ref={panelGroupContainerRef}
          flex={1}
          position="relative"
          overflow="hidden"
        >
          <PanelGroup direction="horizontal">
            {/* Main Content */}
            <Panel id="main-panel" defaultSize={100} minSize={5} order={1}>
              <Box h="100%" display="flex" flexDirection="column" p={4}>
                {/* Canvas with overlay controls */}
                <Box
                  ref={setCanvasRef}
                  flex={1}
                  bg="gray.100"
                  borderRadius="lg"
                  boxShadow="inner"
                  position="relative"
                  data-canvas="true"
                  style={{
                    userSelect: "none",
                    overflow: "hidden",
                    cursor: altKeyPressed
                      ? canvasDragState?.isDragging
                        ? "grabbing"
                        : "grab"
                      : "default"
                  }}
                >
                  {/* Top-left three-dots menu */}
                  <Box position="absolute" top={2} left={2} zIndex={2000}>
                    <CanvasMenu handleExportSvg={handleExportSvg} />
                  </Box>
                  {/* Floating panels toolbar */}
                  <FloatingPanelsToolbar />
                  {/* Top-center title (contextual) */}
                  <Box
                    position="absolute"
                    top={2}
                    left="50%"
                    transform="translateX(-50%)"
                    zIndex={15}
                    opacity={0.2}
                    _hover={{ opacity: 1 }}
                    transition="opacity 0.2s"
                    bg={useColorModeValue("white", "gray.800")}
                    borderRadius="md"
                    boxShadow="md"
                    px={3}
                    py={1}
                  >
                    <Editable
                      value={currentTitle}
                      onChange={handleTitleChange}
                      onKeyDown={handleTitleKeyDown}
                    >
                      <EditablePreview fontSize="sm" />
                      <EditableInput fontSize="sm" />
                    </Editable>
                  </Box>
                  {/* Top-right controls */}
                  <Box
                    position="absolute"
                    top={2}
                    right={2}
                    zIndex={20}
                    display="flex"
                    gap={2}
                  >
                    {/* Documentation button */}
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Box
                          bg="transparent"
                          borderRadius="md"
                          px={2}
                          py={2}
                          opacity={0.8}
                          _hover={{
                            opacity: 1,
                            bg: useColorModeValue("gray.100", "gray.700")
                          }}
                          transition="opacity 0.2s"
                          cursor="pointer"
                          onClick={() => window.open("/docs/", "_blank")}
                          alignItems="center"
                          display="flex"
                        >
                          <Icon as={FiFileText} boxSize={5} />
                        </Box>
                      </TooltipTrigger>
                      <TooltipContent className="high-z">
                        Documentation
                      </TooltipContent>
                    </Tooltip>
                    {/* Share button */}
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Box
                          bg="transparent"
                          borderRadius="md"
                          px={2}
                          py={2}
                          opacity={0.8}
                          _hover={{
                            opacity: 1,
                            bg: useColorModeValue("gray.100", "gray.700")
                          }}
                          transition="opacity 0.2s"
                          cursor="pointer"
                          onClick={openShareDialog}
                          alignItems="center"
                          display="flex"
                        >
                          <Icon as={FiShare2} boxSize={5} />
                        </Box>
                      </TooltipTrigger>
                      <TooltipContent className="high-z">
                        Share canvas
                      </TooltipContent>
                    </Tooltip>
                    {/* User menu */}
                    <Box
                      bg="transparent"
                      borderRadius="md"
                      p={1}
                      opacity={0.8}
                      _hover={{ opacity: 1 }}
                      transition="opacity 0.2s"
                    >
                      <UserMenu onSignIn={handleAuthDialogOpen} />
                    </Box>
                  </Box>

                  <svg
                    id="canvas-svg"
                    xmlns="http://www.w3.org/2000/svg"
                    ref={setCanvasSvgRef}
                    style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      width: "100%",
                      height: "100%",
                      pointerEvents: "none",
                      userSelect: "none"
                    }}
                    viewBox={
                      canvasRef
                        ? `0 0 ${canvasRef?.current?.clientWidth} ${canvasRef?.current?.clientHeight}`
                        : undefined
                    }
                  >
                    <ConnectionsLayer bodyOrder="behind" />
                    {/* Selection Manager */}
                    <LegosLayer />
                    <ConnectionsLayer bodyOrder="front" />
                  </svg>

                  {/* Subnet Toolbar Overlay - rendered outside SVG context */}
                  <SubnetToolbarOverlay />

                  <SelectionManager ref={selectionManagerRef} />

                  {/* Drag Proxy for smooth dragging */}
                  <DragProxy />

                  {/* Focus Bounding Box for tensor network focus effect */}
                  <FocusBoundingBox />

                  {import.meta.env.VITE_ENV === "debug" && (
                    // Debug viewport overlay
                    <ViewportDebugOverlay />
                  )}

                  {/* Mini-map with zoom level display */}
                  <CanvasMiniMap />

                  {/* Help button in bottom left corner */}
                  <Box position="absolute" bottom={2} left={2} zIndex={1000}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Box
                          bg="transparent"
                          borderRadius="md"
                          px={2}
                          py={2}
                          opacity={0.7}
                          _hover={{
                            opacity: 1,
                            bg: useColorModeValue("gray.100", "gray.700")
                          }}
                          transition="opacity 0.2s"
                          cursor="pointer"
                          onClick={handleHelpClick}
                          alignItems="center"
                          display="flex"
                        >
                          <Icon as={QuestionIcon} boxSize={5} />
                        </Box>
                      </TooltipTrigger>
                      <TooltipContent className="high-z">
                        Canvas Help
                      </TooltipContent>
                    </Tooltip>
                  </Box>
                </Box>
              </Box>
            </Panel>
          </PanelGroup>
          {/* Error Panel */}
          <ErrorPanel />
        </Box>

        <FloatingPanelHandler />
      </VStack>

      {/* Network dialogs managed by ModalRoot */}
      <ModalRoot currentUser={currentUser} setError={setError} />
    </>
  );
};

export default LegoStudioView;
