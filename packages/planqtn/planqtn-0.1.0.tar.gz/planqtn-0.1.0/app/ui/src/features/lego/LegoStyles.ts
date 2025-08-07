import { PauliOperator } from "../../lib/types";
import {
  getPauliColor,
  I_COLOR,
  I_COLOR_DARK,
  I_COLOR_LIGHT,
  X_COLOR,
  X_COLOR_DARK,
  X_COLOR_LIGHT,
  Z_COLOR,
  Z_COLOR_DARK,
  Z_COLOR_LIGHT
} from "../../lib/PauliColors";
import { DroppedLego } from "../../stores/droppedLegoStore";

export const Z_REP_CODE = "z_rep_code";
export const X_REP_CODE = "x_rep_code";

// Color mapping for SVG elements
const chakraToHexColors: { [key: string]: string } = {
  white: "#FFFFFF",
  "yellow.200": "#FBD38D",
  "yellow.400": "#F6AD55",
  "yellow.500": "#ECC94B",
  "yellow.600": "#D69E2E",
  "yellow.700": "#B7791F",
  "blue.100": "#BEE3F8",
  "blue.200": "#90CDF4",
  "blue.300": "#63B3ED",
  "blue.400": "#4299E1",
  "blue.500": "#3182CE",
  "blue.600": "#2B6CB0",
  "blue.700": "#2C5282",
  "green.200": "#9AE6B4",
  "green.300": "#68D391",
  "green.400": "#48BB78",
  "green.700": "#2F855A",
  "red.200": "#FEB2B2",
  "red.300": "#FC8181",
  "red.400": "#F56565",
  "red.700": "#C53030",
  "gray.100": "#F3F4F6",
  "gray.200": "#E5E7EB",
  "gray.300": "#D1D5DB",
  "gray.400": "#9CA3AF",
  "gray.500": "#6B7280",
  "gray.600": "#4B5563",
  "gray.700": "#374151"
};

export interface LegPosition {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  labelX: number;
  labelY: number;
  angle: number;
}

const LEG_LABEL_DISTANCE = 15;

export interface LegStyle {
  angle: number;
  length: number;
  width: string;
  lineStyle: "solid" | "dashed";
  color: string;
  is_highlighted: boolean;
  type: "logical" | "gauge" | "physical";
  position: LegPosition;
  bodyOrder: "front" | "behind";
}

// Styling for a given lego. This contains calculated leg positions, colors for the legs etc.
export abstract class LegoStyle {
  public readonly legStyles: LegStyle[];
  constructor(
    protected readonly id: string,
    protected readonly lego: DroppedLego,
    protected readonly overrideLegStyles?: LegStyle[]
  ) {
    this.legStyles =
      overrideLegStyles || lego.numberOfLegs > 0
        ? Array(lego.numberOfLegs)
            .fill(0)
            .map((_, i) => {
              return this.calculateLegStyle(i, true);
            })
        : [];
  }

  get displayShortName(): boolean {
    return true;
  }

  abstract get size(): number;
  abstract get borderRadius(): string;
  abstract get backgroundColor(): string;
  abstract get borderColor(): string;
  abstract get selectedBackgroundColor(): string;
  abstract get selectedBorderColor(): string;

  // New methods for SVG colors
  getBackgroundColorForSvg(): string {
    return chakraToHexColors[this.backgroundColor] || this.backgroundColor;
  }

  getBorderColorForSvg(): string {
    return chakraToHexColors[this.borderColor] || this.borderColor;
  }

  getSelectedBackgroundColorForSvg(): string {
    return (
      chakraToHexColors[this.selectedBackgroundColor] ||
      this.selectedBackgroundColor
    );
  }

  getSelectedBorderColorForSvg(): string {
    return (
      chakraToHexColors[this.selectedBorderColor] || this.selectedBorderColor
    );
  }

