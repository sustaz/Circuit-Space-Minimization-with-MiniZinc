from z3 import *
import matplotlib
import matplotlib.pyplot as plt
from random import randint
import time
import signal
from pathlib import Path
# Import the os module
import os

# Get the current working directory
cwd = str(Path(Path(os.getcwd()).parent).parent)
plot_flag = False

""" Definition of some used functions """
def handler(signum, frame):
    print("Time is out!")
    raise Exception

# lexicographic order between two arrays recursive function
def lex_lesseq(pos, pos_pi):
    if not pos:
        return True
    if not pos_pi:
        return False
    return Or(pos[0] < pos_pi[0], And(pos[0] == pos_pi[0], lex_lesseq(pos[1:], pos_pi[1:])))

for k in range(1, 41):
    try:

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(60*5)

        with open(cwd + '/instances/ins-{num}.txt'.format(num=k)) as f:
            lines = f.readlines()

        """ Input variables """
        lines_r = [''] * len(lines)
        piece_width_r = [0] * (int(len(lines)) - 2)
        piece_height_r = [0] * (int(len(lines)) - 2)
        area = [0] * (int(len(lines)) - 2)

        for j in range(0, len(lines) - 1):
            lines_r[j] = lines[j].replace("\n", "")
            lines_r[j + 1] = lines[j + 1].replace("\n", "")
        for j in range(0, len(lines)):
            if j == 0:
                fixed_width = int(lines_r[j])
            elif j == 1:
                num_circuits = int(lines_r[j])
            else:
                piece_width_r[j - 2] = int(lines_r[j].split(" ")[0])
                piece_height_r[j - 2] = int(lines_r[j].split(" ")[1])
                area[j - 2] = piece_width_r[j - 2] * piece_height_r[j - 2]

        # compute the lower limit
        lower_limit = sum(area) / fixed_width
        smt = Optimize();
        biggest_c = area.index(max(area))

        """ Output variables """
        position_x = IntVector('position_x', num_circuits)
        position_y = IntVector('position_y', num_circuits)
        plate_height = Int('plate_height')

        """ Support Variables """
        position_x_pi = IntVector('position_x', num_circuits)
        position_y_pi = IntVector('position_y', num_circuits)
        rotation = IntVector('rotation', num_circuits)
        piece_width = IntVector('piece_width', num_circuits);
        piece_height = IntVector('piece_height', num_circuits);

        """ Definition of the rules """
        smt.add(num_circuits == num_circuits)
        smt.add(fixed_width == fixed_width)  # GIUSTA SINTASSI
        timer = time.time()

        # DOMAIN REDUCTION RULES
        dom = And(position_x[biggest_c] == 0, position_y[biggest_c] == 0)

        smt.add(dom)

        # LOWER LIMIT RULE
        smt.add(plate_height>=lower_limit)

        for i in range(0, num_circuits):

            # Generate the arrays for symmetry breaking
            position_x_pi[i] = fixed_width - piece_width[i] - position_x[i]
            position_y_pi[i] = plate_height - piece_height[i] - position_y[i]

            # ROTATION RULES
            smt.add(Implies(piece_height_r[i] == piece_width_r[i], rotation[i] == 0))

            smt.add(Implies(piece_height_r[i] != piece_width_r[i], Or(rotation[i] == 0, rotation[i] == 1)))
            smt.add(
                Implies(rotation[i] == 0, And(piece_width[i] == piece_width_r[i], piece_height[i] == piece_height_r[i])))
            smt.add(
                Implies(rotation[i] == 1, And(piece_width[i] == piece_height_r[i], piece_height[i] == piece_width_r[i])))

            # BOUNDARIES RULES
            a = position_x[i] >= 0
            b = position_x[i] + piece_width[i] <= fixed_width
            c = position_y[i] >= 0
            d = position_y[i] + piece_height[i] <= plate_height
            smt.add(And(a, b, c, d))

            for j in range(i + 1, num_circuits):

                # NON-OVERLAPPING RULES
                s1 = position_x[j] + piece_width[j] <= position_x[i]
                s2 = position_y[j] + piece_height[j] <= position_y[i]
                s3 = position_x[j] >= position_x[i] + piece_width[i]
                s4 = position_y[j] >= position_y[i] + piece_height[i]

                total = Or(s1, s2, s3, s4)

                smt.add(total)

        # Symmetry breaking rule
        smt.add(And(lex_lesseq(position_x_pi, position_x), lex_lesseq(position_y_pi, position_y)))

        timestamp = time.time()  # time before the minimization

        # OBJECTIVE FUNCTION
        h = smt.minimize(plate_height)

        # Defining the minimization function
        smt.check()
        smt.model()

        """ Compute output  """
        rotation_vector = list()
        timer = str((time.time() - timestamp))
        print(" For the problem with ",num_circuits, " pieces "
              " and given fixed width :", fixed_width, " \n "
              "the minimized plate height is : ", h.value(), "\n",
              " in : " ,( timer), "seconds!")
        for i in range(0,len(rotation)):
             rotation_vector.append(smt.model()[rotation[i]])

        print("The rotation vector is ", rotation_vector, "\n")

        x = [0] * (int(len(lines)) - 2)
        y = [0] * (int(len(lines)) - 2)

        # Getting the computed positions
        for j in range(0, num_circuits):
            x[j] = smt.model()[position_x[j]]
            y[j] = smt.model()[position_y[j]]

        # Generate the time results
        with open(cwd + '/out/smt/smt_rot/time-{num}.txt'.format(num=k), 'a') as f:
            f.truncate(0)
            f.writelines('The result is computed in : ' + str(timer) + ' seconds' + '\n')
            f.close()

        # Generate the output results
        with open(cwd + '/out/smt/smt_rot/ins-{num}.txt'.format(num=k), 'a') as f:
            f.truncate(0)
            f.writelines(str(fixed_width) + ' ' + str(h.value()) + '\n')
            f.writelines(str(num_circuits) + '\n')
            for z in range(0, num_circuits):
                f.writelines(str(piece_width_r[z]) + ' ' + str(piece_height_r[z]) + ' ' +
                             str(x[z]) + ' ' + str(y[z]) + '\n')
            f.close()

        colors = []

        """ Plot solutions """
        if (plot_flag == True):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            for i in range(0, num_circuits):
                colors.append('#%06X' % randint(0, 0xFFFFFF))
                if (int(str(smt.model()[rotation[i]])) == 1):
                    rect1 = matplotlib.patches.Rectangle((int(str(x[i])), int(str(y[i]))), piece_height_r[i], piece_width_r[i],
                                                         color=colors[i])
                elif (int(str(smt.model()[rotation[i]])) == 0):
                    rect1 = matplotlib.patches.Rectangle((int(str(x[i])), int(str(y[i]))), piece_width_r[i], piece_height_r[i],
                                                         color=colors[i])
                ax.add_patch(rect1)
            plt.xlim([0, fixed_width])
            plt.ylim([0, (int(str(h.value())))])
            plt.show()

    except Exception as exp:
        print("Time is out!")
        continue;