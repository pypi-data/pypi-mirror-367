import {
  Button,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  Input,
  Text,
  VStack,
  HStack,
  Checkbox,
  Box,
  IconButton
} from "@chakra-ui/react";
import { useState, useMemo } from "react";
import { TensorNetwork, TensorNetworkLeg } from "../../lib/TensorNetwork";
import { Connection } from "../../stores/connectionStore";
import { useCanvasStore } from "../../stores/canvasStateStore";
import { HelpCircle } from "lucide-react";

interface WeightEnumeratorCalculationDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (truncateLength?: number, openLegs?: TensorNetworkLeg[]) => void;
  subNetwork: TensorNetwork;
  mainNetworkConnections: Connection[];
}

const WeightEnumeratorCalculationDialog: React.FC<
  WeightEnumeratorCalculationDialogProps
> = ({ open, onClose, onSubmit, subNetwork, mainNetworkConnections }) => {
  const openHelpDialog = useCanvasStore((state) => state.openHelpDialog);
  const { externalLegs, danglingLegs } = subNetwork.getExternalAndDanglingLegs(
    mainNetworkConnections
  );
  const [truncateLength, setTruncateLength] = useState<string>("");
  // Use string keys for easy lookup: "instance_id-leg_index"
  const externalKeys = useMemo(
    () => externalLegs.map((l) => `${l.instance_id}-${l.leg_index}`),
    [externalLegs]
  );
  const danglingKeys = useMemo(
    () => danglingLegs.map((l) => `${l.instance_id}-${l.leg_index}`),
    [danglingLegs]
  );

  // By default, external legs selected, dangling legs not
  const [selectedExternal, setSelectedExternal] = useState<Set<string>>(
    new Set(externalKeys)
  );
  const [selectedDangling, setSelectedDangling] = useState<Set<string>>(
    new Set()
  );

  // Update selection if legs change
  // (e.g. dialog is opened for a different network)

  useMemo(() => {
    setSelectedExternal(new Set(externalKeys));
  }, [externalKeys.join(",")]);

  useMemo(() => {
    setSelectedDangling(new Set());
  }, [danglingKeys.join(",")]);

  // Three-state logic for parent checkboxes
  const getParentState = (all: string[], selected: Set<string>) => {
    if (selected.size === 0) return false;
    if (selected.size === all.length) return true;
    return "indeterminate";
  };

  const handleParentToggle = (
    all: string[],
    selected: Set<string>,
    setSelected: (s: Set<string>) => void
  ) => {
    if (selected.size === all.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(all));
    }
  };

  const handleChildToggle = (
    key: string,
    selected: Set<string>,
    setSelected: (s: Set<string>) => void
  ) => {
    const newSet = new Set(selected);
    if (newSet.has(key)) {
      newSet.delete(key);
    } else {
      newSet.add(key);
    }
    setSelected(newSet);
  };

  // Collect selected legs
  const selectedLegs: TensorNetworkLeg[] = [
    ...externalLegs.filter((l) =>
      selectedExternal.has(`${l.instance_id}-${l.leg_index}`)
    ),
    ...danglingLegs.filter((l) =>
      selectedDangling.has(`${l.instance_id}-${l.leg_index}`)
    )
  ];

  const subtitle =
    selectedLegs.length === 0
      ? "Scalar weight enumerator"
      : `Tensor weight enumerator with ${selectedLegs.length} open leg${selectedLegs.length > 1 ? "s" : ""}`;

  const handleSubmit = () => {
    if (truncateLength === "") {
      onSubmit(undefined, selectedLegs);
    } else {
      const value = parseInt(truncateLength);
      if (isNaN(value) || value < 1) {
        return;
      }
      onSubmit(value, selectedLegs);
    }
    onClose();
  };

  const handleHelpClick = () => {
    openHelpDialog(
      "/docs/planqtn-studio/analyze/#weight-enumerator-polynomial-calculations",
      "Weight Enumerator Help"
    );
  };

  return (
    <Modal isOpen={open} onClose={onClose}>
      <ModalContent maxHeight="90vh" overflowY="auto" className="modal-high-z">
        <ModalHeader>
          <HStack justify="space-between" align="center">
            <Text>Weight Enumerator Calculation</Text>
            <IconButton
              aria-label="Help"
              icon={<HelpCircle size={16} />}
              size="sm"
              variant="ghost"
              onClick={handleHelpClick}
            />
          </HStack>
        </ModalHeader>
        <ModalBody>
          <VStack spacing={4} align="stretch">
            <Text fontSize="md" fontWeight="semibold">
              {subtitle}
            </Text>
            <HStack>
              <Text>Truncation level (leave empty for no truncation):</Text>
            </HStack>
            <Input
              value={truncateLength}
              onKeyDown={(e) => {
                e.stopPropagation();
                if (e.key === "Enter") {
                  handleSubmit();
                }
              }}
              onChange={(e) => setTruncateLength(e.target.value)}
              placeholder="Enter truncation level (≥ 1)"
              type="number"
              min={1}
            />
            <Box>
              <Text fontWeight="bold" mb={1}>
                External legs
              </Text>
              {externalLegs.length === 0 ? (
                <Text color="gray.500">No external connections</Text>
              ) : (
                <>
                  <Checkbox
                    isChecked={
                      getParentState(externalKeys, selectedExternal) === true
                    }
                    isIndeterminate={
                      getParentState(externalKeys, selectedExternal) ===
                      "indeterminate"
                    }
                    onChange={() =>
                      handleParentToggle(
                        externalKeys,
                        selectedExternal,
                        setSelectedExternal
                      )
                    }
                    mb={1}
                  >
                    Select all
                  </Checkbox>
                  <VStack
                    align="start"
                    spacing={1}
                    pl={4}
                    maxHeight="200px"
                    overflowY="auto"
                  >
                    {externalLegs.map((leg) => {
                      const key = `${leg.instance_id}-${leg.leg_index}`;
                      return (
                        <Checkbox
                          key={key}
                          isChecked={selectedExternal.has(key)}
                          onChange={() =>
                            handleChildToggle(
                              key,
                              selectedExternal,
                              setSelectedExternal
                            )
                          }
                        >
                          {leg.instance_id} - {leg.leg_index}
                        </Checkbox>
                      );
                    })}
                  </VStack>
                </>
              )}
            </Box>
            <Box mt={4}>
              <Text fontWeight="bold" mb={1}>
                Dangling legs
              </Text>
              {danglingLegs.length === 0 ? (
                <Text color="gray.500">No dangling legs</Text>
              ) : (
                <>
                  <Checkbox
                    isChecked={
                      getParentState(danglingKeys, selectedDangling) === true
                    }
                    isIndeterminate={
                      getParentState(danglingKeys, selectedDangling) ===
                      "indeterminate"
                    }
                    onChange={() =>
                      handleParentToggle(
                        danglingKeys,
                        selectedDangling,
                        setSelectedDangling
                      )
                    }
                    mb={1}
                  >
                    Select all
                  </Checkbox>
                  <VStack
                    align="start"
                    spacing={1}
                    pl={4}
                    maxHeight="200px"
                    overflowY="auto"
                  >
                    {danglingLegs.map((leg) => {
                      const key = `${leg.instance_id}-${leg.leg_index}`;
                      return (
                        <Checkbox
                          key={key}
                          isChecked={selectedDangling.has(key)}
                          onChange={() =>
                            handleChildToggle(
                              key,
                              selectedDangling,
                              setSelectedDangling
                            )
                          }
                        >
                          {leg.instance_id} - {leg.leg_index}
                        </Checkbox>
                      );
                    })}
                  </VStack>
                </>
              )}
            </Box>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button colorScheme="blue" onClick={handleSubmit}>
            Calculate
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default WeightEnumeratorCalculationDialog;