  getLegHighlightPauliOperator = (leg_index: number) => {
    // First check if there's a pushed leg
    const h = this.lego.parity_check_matrix;
    const num_legs = h[0].length / 2;

    if (this.lego.selectedMatrixRows === undefined) {
      return PauliOperator.I;
    }

    const combinedRow = new Array(this.lego.parity_check_matrix[0].length).fill(
      0
    );

    for (const rowIndex of this.lego.selectedMatrixRows) {
      this.lego.parity_check_matrix[rowIndex].forEach((val, idx) => {
        combinedRow[idx] = (combinedRow[idx] + val) % 2;
      });
    }

    const xPart = combinedRow[leg_index];
    const zPart = combinedRow[leg_index + num_legs];

    if (xPart === 1 && zPart === 0) return PauliOperator.X;
    if (xPart === 0 && zPart === 1) return PauliOperator.Z;
    if (xPart === 1 && zPart === 1) return PauliOperator.Y;

    return PauliOperator.I;
  };

  getLegPosition(
    length: number,
    angle: number,
    labelDistance: number
  ): LegPosition {
    // Calculate start position relative to center
    const startX = 0;
    const startY = 0;

    // Calculate end position
    const endX = startX + length * Math.cos(angle);
    const endY = startY + length * Math.sin(angle);

    // Calculate label position
    const labelX = endX + labelDistance * Math.cos(angle);
    const labelY = endY + labelDistance * Math.sin(angle);

    return {
      startX,
      startY,
      endX,
      endY,
      labelX,
      labelY,
      angle: angle
    };
  }

  protected calculateLegProps(leg_index: number): {
    isLogical: boolean;
    isGauge: boolean;
    isHighlighted: boolean;
    highlightOperator: PauliOperator;
  } {
    const isLogical = this.lego.logical_legs.includes(leg_index);
    const isGauge = this.lego.gauge_legs.includes(leg_index);
    const localHighlightPauliOperator =
      this.getLegHighlightPauliOperator(leg_index);
    const globalHighlightPauliOperator =
      this.lego.highlightedLegConstraints.find(
        (constraint) => constraint.legIndex === leg_index
      )?.operator || PauliOperator.I;

    const isHighlighted =
      localHighlightPauliOperator !== PauliOperator.I ||
      globalHighlightPauliOperator !== PauliOperator.I;

    const highlightOperator =
      globalHighlightPauliOperator === PauliOperator.I
        ? localHighlightPauliOperator
        : globalHighlightPauliOperator;

    return {
      isLogical,
      isGauge,
      isHighlighted,
      highlightOperator
    };
  }

