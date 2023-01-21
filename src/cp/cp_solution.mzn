%-- Import Libraries--
include "cumulative.mzn"; 
include "globals.mzn";
include "gecode.mzn";
include "lex_lesseq.mzn";

% -----Input Variables-----
array[OBJECTS] of int: piece_width; % number of handlers required  
array[OBJECTS] of int: piece_height; % required duration to move 
int: fixed_width;
int: num_circuits;
int: lower_limit;
set of int: OBJECTS = 1..num_circuits;

%-- Output Variables --
array[OBJECTS] of var 0..fixed_width: position_x; 
array[OBJECTS] of var 0..sum(piece_height): position_y; 
var lower_limit..sum(piece_height): plate_height ;


%-- Support Variables --
array[OBJECTS] of var 0..fixed_width: position_x_pi; 
array[OBJECTS] of var 0..sum(piece_height): position_y_pi; 
array[OBJECTS] of int : ordered_ob = sort_by(OBJECTS, [-piece_height[ob]*piece_width[ob] | ob in OBJECTS]); 


% ----- Global Constraint -----
constraint cumulative(position_x, piece_width, piece_height, plate_height); 
constraint cumulative(position_y, piece_height, piece_width, fixed_width); 

constraint diffn(position_x, position_y,piece_width, piece_height );

% ----- Constraint for domain reduction -------
constraint forall(o in OBJECTS)(position_y[o] + piece_height[o] <= plate_height); 
constraint forall(o in OBJECTS)(position_x[o] + piece_width[o] <= fixed_width); 

% Fix the biggest block in one of the four corners to reduce the domain

constraint (position_x[ordered_ob[1]] = 0  /\ position_y[ordered_ob[1]] = 0 )
          \/ (position_x[ordered_ob[1]] = 0  /\ position_y[ordered_ob[1]] = plate_height - piece_height[ordered_ob[1]] )
          \/ (position_x[ordered_ob[1]] = fixed_width - piece_width[ordered_ob[1]]  /\ position_y[ordered_ob[1]] = 0 )
          \/ (position_x[ordered_ob[1]] = fixed_width - piece_width[ordered_ob[1]]  /\ position_y[ordered_ob[1]] = plate_height - piece_height[ordered_ob[1]] )
  ;

% Symmetry breaking for vertical and horizontal flips

constraint forall(o in OBJECTS)((plate_height - piece_height[ordered_ob[o]] - position_y[ordered_ob[o]] == position_y_pi[ordered_ob[o]]) /\ 
                                 fixed_width - piece_width[ordered_ob[o]] - position_x[ordered_ob[o]] == position_x_pi[ordered_ob[o]]);

constraint lex_lesseq(position_x_pi, position_x) /\ lex_lesseq(position_y_pi, position_y);

% ---- Solve the problem minimizing the plate height ----
solve :: int_search([plate_height], dom_w_deg, indomain_min)
     
      %:: restart_luby(1000)
minimize plate_height ;

output [ "Sorted circuits = \(ordered_ob)\n"];
output  [ "Position of x axis = \(position_x)\n"]; 
output [ "Position of y axis = \(position_y)\n"]; 
output [ "The minimized height of the plate = \(plate_height)\n"];

