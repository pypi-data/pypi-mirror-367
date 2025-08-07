import { TensorNetwork } from "./TensorNetwork";
import { Connection } from "../stores/connectionStore";
import { createHadamardLego, DroppedLego } from "../stores/droppedLegoStore.ts";
import { GF2 } from "./GF2";
import { LogicalPoint } from "../types/coordinates.ts";
import { Legos } from "../features/lego/Legos.ts";

describe("TensorNetwork", () => {
  it("should correctly conjoin nodes after double tracing 602 with identity stoppers", () => {
    // Create the nodes
    const nodes: DroppedLego[] = [
      new DroppedLego(
        {
          type_id: "encoding_tensor_602",
          name: "Encoding Tensor 602",
          short_name: "602",
          description: "Encoding Tensor 602",

          parity_check_matrix: [
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
            [1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0],
            [0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1]
          ],
          logical_legs: [],
          gauge_legs: []
        },
        new LogicalPoint(0, 0),
        "0"
      ),
      new DroppedLego(
        {
          type_id: "stopper_i",
          name: "Identity Stopper",
          short_name: "I",
          description: "Identity Stopper",

          parity_check_matrix: [[0, 0]],
          logical_legs: [],
          gauge_legs: []
        },
        new LogicalPoint(0, 0),
        "stop1"
      ),
      new DroppedLego(
        {
          type_id: "stopper_i",
          name: "Identity Stopper",
          short_name: "I",
          description: "Identity Stopper",

          parity_check_matrix: [[0, 0]],
          logical_legs: [],
          gauge_legs: []
        },
        new LogicalPoint(0, 0),
        "stop2"
      )
    ];

    // Create the connections
    const connections: Connection[] = [
      new Connection(
        { legoId: "stop1", leg_index: 0 },
        { legoId: "0", leg_index: 4 }
      ),
      new Connection(
        { legoId: "stop2", leg_index: 0 },
        { legoId: "0", leg_index: 5 }
      )
    ];

    // Create the tensor network
    const tn = new TensorNetwork({
      legos: nodes,
      connections: connections
    });

    // Get the conjoined tensor
    const conjoined = tn.conjoin_nodes();

    // Expected 422 parity check matrix
    const expected422Matrix = [
      [1, 1, 1, 1, 0, 0, 0, 0],
      [0, 0, 0, 0, 1, 1, 1, 1]
    ];

    // Compare the matrices
    expect(conjoined.h.getMatrix()).toEqual(expected422Matrix);
  });

  it("should calculate 6 lego TN parity check matrix", () => {
    // console.log(
    //   "=================6 lego TN parity check matrix=====================",
    // );
    const tn = new TensorNetwork({
      legos: [
        new DroppedLego(
          {
            type_id: "t5fake", // fake type id to avoid parsing svg
            name: "[[5,1,2]] tensor",
            short_name: "T5",
            description: "[[5,1,2]] encoding tensor",
            parity_check_matrix: [
              [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
              [1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 1, 1, 0, 1]
            ],
            logical_legs: [4],
            gauge_legs: [],
            is_dynamic: false,
            parameters: {}
          },
          new LogicalPoint(0, 0),
          "1"
        ),
        new DroppedLego(
          {
            type_id: "t5fake",
            name: "[[5,1,2]] tensor",
            short_name: "T5",
            description: "[[5,1,2]] encoding tensor",
            parity_check_matrix: [
              [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
              [1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 1, 1, 0, 1]
            ],
            logical_legs: [4],
            gauge_legs: [],
            is_dynamic: false,
            parameters: {}
          },
          new LogicalPoint(0, 0),
          "2"
        ),
        new DroppedLego(
          {
            type_id: "t5fake",
            name: "[[5,1,2]] tensor",
            short_name: "T5",
            description: "[[5,1,2]] encoding tensor",
            parity_check_matrix: [
              [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
              [1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 1, 1, 0, 1]
            ],
            logical_legs: [4],
            gauge_legs: [],
            is_dynamic: false,
            parameters: {}
          },
          new LogicalPoint(0, 0),
          "3"
        ),
        new DroppedLego(
          {
            type_id: "t5fake",
            name: "[[5,1,2]] tensor",
            short_name: "T5",
            description: "[[5,1,2]] encoding tensor",
            parity_check_matrix: [
              [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
              [1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 1, 1, 0, 1]
            ],
            logical_legs: [4],
            gauge_legs: [],
            is_dynamic: false,
            parameters: {}
          },
          new LogicalPoint(0, 0),
          "4"
        ),
        new DroppedLego(
          {
            type_id: "t5fake",
            name: "[[5,1,2]] tensor",
            short_name: "T5",
            description: "[[5,1,2]] encoding tensor",
            parity_check_matrix: [
              [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
              [1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 1, 1, 0, 1]
            ],
            logical_legs: [4],
            gauge_legs: [],
            is_dynamic: false,
            parameters: {}
          },
          new LogicalPoint(0, 0),
          "5"
        ),
        new DroppedLego(
          {
            type_id: "t5fake",
            name: "[[5,1,2]] tensor",
            short_name: "T5",
            description: "[[5,1,2]] encoding tensor",
            parity_check_matrix: [
              [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
              [1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 1, 1, 0, 1]
            ],
            logical_legs: [4],
            gauge_legs: [],
            is_dynamic: false,
            parameters: {}
          },
          new LogicalPoint(0, 0),
          "6"
        )
      ],
      connections: [
        new Connection(
          { legoId: "5", leg_index: 0 },
          { legoId: "6", leg_index: 3 }
        ),
        new Connection(
          { legoId: "4", leg_index: 0 },
          { legoId: "5", leg_index: 3 }
        ),
        new Connection(
          { legoId: "4", leg_index: 2 },
          { legoId: "3", leg_index: 3 }
        ),
        new Connection(
          { legoId: "4", leg_index: 1 },
          { legoId: "3", leg_index: 0 }
        ),
        new Connection(
          { legoId: "5", leg_index: 2 },
          { legoId: "2", leg_index: 3 }
        ),
        new Connection(
          { legoId: "6", leg_index: 1 },
          { legoId: "1", leg_index: 0 }
        ),
        new Connection(
          { legoId: "2", leg_index: 1 },
          { legoId: "1", leg_index: 2 }
        ),
        new Connection(
          { legoId: "1", leg_index: 3 },
          { legoId: "2", leg_index: 0 }
        )
      ]
    });
    const conjoined = tn.conjoin_nodes();

    // prettier-ignore
    const expectedMatrix = GF2.gauss(new GF2([
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
      [0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
      [0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
      [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]));

    // console.log(sstr(GF2.gauss(conjoined.h)));
    // console.log(sstr(expectedMatrix));
    expect(GF2.gauss(conjoined.h)).toEqual(expectedMatrix);
  });

  it("should correctly fuse two legos with new legs containing the old leg ids", () => {
    const tn = new TensorNetwork({
      legos: [
        createHadamardLego(new LogicalPoint(0, 0), "1"),
        createHadamardLego(new LogicalPoint(1, 1), "2")
      ],
      connections: []
    });
    const conjoined = tn.conjoin_nodes();
    expect(conjoined.h).toEqual(
      new GF2([
        [1, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0, 0, 1, 0]
      ])
    );
    expect(conjoined.legs).toEqual([
      { instance_id: "1", leg_index: 0 },
      { instance_id: "1", leg_index: 1 },
      { instance_id: "2", leg_index: 0 },
      { instance_id: "2", leg_index: 1 }
    ]);
  });

  // repro https://github.com/planqtn/planqtn/issues/118
  it("should conjoin a free qubit with a regular lego", () => {
    const zero = new GF2([[0]]);
    const z3 = new GF2(Legos.z_rep_code(3));

    const tn = new TensorNetwork({
      legos: [
        new DroppedLego(
          {
            type_id: "zero",
            name: "Zero",
            short_name: "0",
            description: "Zero",
            parity_check_matrix: zero.getMatrix(),
            logical_legs: [],
            gauge_legs: []
          },
          new LogicalPoint(0, 0),
          "0"
        ),
        new DroppedLego(
          {
            type_id: "z_rep_code",
            name: "Z Rep Code",
            short_name: "Z3",
            description: "Z Rep Code",
            parity_check_matrix: z3.getMatrix(),
            logical_legs: [],
            gauge_legs: []
          },
          new LogicalPoint(0, 0),
          "1"
        )
      ],
      connections: []
    });
    const conjoined = tn.conjoin_nodes();
    expect(conjoined.h).toEqual(new GF2([[0]]));
  });
});