  private calculateLegStyle(
    leg_index: number,
    forSvg: boolean = false
  ): LegStyle {
    const { isLogical, isGauge, isHighlighted, highlightOperator } =
      this.calculateLegProps(leg_index);

    const legCount = this.lego.numberOfLegs;

    // Calculate the number of each type of leg
    const logicalLegsCount = this.lego.logical_legs.length;
    const physicalLegsCount =
      legCount - logicalLegsCount - this.lego.gauge_legs.length;

    if (isLogical) {
      // Sort logical legs to ensure consistent ordering regardless of their indices
      const sortedLogicalLegs = [...this.lego.logical_legs].sort(
        (a, b) => a - b
      );
      const logicalIndex = sortedLogicalLegs.indexOf(leg_index);

      if (logicalLegsCount === 1) {
        // Single logical leg points straight up
        return {
          angle: -Math.PI / 2,
          length: 60,
          width: "3px",
          lineStyle: "solid",
          color: forSvg
            ? getPauliColor(highlightOperator, true)
            : getPauliColor(highlightOperator),
          is_highlighted: isHighlighted,
          type: "logical",
          position: this.getLegPosition(60, -Math.PI / 2, LEG_LABEL_DISTANCE),
          bodyOrder: "behind"
        };
      }

      // For multiple logical legs, calculate the required spread based on count
      // Use a minimum of 30 degrees between legs
      const minSpreadPerLeg = Math.PI / 6; // 30 degrees
      const totalSpread = Math.min(
        Math.PI * 0.8,
        minSpreadPerLeg * (logicalLegsCount - 1)
      );
      const startAngle = -Math.PI / 2 - totalSpread / 2;
      const angle =
        startAngle + (totalSpread * logicalIndex) / (logicalLegsCount - 1);

      return {
        angle,
        length: 60,
        width: "3px",
        lineStyle: "solid",
        color: forSvg
          ? getPauliColor(highlightOperator, true)
          : getPauliColor(highlightOperator),
        is_highlighted: isHighlighted,
        type: "logical",
        position: this.getLegPosition(60, angle, LEG_LABEL_DISTANCE),
        bodyOrder: "behind"
      };
    } else if (isGauge) {
      // For gauge legs, calculate angle from bottom
      const angle = Math.PI + (2 * Math.PI * leg_index) / legCount;
      return {
        angle,
        length: 40,
        width: "2px",
        lineStyle: "dashed",
        color: forSvg
          ? getPauliColor(highlightOperator, true)
          : getPauliColor(highlightOperator),
        is_highlighted: isHighlighted,
        type: "gauge",
        position: this.getLegPosition(40, angle, LEG_LABEL_DISTANCE),
        bodyOrder: "behind"
      };
    } else {
      // For physical legs
      // Create an array of all physical leg indices (non-logical, non-gauge legs)
      const physicalLegIndices = Array.from({ length: legCount }, (_, i) => i)
        .filter(
          (i) =>
            !this.lego.logical_legs.includes(i) &&
            !this.lego.gauge_legs.includes(i)
        )
        .sort((a, b) => a - b);

      // Find the index of the current leg in the physical legs array
      const physicalIndex = physicalLegIndices.indexOf(leg_index);

      if (physicalLegsCount === 1) {
        // Single physical leg points straight down
        return {
          angle: Math.PI / 2,
          length: 40,
          width: highlightOperator === PauliOperator.I ? "1px" : "3px",
          lineStyle: "solid",
          color: forSvg
            ? getPauliColor(highlightOperator, true)
            : getPauliColor(highlightOperator),
          is_highlighted: isHighlighted,
          type: "physical",
          position: this.getLegPosition(40, Math.PI / 2, LEG_LABEL_DISTANCE),
          bodyOrder: "behind"
        };
      }

      if (logicalLegsCount === 0) {
        // If no logical legs, distribute physical legs evenly around the circle
        const angle = (2 * Math.PI * physicalIndex) / physicalLegsCount;
        return {
          angle,
          length: 40,
          width: highlightOperator === PauliOperator.I ? "1px" : "3px",
          lineStyle: "solid",
          color: forSvg
            ? getPauliColor(highlightOperator, true)
            : getPauliColor(highlightOperator),
          is_highlighted: isHighlighted,
          type: "physical",
          position: this.getLegPosition(40, angle, LEG_LABEL_DISTANCE),
          bodyOrder: "behind"
        };
      }

      // For multiple physical legs with logical legs present
      // Calculate the space needed for logical legs with increased spread
      const logicalSpread =
        logicalLegsCount <= 1
          ? Math.PI / 4 // Increased from PI/6 to PI/4
          : Math.min(Math.PI, (Math.PI / 4) * (logicalLegsCount - 1)); // Increased from PI/6 to PI/4

      // Use most of the remaining space for physical legs, leaving a small gap
      const availableAngle = 2 * Math.PI - logicalSpread - Math.PI / 6; // Leave a small gap

      // Start just after the logical legs section
      const startAngle = -Math.PI / 2 + logicalSpread / 2 + Math.PI / 12;
      const angle =
        startAngle + (availableAngle * physicalIndex) / (physicalLegsCount - 1);

      return {
        angle,
        length: 40,
        width: highlightOperator === PauliOperator.I ? "1px" : "3px",
        lineStyle: "solid",
        color: forSvg
          ? getPauliColor(highlightOperator, true)
          : getPauliColor(highlightOperator),
        is_highlighted: isHighlighted,
        type: "physical",
        position: this.getLegPosition(40, angle, LEG_LABEL_DISTANCE),
        bodyOrder: "behind"
      };
    }
  }

