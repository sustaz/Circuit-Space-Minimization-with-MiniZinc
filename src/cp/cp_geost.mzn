include "diffn.mzn";
include "geost.mzn";
include "lex_lesseq.mzn";
include "geost_data/data.dzn";
% -- Input Variables --
int: num_circuits;
array[OBJECTS] of int: piece_width;
array[OBJECTS] of int: piece_height; 
int: fixed_width;
int: lower_limit;
int: permut;
set of int: PERMUT = 1..permut;
set of int: OBJECTS = 1..num_circuits;
array[PERMUT,1..2] of int: rect_size;
array[PERMUT,1..2] of 0..0: rect_offset;
array[int] of set of PERMUT: shape;
array[OBJECTS,1..2] of var int: coord;
array[OBJECTS] of var int: kind;
array[OBJECTS] of set of int: in_shape;
var lower_limit..sum(piece_width): plate_height;

% -- Output Variables --
array[OBJECTS] of var 0..fixed_width: position_x;
array[OBJECTS] of var 0..sum(piece_height): position_y;

% -- Support Variables --
array[OBJECTS] of var 0..fixed_width: position_x_pi;
array[OBJECTS] of var 0..sum(piece_height): position_y_pi;

% -- Constraint -- 
constraint forall (obj in OBJECTS)(
    kind[obj] in in_shape[obj]
);

array[OBJECTS] of int : ordered_ob = sort_by(OBJECTS, [-piece_height[ob]*piece_width[ob] | ob in OBJECTS]);

% Domain reduction constraint

constraint (position_x[ordered_ob[1]] = 0  /\ position_y[ordered_ob[1]] = 0 )
          \/ (position_x[ordered_ob[1]] = 0  /\ position_y[ordered_ob[1]] = plate_height - piece_height[ordered_ob[1]] )
          \/ (position_x[ordered_ob[1]] = fixed_width - piece_width[ordered_ob[1]]  /\ position_y[ordered_ob[1]] = 0 )
           \/ (position_x[ordered_ob[1]] = fixed_width - piece_width[ordered_ob[1]]  /\ position_y[ordered_ob[1]] = plate_height - piece_height[ordered_ob[1]] )
  ;

% symmetry breaking for vertical and horizontal flip
constraint forall(o in OBJECTS)((plate_height - piece_height[ordered_ob[o]] - position_y[ordered_ob[o]] == position_y_pi[ordered_ob[o]]) /\
                                 fixed_width - piece_width[ordered_ob[o]] - position_x[ordered_ob[o]] == position_x_pi[ordered_ob[o]]);

constraint lex_lesseq(position_x_pi, position_x) /\ lex_lesseq(position_y_pi, position_y);


% -- Instantiation of coord array as position x and y packed
constraint forall(i in OBJECTS) 
   (coord[i,1] = position_x[i] /\ coord[i,2] = position_y[i]);
   
constraint geost_bb(2, 
         rect_size, 
         rect_offset, 
         shape, 
         coord, 
         kind,
         [0,0],
         [fixed_width,plate_height]
         );   
        
solve ::
      int_search([plate_height], first_fail, indomain_random)

       :: restart_luby(100)
  

minimize plate_height;

% ----- EXECUTION ------
output ["l = \(plate_height);\nx = \(position_x);\ny = \(position_y);\nkind = \(kind);\ncoord = \(coord);\n "];



