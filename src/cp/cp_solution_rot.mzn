include "cumulative.mzn"; 
include "globals.mzn";

% -----Input Variables -----
int: num_circuits; 
set of int: OBJECTS = 1..num_circuits;
array[OBJECTS] of int: piece_width;
array[OBJECTS] of int: piece_height;
int: fixed_width;
int: lower_limit;

% -- Output Variables --
array[OBJECTS] of var 0..fixed_width: position_x;
array[OBJECTS] of var 0..sum(piece_height): position_y;
var lower_limit..sum(piece_height): plate_height;

%-- Support Variables --
array[OBJECTS] of var 0..fixed_width: position_x_pi;
array[OBJECTS] of var 0..sum(piece_height): position_y_pi;
array[OBJECTS] of int : ordered_ob = sort_by(OBJECTS, [-piece_height[ob]*piece_width[ob] | ob in OBJECTS]);
array [1..num_circuits] of var 0..1 : rotation;
array[1..num_circuits] of var 0..max([max(piece_width),max(piece_height)]): piece_width_rotation;
array[1..num_circuits] of var 0..max([max(piece_width),max(piece_height)]): piece_height_rotation;

% -- Rotation Constraints --  
constraint forall(o in OBJECTS)(piece_height_rotation[o] = piece_height[o]* (1- rotation[o] ) + piece_width[o]*rotation[o]);
constraint forall(o in OBJECTS)(piece_width_rotation[o] = piece_width[o]*(1- rotation[o] ) + piece_height[o]*rotation[o]);
constraint forall(o in OBJECTS)(if piece_height[o] == piece_width[o] then (rotation[o] = 0)endif);

% ----- Global Constraints -----
constraint cumulative(position_x, piece_width_rotation, piece_height_rotation, plate_height);
constraint cumulative(position_y, piece_height_rotation, piece_width_rotation, fixed_width);
constraint diffn(position_x, position_y,piece_width_rotation, piece_height_rotation);

% ----- Domain Reduction -------
constraint forall(o in OBJECTS)(position_y[o] + piece_height_rotation[o] <= plate_height);
constraint forall(o in OBJECTS)(position_x[o] + piece_width_rotation[o] <= fixed_width);

constraint (position_x[ordered_ob[1]] = 0  /\ position_y[ordered_ob[1]] = 0 )

          \/ (position_x[ordered_ob[1]] = 0  /\ position_y[ordered_ob[1]] = plate_height -piece_height_rotation[ordered_ob[1]] )

          \/ (position_x[ordered_ob[1]] = fixed_width - piece_width_rotation[ordered_ob[1]]  /\ position_y[ordered_ob[1]] = 0 )

          \/ (position_x[ordered_ob[1]] = fixed_width - piece_width_rotation[ordered_ob[1]]  /\ position_y[ordered_ob[1]] = 
              plate_height - piece_height_rotation[ordered_ob[1]] );

% symmetry breaking for vertical and horizontal flips
constraint forall(o in OBJECTS)((plate_height - piece_height_rotation[o] - position_y[o] == position_y_pi[o]) /\
                                 fixed_width - piece_width_rotation[o] - position_x[o] == position_x_pi[o]);

constraint lex_lesseq(position_x_pi, position_x) /\ lex_lesseq(position_y_pi, position_y);

solve
  :: seq_search([
      int_search([plate_height], dom_w_deg, indomain_min),
      int_search(rotation, first_fail, indomain_min)
  ])
  %:: restart_luby(1000)
   minimize plate_height ;

% ----- EXECUTION ------
output [ "Position of x axis = \(position_x)\n"]; 
output [ "Position of y axis = \(position_y)\n"];
output [ "ORDERED ARRAY = \(position_y)\n"];
output [ "The minimized height of the plate = \(plate_height)\n"];
output [ "PERMUTATION = \(rotation)\n"];