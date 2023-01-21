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
plot_flag=False #Flag to print the plot if setted on True

""" Definition of some used functions """

# handle the timeout (set to 5 minutes)
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

        # Import instances
        with open(cwd + '/instances/ins-{num}.txt'.format(num=k)) as f:
            lines = f.readlines()

        """ Input variables """
        lines_r = [''] * len(lines)
        piece_width = [0] * (int(len(lines)) - 2)
        piece_height = [0] * (int(len(lines)) - 2)
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
                piece_width[j - 2] = int(lines_r[j].split(" ")[0])
                piece_height[j - 2] = int(lines_r[j].split(" ")[1])
                area[j - 2] = piece_width[j - 2] * piece_height[j - 2]
        # compute the lower limit
        lower_limit = sum(area) / fixed_width
        smt = Optimize();
        biggest_c = area.index(max(area))

        """ Output variables """
        position_x = IntVector('position_x', num_circuits)
        position_y = IntVector('position_y', num_circuits)
        plate_height = Int('plate_height')

        """ Support variables """
        position_x_pi = IntVector('position_x', num_circuits)
        position_y_pi = IntVector('position_y', num_circuits)

        """ Definition of the rules """
        smt.add(num_circuits == num_circuits)
        smt.add(fixed_width == fixed_width)

        # DOMAIN REDUCTION RULES
        dom = And(position_x[biggest_c] == 0, position_y[biggest_c] == 0)
        smt.add(dom)
        smt.add(plate_height >= lower_limit)

        for i in range(0, num_circuits):

            # BOUNDARIES RULES
            a = position_x[i] >= 0
            b = position_x[i] + piece_width[i] <= fixed_width
            c = position_y[i] >= 0
            d = position_y[i] + piece_height[i] <= plate_height
            smt.add(And(a, b, c, d))

            # Generate the arrays for symmetry breaking
            position_x_pi[i] = fixed_width - piece_width[i] - position_x[i]
            position_y_pi[i] = plate_height - piece_height[i] - position_y[i]

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

        """ Minimization of the objective function """
        # Minimization function definition
        timestamp = time.time() # time before the minimization
        h = smt.minimize(plate_height)
        smt.check()
        smt.model()

        timer = str((time.time() - timestamp))
        print(" For the problem with ",num_circuits, " pieces "
              " and given fixed width :", fixed_width, " \n "
              "the minimized plate height is : ", h.value(), "\n",
              " in : " ,timer, "seconds!")

        """ Compute output  """
        x = [0] * (int(len(lines)) - 2)
        y = [0] * (int(len(lines)) - 2)


        # Getting the computed positions
        for j in range(0, num_circuits):
            x[j] = smt.model()[position_x[j]]
            y[j] = smt.model()[position_y[j]]

        # Generate the time results
        with open( cwd + '/out/smt/smt_vanilla/time/time-{num}.txt'.format(num=k), 'a') as f:
            f.truncate(0)
            f.writelines('The result is computed in : ' + timer + ' seconds' + '\n')
            f.close()

        # Generate the output results
        with open(cwd + '/out/smt/smt_vanilla/ins-{num}.txt'.format(num=k), 'a') as f:
            f.truncate(0)
            f.writelines(str(fixed_width) + ' ' +  str(h.value()) + '\n')
            f.writelines(str(num_circuits) + '\n')
            for z in range(0,num_circuits):
                f.writelines(str(piece_width[z]) + ' ' + str(piece_height[z]) + ' ' +
                             str(x[z]) + ' ' + str(y[z]) + '\n')
            f.close()
        colors = []

        """ Plot solutions """
        fig = plt.figure()
        ax = fig.add_subplot(111)

        if(plot_flag==True):
            for i in range(0, num_circuits):
                colors.append('#%06X' % randint(0, 0xFFFFFF))

                rect1 = matplotlib.patches.Rectangle((int(str(x[i])), int(str(y[i]))), piece_width[i], piece_height[i],
                                                         color=colors[i])
                ax.add_patch(rect1)
            plt.xlim([0, fixed_width])
            plt.ylim([0, (int(str(h.value())))])
            plt.show()

    except Exception as exp:
        print("Time is out!")
        continue;