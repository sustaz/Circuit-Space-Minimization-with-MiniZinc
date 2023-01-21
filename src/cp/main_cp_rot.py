from minizinc import Instance, Model, Solver
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
plot_flag = True

def handler(signum, frame):
    print("Time is out!")
    raise Exception

for i in range(1,41):
    try:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(5*60)

        with open(cwd + '/instances/ins-{num}.txt'.format(num = i)) as f:
            lines = f.readlines()
        lines_r = [''] * len(lines)
        piece_width = [0] * (int(len(lines))-2)
        piece_height = [0] * (int(len(lines))-2)
        tot_area=0
        for j in range(0, len(lines)-1):
          lines_r[j] = lines[j].replace("\n", "")
          lines_r[j+1] = lines[j+1].replace("\n", "")
        for j in range(0, len(lines)):
          if j == 0:
            fixed_width = int(lines_r[j])
          elif j == 1:
            num_circuits = int(lines_r[j])
          else:
            piece_width[j-2] = int(lines_r[j].split(" ")[0])
            piece_height[j-2] = int(lines_r[j].split(" ")[1])
            tot_area += piece_width[j-2] * piece_height[j-2]

        ###### OUTPUT MODEL ##########
        # import minizinc model
        vlsi = Model("cp_solution_rot.mzn")
        # instantiate gecode model
        gecode = Solver.lookup("gecode")
        instance = Instance(gecode, vlsi)

        # assign the variables
        instance["num_circuits"] = num_circuits;
        instance["piece_width"] = piece_width;
        instance["piece_height"] = piece_height;
        instance["fixed_width"]  = fixed_width;
        instance["lower_limit"]  = int(tot_area/fixed_width);

        print("Fixed width= ", fixed_width ,'\n');


        # print the results you want to analyze
        timest = time.time()

        # print the results you want to analyze
        result = instance.solve()
        colors = []
        print(result)
        timestamp = int((time.time() - timest) * 10000) / 10000
        print("The result is computed in : ", timestamp, " seconds\n")

        colors=[]
        x = result['position_x']
        y = result['position_y']

        # Generate the txts results
        with open(cwd + '/out/cp/cp_rot_ann/ins-{num}.txt'.format(num=i), 'a') as f:
            f.truncate(0)
            f.writelines(str(fixed_width) + ' ' + str(result['plate_height']) + '\n')
            f.writelines(str(num_circuits) + '\n')
            for z in range(0, num_circuits):
                f.writelines(str(piece_width[z]) + ' ' + str(piece_height[z]) + ' ' +
                             str(result['position_x'][z]) + ' ' + str(result['position_y'][z]) + '\n')
            f.close()

        # Generate the time results
        with open(cwd + '/out/cp/cp_rot_ann/time/time-{num}.txt'.format(num=i), 'a') as f:
            f.truncate(0)
            f.writelines('The result is computed in : ' + str(timestamp) + ' seconds' + '\n')
            f.close()

        ########### PLOT ###########
        if (plot_flag == True):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            for i in range(0,num_circuits):
                colors.append('#%06X' % randint(0, 0xFFFFFF))
                if (result['rotation'][i]==True):
                    rect1 = matplotlib.patches.Rectangle((x[i], y[i]),piece_height[i] , piece_width[i], color=colors[i])
                else:
                    rect1 = matplotlib.patches.Rectangle((x[i], y[i]), piece_width[i], piece_height[i], color=colors[i])
                ax.add_patch(rect1)
            plt.xlim([0, fixed_width])
            plt.ylim([0, result['plate_height']])
            plt.show()

    except Exception as exp:
        continue;



