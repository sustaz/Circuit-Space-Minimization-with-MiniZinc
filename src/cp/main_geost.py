import time
from minizinc import Instance, Model, Solver
import matplotlib
import matplotlib.pyplot as plt
from random import randint
import signal
from pathlib import Path
import os

# Get the current working directory
cwd = str(Path(Path(os.getcwd()).parent).parent)

plot_flag = False

def handler(signum, frame):
    print("Time is out!")
    raise Exception

def join_separator(vector, separator):
    vector = ''.join([str(ele) + separator for ele in vector])
    vector = vector[: len(vector) - len(separator)]
    vector = vector.replace("(", "")
    vector = vector.replace(")", "")
    return '[' + separator + vector + separator + ']'

for i in range(1, 41):
    try:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(5*60)

        with open(cwd + '/instances/ins-{num}.txt'.format(num=i)) as f:
            lines = f.readlines()
        lines_r = [''] * len(lines)
        piece_width = [0] * (int(len(lines)) - 2)
        piece_height = [0] * (int(len(lines)) - 2)
        tot_area = 0
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
                tot_area += piece_width[j - 2] * piece_height[j - 2]
        rect_size = list()
        shape = list()
        # assigning the basic variables
        # Transform the variables into support ones for geost implementation
        rect_size = list(zip(piece_width, piece_height));
        in_shape = list()
        for j in range(0, len(rect_size)):
            if rect_size[j] not in shape:
                shape.append(rect_size[j])
            if ((rect_size[j][1], rect_size[j][0])) not in shape:
                shape.append((rect_size[j][1], rect_size[j][0]))

        for j in range(0, len(rect_size)):
            if rect_size[j][0] == rect_size[j][1]:
                in_shape.append('{' + str(1 + shape.index(rect_size[j])) + '}')
            else:
                in_shape.append('{' + str(1 + shape.index(rect_size[j])) + ',' + str(
                    1 + shape.index((rect_size[j][1], rect_size[j][0]))) + '}')

        shape_pass = ['{' + str(j) + '}' for j in range(1, len(shape) + 1)]
        shape_pass = str(shape_pass).replace("'", "")
        in_shape_pass = str(in_shape).replace("'", "")
        rect_offset = join_separator([(0, 0)] * len(shape), '|')
        rect_size_in = join_separator(shape,'|')
        lower_limit = int(tot_area / fixed_width);

        with open(cwd + '/src/cp/geost_data/data.dzn', 'a') as f:
            f.truncate(0)
            f.writelines('fixed_width = ' + str(fixed_width) + ';' + '\n')
            f.writelines('permut = ' + str(len(shape)) + ';' + '\n')
            f.writelines('in_shape = ' + str(in_shape_pass) + ';' + '\n')
            f.writelines('lower_limit = ' + str(lower_limit) + ';' + '\n')
            f.writelines('num_circuits = ' + str(num_circuits) + ';' + '\n')
            f.writelines('piece_height = ' + str(piece_height) + ';' + '\n')
            f.writelines('piece_width = ' + str(piece_width) + ';' + '\n')
            f.writelines('rect_offset = ' + str(rect_offset) + ';' + '\n')
            f.writelines('rect_size = ' + str(rect_size_in) + ';' + '\n')
            f.writelines('shape = ' + str(shape_pass) + ';' + '\n')
            f.close()

        ###### OUTPUT MODEL ##########
        # import minizinc model
        vlsi = Model("cp_geost.mzn")
        # instantiate gecode model
        gecode = Solver.lookup("gecode")
        instance = Instance(gecode, vlsi)
        timest = time.time()
        result=instance.solve()
        print(result)
        colors=[]
        res_kind = result['kind']
        timestamp = int((time.time() - timest) * 10000) / 10000
        print("The result is computed in : " , timestamp, " seconds\n")

        # Generate the txts results
        with open(cwd + '/out/cp/geost/ins-{num}.txt'.format(num=i), 'a') as f:
            f.truncate(0)
            f.writelines(str(fixed_width) + ' ' + str(result['plate_height']) + '\n')
            f.writelines(str(num_circuits) + '\n')
            for z in range(0, num_circuits):
                f.writelines(str(piece_width[z]) + ' ' + str(piece_height[z]) + ' ' +
                             str(result['position_x'][z]) + ' ' + str(result['position_y'][z]) + '\n')
            f.close()

        # Generate the time results
        with open(cwd + '/out/cp/geost/time/time-{num}.txt'.format(num=i), 'a') as f:
            f.truncate(0)
            f.writelines('The result is computed in : ' + str(timestamp) + ' seconds' + '\n')
            f.close()

        # Generate the plot
        x = result['position_x']
        y = result['position_y']

        if (plot_flag == True):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            for i in range(0, num_circuits):
                colors.append('#%06X' % randint(0, 0xFFFFFF))
                rect1 = matplotlib.patches.Rectangle((x[i], y[i]), piece_width[res_kind[i] - 1],
                                                     piece_height[res_kind[i] - 1], color=colors[i])
                ax.add_patch(rect1)
            plt.xlim([0, fixed_width])
            plt.ylim([0, result['plate_height']])
            plt.show()
            plt.close()




    except Exception as exp:
        print('Time is out!')
        continue;