  getLegColor(leg_index: number): string {
    const legStyle = this.legStyles[leg_index];
    return legStyle.color;
  }
}

export class HadamardStyle extends LegoStyle {
  get size(): number {
    return 20;
  }

  get borderRadius(): string {
    return "0";
  }

  get backgroundColor(): string {
    return "yellow.200";
  }

  get borderColor(): string {
    return "yellow.400";
  }

  get selectedBackgroundColor(): string {
    return "yellow.500";
  }

  get selectedBorderColor(): string {
    return "yellow.600";
  }

  get displayShortName(): boolean {
    return false;
  }
}

export class GenericStyle extends LegoStyle {
  get size(): number {
    return 50;
  }

  get borderRadius(): string {
    return "full";
  }

  get backgroundColor(): string {
    return "white";
  }

  get borderColor(): string {
    return "blue.400";
  }

  get selectedBackgroundColor(): string {
    return "blue.500";
  }

  get selectedBorderColor(): string {
    return "blue.700";
  }
}

export class IdentityStyle extends LegoStyle {
  get size(): number {
    return 20;
  }

  get borderRadius(): string {
    return "full";
  }

  get backgroundColor(): string {
    return "white";
  }

  get borderColor(): string {
    return "blue.400";
  }

  get selectedBackgroundColor(): string {
    return "blue.100";
  }

  get selectedBorderColor(): string {
    return "blue.500";
  }

  get displayShortName(): boolean {
    return false;
  }
}

export class RepetitionCodeStyle extends LegoStyle {
  get size(): number {
    return 30;
  }

  get borderRadius(): string {
    return "full";
  }

  get backgroundColor(): string {
    return this.id === Z_REP_CODE ? X_COLOR_LIGHT : Z_COLOR_LIGHT;
  }

  get borderColor(): string {
    return this.id === Z_REP_CODE ? X_COLOR : Z_COLOR;
  }

  get selectedBackgroundColor(): string {
    return this.id === Z_REP_CODE ? X_COLOR_DARK : Z_COLOR_DARK;
  }

  get selectedBorderColor(): string {
    return this.id === Z_REP_CODE ? X_COLOR_DARK : Z_COLOR_DARK;
  }
  get displayShortName(): boolean {
    return false;
  }
}

export class StopperStyle extends LegoStyle {
  get size(): number {
    return 20;
  }
  get borderRadius(): string {
    return "full";
  }

  get backgroundColor(): string {
    switch (this.id) {
      case "stopper_i":
        return I_COLOR_LIGHT;
      case "stopper_x":
        return X_COLOR_LIGHT;
      case "stopper_z":
        return Z_COLOR_LIGHT;
      default:
        return I_COLOR_LIGHT;
    }
  }

  get borderColor(): string {
    switch (this.id) {
      case "stopper_i":
        return I_COLOR;
      case "stopper_x":
        return X_COLOR;
      case "stopper_z":
        return Z_COLOR;
      default:
        return I_COLOR;
    }
  }

  get selectedBackgroundColor(): string {
    switch (this.id) {
      case "stopper_i":
        return I_COLOR_DARK;
      case "stopper_x":
        return X_COLOR_DARK;
      case "stopper_z":
        return Z_COLOR_DARK;
      default:
        return I_COLOR_DARK;
    }
  }

  get selectedBorderColor(): string {
    switch (this.id) {
      case "stopper_i":
        return I_COLOR_DARK;
      case "stopper_x":
        return X_COLOR_DARK;
      case "stopper_z":
        return Z_COLOR_DARK;
      default:
        return I_COLOR_DARK;
    }
  }

  get displayShortName(): boolean {
    return false;
  }
}

export class ScalarStyle extends LegoStyle {
  get size(): number {
    return 40;
  }

  get borderRadius(): string {
    return "full";
  }

  get backgroundColor(): string {
    return "none";
  }

  get borderColor(): string {
    return "black";
  }

  get selectedBackgroundColor(): string {
    return "blue.100";
  }

  get selectedBorderColor(): string {
    return "blue.500";
  }
}
