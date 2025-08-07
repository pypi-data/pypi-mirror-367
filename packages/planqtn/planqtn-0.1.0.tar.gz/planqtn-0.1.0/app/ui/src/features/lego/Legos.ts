import { DroppedLego, LegoPiece } from "../../stores/droppedLegoStore.ts";
import { GF2 } from "../../lib/GF2.ts";
import { is_gauss_equivalent } from "../../lib/parity_check.ts";
import { LogicalPoint } from "../../types/coordinates.ts";

export enum LegoType {
  H = "h",
  ZREP = "z_rep_code",
  XREP = "x_rep_code",
  T6 = "t6",
  T6_FLIPPED = "t6_flipped",
  T5 = "t5",
  T5_FLIPPED = "t5_flipped",
  T5X = "t5x",
  T5Z = "t5z",
  STOPPER_X = "stopper_x",
  STOPPER_Z = "stopper_z",
  STOPPER_Y = "stopper_y",
  STOPPER_I = "stopper_i",
  ID = "identity"
}

export interface DynamicLegoRequest {
  lego_id: string;
  parameters: Record<string, unknown>;
}

export class Legos {
  private static encoding_tensor_603 = [
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
    [1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1]
  ];

  private static steane_code_813_encoding_tensor = [
    [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
  ];

  private static identity = [
    [1, 1, 0, 0],
    [0, 0, 1, 1]
  ];

  private static encoding_tensor_512 = [
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
    [1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 0, 1]
  ];

  private static h = [
    [1, 0, 0, 1],
    [0, 1, 1, 0]
  ];

  private static stopper_x_paulis = [[1, 0]];
  private static stopper_z_paulis = [[0, 1]];
  private static stopper_i_paulis = [[0, 0]];

  public static z_rep_code(d: number = 3): number[][] {
    const gens: number[][] = [];
    for (let i = 0; i < d - 1; i++) {
      const g = Array(2 * d).fill(0);
      g[d + i] = 1;
      g[d + i + 1] = 1;
      gens.push(g);
    }
    const g = Array(2 * d).fill(0);
    for (let i = 0; i < d; i++) {
      g[i] = 1;
    }
    gens.push(g);
    return gens;
  }

  public static x_rep_code(d: number = 3): number[][] {
    const gens: number[][] = [];
    for (let i = 0; i < d - 1; i++) {
      const g = Array(2 * d).fill(0);
      g[i] = 1;
      g[i + 1] = 1;
      gens.push(g);
    }
    const g = Array(2 * d).fill(0);
    for (let i = d; i < 2 * d; i++) {
      g[i] = 1;
    }
    gens.push(g);
    return gens;
  }

  public static listAvailableLegos(): LegoPiece[] {
    return [
      this.stopper_x(),
      this.stopper_z(),
      this.stopper_i(),
      {
        type_id: LegoType.H,
        name: "Hadamard",
        short_name: "H",
        description: "Hadamard tensor",
        parity_check_matrix: this.h,
        logical_legs: [],
        gauge_legs: [],
        is_dynamic: false,
        parameters: {}
      },
      {
        type_id: LegoType.ID,
        name: "Identity",
        short_name: "I",
        description: "Identity tensor",
        parity_check_matrix: this.identity,
        logical_legs: [],
        gauge_legs: [],
        is_dynamic: false,
        parameters: {}
      },

      {
        type_id: LegoType.ZREP,
        name: "Z-Repetition Code",
        short_name: "ZREP3",
        description: "Bitflip code, ZZ stabilizers",
        is_dynamic: true,
        parameters: { d: 3 },
        parity_check_matrix: this.z_rep_code(),
        logical_legs: [],
        gauge_legs: []
      },
      {
        type_id: LegoType.XREP,
        name: "X-Repetition Code",
        short_name: "XREP3",
        description: "Phase flip code, XX stabilizers",
        is_dynamic: true,
        parameters: { d: 3 },
        parity_check_matrix: this.x_rep_code(),
        logical_legs: [],
        gauge_legs: []
      },

      {
        type_id: LegoType.T6,
        name: "[[6,0,3]] tensor",
        short_name: "T6",
        description: "[[6,0,3]] encoding tensor",
        parity_check_matrix: this.encoding_tensor_603,
        logical_legs: [4, 5],
        gauge_legs: [],
        is_dynamic: false,
        parameters: {}
      },
      {
        type_id: LegoType.T6_FLIPPED,
        name: "[[6,0,3]] tensor flipped",
        short_name: "T6F",
        description: "[[6,0,3]] encoding tensor flipped",
        parity_check_matrix: this.encoding_tensor_603,
        logical_legs: [4, 5],
        gauge_legs: [],
        is_dynamic: false,
        parameters: {}
      },
      {
        type_id: LegoType.T5,
        name: "[[5,1,2]] subspace tensor",
        short_name: "T5",
        description: "[[5,1,2]] encoding tensor",
        parity_check_matrix: this.encoding_tensor_512,
        logical_legs: [4],
        gauge_legs: [],
        is_dynamic: false,
        parameters: {}
      },
      {
        type_id: LegoType.T5_FLIPPED,
        name: "[[5,1,2]] flipped subspace tensor",
        short_name: "T5F",
        description: "[[5,1,2]] flipped subspace tensor",
        parity_check_matrix: this.encoding_tensor_512,
        logical_legs: [4],
        gauge_legs: [],
        is_dynamic: false,
        parameters: {}
      },
      {
        type_id: "steane",
        name: "Steane Code",
        short_name: "STN",
        description: "Steane code encoding tensor",
        parity_check_matrix: this.steane_code_813_encoding_tensor,
        logical_legs: [7],
        gauge_legs: [],
        is_dynamic: false,
        parameters: {}
      },
      {
        type_id: "832",
        name: "[[8,3,2]] code",
        short_name: "[[8,3,2]]",
        description: "[[8,3,2]] encoding tensor with all 3 logical legs",

        parity_check_matrix: [
          [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        ],
        logical_legs: [8, 9, 10],
        gauge_legs: [],
        is_dynamic: false,
        parameters: {}
      },
      {
        type_id: "15qrm",
        name: "[[15,1,3]] QRM",
        short_name: "QRM15",
        description: "[[15,1,3]] Quantum Reed-Muller code encoding tensor",
        // prettier-ignore
        parity_check_matrix: [
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1]
        ],
        logical_legs: [15],
        gauge_legs: [],
        is_dynamic: false,
        parameters: {}
      }
    ];
  }
  static stopper_i(): LegoPiece {
    return {
      type_id: LegoType.STOPPER_I,
      name: "Identity Stopper",
      short_name: "I",
      description: "Identity stopper tensor",
      parity_check_matrix: this.stopper_i_paulis,
      logical_legs: [],
      gauge_legs: [],
      is_dynamic: false,
      parameters: {}
    };
  }
  static stopper_z(): LegoPiece {
    return {
      type_id: LegoType.STOPPER_Z,
      name: "Z Stopper",
      short_name: "Z",
      description: "Z-type stopper tensor",
      parity_check_matrix: this.stopper_z_paulis,
      logical_legs: [],
      gauge_legs: [],
      is_dynamic: false,
      parameters: {}
    };
  }
  static stopper_x(): LegoPiece {
    return {
      type_id: LegoType.STOPPER_X,
      name: "X Stopper",
      short_name: "X",
      description: "X-type stopper tensor",
      parity_check_matrix: this.stopper_x_paulis,
      logical_legs: [],
      gauge_legs: [],
      is_dynamic: false,
      parameters: {}
    };
  }

  public static getDynamicLego(request: DynamicLegoRequest): LegoPiece {
    // Get the lego definition from available legos
    const legos = this.listAvailableLegos();
    const legoDef = legos.find((l) => l.type_id === request.lego_id);

    if (!legoDef || !legoDef.is_dynamic) {
      throw new Error(`Invalid or non-dynamic lego ID: ${request.lego_id}`);
    }

    // Handle different dynamic lego types
    switch (request.lego_id) {
      case LegoType.ZREP:
      case LegoType.XREP: {
        const d = request.parameters.d as number;
        if (typeof d !== "number" || d < 1) {
          throw new Error(`Invalid parameter 'd' for repetition code: ${d}`);
        }
        if (d == 1) {
          return request.lego_id === LegoType.ZREP
            ? this.stopper_x()
            : this.stopper_z();
        }
        const matrix =
          request.lego_id === LegoType.ZREP
            ? this.z_rep_code(d)
            : this.x_rep_code(d);
        return {
          ...legoDef,
          parity_check_matrix: matrix,
          parameters: { d }
        };
      }
      default:
        throw new Error(`Unsupported dynamic lego type: ${request.lego_id}`);
    }
  }

  public static createDynamicLego(
    legoId: string,
    numLegs: number,
    instance_id: string,
    logicalPosition: LogicalPoint
  ): DroppedLego {
    const data = this.getDynamicLego({
      lego_id: legoId,
      parameters: {
        d: numLegs
      }
    });

    return new DroppedLego(data, logicalPosition, instance_id);
  }
}

export function recognize_parityCheckMatrix(h: GF2): string | null {
  // Get all available legos
  const legos = Legos.listAvailableLegos();

  // First check static legos
  for (const lego of legos) {
    if (!lego.is_dynamic) {
      const lego_matrix = new GF2(lego.parity_check_matrix);
      if (is_gauss_equivalent(h, lego_matrix)) {
        return lego.type_id;
      }
    }
  }

  // Then check for repetition codes
  const num_qubits = h.shape[1] / 2;
  if (num_qubits > 0) {
    // Z repetition code
    const z_rep = Legos.z_rep_code(num_qubits);
    if (is_gauss_equivalent(h, new GF2(z_rep))) {
      return "z_rep_code";
    }

    // X repetition code
    const x_rep = Legos.x_rep_code(num_qubits);
    if (is_gauss_equivalent(h, new GF2(x_rep))) {
      return "x_rep_code";
    }
  }

  return null;
}
