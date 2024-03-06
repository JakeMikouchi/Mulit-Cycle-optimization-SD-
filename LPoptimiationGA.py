from turtle import pos
import numpy as np
import os
import shutil
import random
import time 
import copy
import multiprocessing
t1 = time.time()

# ---------------- Updates -------------------
# This going to be so much funnnnn

# 2/19/24
# first need to make sure that the code can create inputs
# old python doesn't allow f string ( f"hello_{name}" )
# super annoying
# Progress: 
#   all f strings have been changed
#   createChild now works for ANC inputs

# 2/20/24 
# something something I don't know who or where the fuck I am anymore
# confirmed that running removing the & will make the python sript wait until completion of cycle_iterations.py
# goal: add functionality to read outputs and look at fitness function

# 2/22/24
# wooooooooooooooooooo
# now reads anc iutputs and a preliminary fitness function was created

# 2/25/24
# Now the part I've REALLY been dreading
# goal: crossover 
# I think LP bounds needs to be adapted first

# 3/2/24 
# I think I'm going to change this to a SA algorithm instead, it makes more sense since we are starting from an already optimized solution and it might require less solutions
# implamented weighted random for assemblie slection instead of pure random b/c it would be stupid biased without
# making two different types of LP changes
    # 1) chaning the enrichment of a feed assembly
    # 2) swapping the location of an assembly 
# added a method of chooseing LP change types
# stupid diagonal fuck
# stuipid vertical fuck
# OKKKK I figured out all of the swaps and changes!!!!!

# 3/3/24 
# trying to round out some corners
# had to add functionality to change id_map and partner_map
# in the meantime, going to start the cooling schedule
# found something wrong with ANC I think prefix has to be changed after cy34. will investigate.
# need to make backup just for stupid anc just sitting there doing nothing

# 3/4/24
# found a way to ignore ANC when it does't work 
# I think all that's left is making the prabbility function 
# need to wait for alina to finish her 100% core

# 3/5/24
# goals:
# add in average enrichemnt for feed assemblies. This will add a positive value to fitness <---- maybe done?
# add in current best stuff <--- done except for probability function
# I think more ANC bullshit with id definitions. if an assembly is defined but not used <--- I think this is fixed, hard to tell. I'll run some tests and see
# it would be a good idea to actively delete all .out and .h files, track file should keep all relevant information



def fitness(minkeff, RodFDH, maxBoron, minBoron, Burnup, AverageEnrich):
    # Westinghouse Design constraints:
    
    # max cycle Boron: 2000 ppm
    # min eoc Boron: 10 ppm
    # max Burnup: 62000
    # max ARO Peaking factor: 1.550
    # max rodded peaking factor: 1.606

    if maxBoron > 2000:
        WMb = 1
    else: 
        WMb = 0

    if minBoron < 10:
        Wmb = 1
    else: 
        Wmb = 0

    if RodFDH > 1.606:
        WFDH = 400
    else:
        WFDH = 0

    if Burnup > 62000:
        WBU = 0.1
    else: 
        WBU = 0

    F = ((1/AverageEnrich)*1000)-WMb*(maxBoron-2000) + Wmb*(minBoron-10) - WBU*(Burnup-62000) - WFDH*(RodFDH-1.606)

    return F

def Cooling(InitialTemp, FinalTemp, TotalSol, Sol):

    # trigonometric additive cooling 
    # https://what-when-how.com/artificial-intelligence/a-comparison-of-cooling-schedules-for-simulated-annealing-artificial-intelligence/

    a = FinalTemp
    b = (InitialTemp - FinalTemp)/2
    c = (1 + np.cos((Sol * np.pi)/TotalSol))

    CurrentTemp = a + (b*c)

    return CurrentTemp

# def ProbabilityFunc():

def readLP(path):
    LP = []
    with open(os.getcwd()+"/"+path, "r") as file:
        #reads input file
        inp = file.readlines()
        keyword = 'FUE.TYP'
        # checks for lines with string "FUE.TYP" and stores the LP
        for line in inp:
            if line.find(keyword) != -1:
                row = line[15:49].split()
                row = list(map(int, row))
                LP.append(row)
    return LP

def LPBoundsInit(ChangeType, LP):
    # makes sure that random positions are within the bounds of the FA

    if ChangeType == "Change":     
        InitIdentiy = 0

        while InitIdentiy != 1:
        
            # weighted random b/c there would be a huge bias towards [0,0] otherwise
            Columns = [0, 1, 2, 3, 4, 5, 6]
            probabilities = [0.03, 0.1, 0.17, 0.17, 0.19, 0.17, 0.17]
            random_number = np.random.rand()
            cumulative_probability = 0

            # Iterate through columns and select one based on probabilities
            for column, probability in zip(Columns, probabilities):
                cumulative_probability += probability
                if random_number <= cumulative_probability:
                    Initpositions =  np.array([column])
                    break

            # Initpositions = np.random.randint(0,7,size=1)
            if Initpositions[0] == 0:
                Initpositions = np.append(Initpositions, np.random.randint(0,1))
            if Initpositions[0] == 1:
                Initpositions = np.append(Initpositions, np.random.randint(0,2))
            if Initpositions[0] == 2:
                Initpositions = np.append(Initpositions, np.random.randint(0,3))
            if Initpositions[0] == 3:
                Initpositions = np.append(Initpositions, np.random.randint(0,4))
            if Initpositions[0] == 4 :
                Initpositions = np.append(Initpositions, np.random.randint(0,5))
            if Initpositions[0] == 5 :
                Initpositions = np.append(Initpositions, np.random.randint(0,4))
            if Initpositions[0] == 6 :
                Initpositions = np.append(Initpositions, np.random.randint(0,2))
            
            if "FEED_" in LP[Initpositions[0]][Initpositions[1]]:
                InitIdentiy = 1
        
    else: 

        # weighted random b/c there would be a huge bias towards [0,0] otherwise
        Columns = [0, 1, 2, 3, 4, 5, 6]
        probabilities = [0.03, 0.1, 0.17, 0.17, 0.19, 0.17, 0.17]
        random_number = np.random.rand()
        cumulative_probability = 0

        # Iterate through columns and select one based on probabilities
        for column, probability in zip(Columns, probabilities):
            cumulative_probability += probability
            if random_number <= cumulative_probability:
                Initpositions =  np.array([column])
                break

        # Initpositions = np.random.randint(0,7,size=1)
        if Initpositions[0] == 0:
            Initpositions = np.append(Initpositions, np.random.randint(0,1))
        if Initpositions[0] == 1:
            Initpositions = np.append(Initpositions, np.random.randint(0,2))
        if Initpositions[0] == 2:
            Initpositions = np.append(Initpositions, np.random.randint(0,3))
        if Initpositions[0] == 3:
            Initpositions = np.append(Initpositions, np.random.randint(0,4))
        if Initpositions[0] == 4 :
            Initpositions = np.append(Initpositions, np.random.randint(0,5))
        if Initpositions[0] == 5 :
            Initpositions = np.append(Initpositions, np.random.randint(0,4))
        if Initpositions[0] == 6 :
            Initpositions = np.append(Initpositions, np.random.randint(0,2))

    return Initpositions

def LPBoundsSec(Initpositions, LP):
    # makes sure that random positions are within the bounds of the FA

    InitIdentiy = LP[Initpositions[0]][Initpositions[1]].strip()
    SecIndentify = LP[Initpositions[0]][Initpositions[1]].strip()

    # this is for off diagonal 
    if Initpositions[0] != Initpositions[1]:
        if Initpositions[1] != 0:
            while InitIdentiy == SecIndentify:
                # weighted random b/c there would be a huge bias towards [0,0] otherwise
                Columns = [2, 3, 4, 5, 6]
                probabilities = [0.15, 0.2, 0.25, 0.25, 0.15]
                random_number = np.random.rand()
                cumulative_probability = 0

                # Iterate through columns and select one based on probabilities
                for column, probability in zip(Columns, probabilities):
                    cumulative_probability += probability
                    if random_number <= cumulative_probability:
                        Secpositions = np.array([column])
                        break

                if Secpositions[0] == 2:
                    Secpositions = np.append(Secpositions, np.random.randint(1,2))
                if Secpositions[0] == 3:
                    Secpositions = np.append(Secpositions, np.random.randint(1,3))
                if Secpositions[0] == 4 :
                    Secpositions = np.append(Secpositions, np.random.randint(1,4))
                if Secpositions[0] == 5 :
                    Secpositions = np.append(Secpositions, np.random.randint(1,3))
                if Secpositions[0] == 6 :
                    Secpositions = np.append(Secpositions, 1)

                SecIndentify = LP[Secpositions[0]][Secpositions[1]].strip()

        # this is for the veritcal line
        if Initpositions[1] == 0:
            while InitIdentiy == SecIndentify:

                Secpositions = np.array([np.random.randint(0,7),0])
 
                SecIndentify = LP[Secpositions[0]][Secpositions[1]].strip()


    # This section is for the diagonal
    if Initpositions[0] == Initpositions[1]:
        while InitIdentiy == SecIndentify:
            # weighted random b/c there would be a huge bias towards [0,0] otherwise
            Columns = [0, 1, 2, 3, 4]
            probabilities = [0.2,0.2,0.2,0.2,0.2]
            random_number = np.random.rand()
            cumulative_probability = 0

            # Iterate through columns and select one based on probabilities
            for column, probability in zip(Columns, probabilities):
                cumulative_probability += probability
                if random_number <= cumulative_probability:
                    Secpositions = np.array([column,column])
                    break

            SecIndentify = LP[Secpositions[0]][Secpositions[1]].strip()
        
    return Secpositions


def createChild(Generation, Child, LP, FeedTypes):
    # makes a folder and transfers all the files
    os.mkdir("child_"+str(Generation)+"_"+str(Child))

    shutil.copy("../backup/cycle_iterations.py", "child_"+str(Generation)+"_"+str(Child))
    shutil.copy("Template.inp", "child_"+str(Generation)+"_"+str(Child))
    os.chdir("child_"+str(Generation)+"_"+str(Child))
    os.rename("Template.inp", "cycle_N_cy34.in")

    InLP = []
    # this checks which assembly types are in the LP
    for Row in LP:
        for Assembly in Row:
            if Assembly.strip() in FeedTypes and Assembly not in InLP:
                InLP.append(Assembly.strip())
                

    with open("cycle_N_cy34.in", "r") as file:
        data = file.readlines()
        file.close()

    comment_substring = "name =  #DoNOTRemove"
    for j, line in enumerate(data):
        if comment_substring in line:
            start_index = j + 1
            end_index = start_index + 7
            name_map_str = convert_to_original_format(LP)
            data[start_index:end_index] = name_map_str+"\n"

        if "partner = #DoNotRemove" in line:   
            start_index = j + 1
            end_index = start_index + 7
            Partner_map = replace_elements(LP)
            Partner_map_map_str = convert_to_original_format(Partner_map)
            data[start_index:end_index] = Partner_map_map_str+"\n"
        
        if "placement_specification_type = #DoNOTRemove" in line:
            start_index = j + 1
            end_index = start_index + 7
            id_map = replace_elements_id(LP)
            id_map_str = convert_to_original_format(id_map)
            data[start_index:end_index] = id_map_str+"\n"

        # this part is hard coded, it is not worth my time to figure out a way to make this better
            
        if "name	=	FEED_BX # DoNotRemove" in line and "FEED_BX" not in InLP:
            start_index = j - 1
            end_index = j + 6
            data[start_index:end_index] = "\n"

        if "name	=	FEED_A108X # DoNotRemove" in line and "FEED_A108X" not in InLP:
            start_index = j - 1
            end_index = j + 6
            data[start_index:end_index] = "\n"

        if "name	=	FEED_A1X # DoNotRemove" in line and "FEED_A1X" not in InLP:
            start_index = j - 1
            end_index = j + 6
            data[start_index:end_index] = "\n"
        

    with open("cycle_N_cy34.in", "w") as file:
        file.writelines(data)
    os.chdir("..")

def runANC(Generation, Child):
    # runs simulate 
    os.chdir("child_"+str(Generation)+"_"+str(Child))
    os.system("nohup python cycle_iterations.py > output.log 2>&1")
    # os.system("nohup python hehe_test.py > output.log 2>&1 ")
    os.chdir("..")

def readOutput(Generation, Child):
    os.chdir("child_"+str(Generation)+"_"+str(Child))
    current_directory = os.getcwd()
    # opens output file and reads each line
    cycles = ["cycle_N_cy34","cycle_35","cycle_36","cycle_37"]

    keff = []
    RodFDH = []
    #AROFDH = []
    Boron = []
    Burnup = []

    for i in range(len(cycles)):
        for filename in os.listdir(current_directory):
            if filename.startswith(cycles[i]) and filename.endswith(".out"):
                out_file = filename
        
        with open(out_file, "r") as file:
            data = file.readlines()
            for k, line in enumerate(data):
                if "SE-General         Summary of ANC Cases" in line:
                    ind = data.index(line)
                    for j in range(19):
                        keff.append(float(data[ind+j+5][27:35]))
                        Boron.append(float(data[ind+j+5][43:50]))
                        RodFDH.append(float(data[ind+j+5][84:90]))
                        # if j == 22: 
                            # AROFDH.append(float(data[ind+j+5][84:90]))
                if "SA-General" in line:
                    for j in range(121):
                        Burnup.append(float(data[k+j+5][171:177]))


    minkeff = min(keff)
    RodFDH = max(RodFDH)
    # AROFDH = max(AROFDH)
    maxBoron = max(Boron)
    minBoron = min(Boron)
    Burnup = max(Burnup)
    os.chdir("..")

    return minkeff, RodFDH, maxBoron, minBoron, Burnup

def optimizationTrack(RodFDH, maxBoron, minBoron, Burnup, fit, Generation, Population, NumErrors,CurrentTemp, AverageEnrich):
    # tracks optimization progress
    if Population == 0:
        with open('optimization_track.txt', 'w') as f:
            f.write('Optimization start \n')
            if RodFDH < 1.606 and maxBoron < 2000 and minBoron > 10 and Burnup < 62000:
                f.write("child_"+str(Generation)+"_"+str(Population)+":     FDH: "+str(RodFDH)+"     Max Boron: "+str(maxBoron)+"     Min Boron: "+str(minBoron)+"     Max Bunrup: "+str(Burnup)+"   fitness: "+str(fit)+"   Temp: "+str(CurrentTemp)+"   Average Enrichment: "+str(AverageEnrich)+"   Constraints Met\n")
            else: 
                f.write("child_"+str(Generation)+"_"+str(Population)+":     FDH: "+str(RodFDH)+"     Max Boron: "+str(maxBoron)+"     Min Boron: "+str(minBoron)+"     Max Bunrup: "+str(Burnup)+"   fitness: "+str(fit)+"   Temp: "+str(CurrentTemp)+"   Average Enrichment: "+str(AverageEnrich)+"   \n")
    else:
        with open('optimization_track.txt', 'a') as f:
            if RodFDH < 1.606 and maxBoron < 2000 and minBoron > 10 and Burnup < 62000:
                f.write("child_"+str(Generation)+"_"+str(Population)+":     FDH: "+str(RodFDH)+"     Max Boron: "+str(maxBoron)+"     Min Boron: "+str(minBoron)+"     Max Bunrup: "+str(Burnup)+"   fitness: "+str(fit)+"   Temp: "+str(CurrentTemp)+"   Average Enrichment: "+str(AverageEnrich)+"   Constraints Met\n")
            else: 
                f.write("child_"+str(Generation)+"_"+str(Population)+":     FDH: "+str(RodFDH)+"     Max Boron: "+str(maxBoron)+"     Min Boron: "+str(minBoron)+"     Max Bunrup: "+str(Burnup)+"   fitness: "+str(fit)+"   Temp: "+str(CurrentTemp)+"   Average Enrichment: "+str(AverageEnrich)+"   \n")
        f.close()

def TerminationTrack(Generation, Sol):
    if Sol ==0:
        with open('optimization_track.txt', 'w') as f:
            f.write("child_"+str(Generation)+"_"+str(Sol)+":    ANC error, run terminated \n")
    else: 
        with open('optimization_track.txt', 'a') as f:
            f.write("child_"+str(Generation)+"_"+str(Sol)+":    ANC error, run terminated \n")
    f.close()


def replace_elements(name_content, xy_map):
    for i in range(len(name_content)):
        for j in range(len(name_content[i])):
            if "FEED" not in name_content[i][j]:
                name_content[i][j] = xy_map[i][j]
    return name_content

def replace_elements_partner(name_content):
    Partner_map = [ ["", "", "", "", "", "", ""],
            ["", "", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", ""],
            ["", "", "", ""],
            ["", ""]]
    for i in range(len(name_content)):
        for j in range(len(name_content[i])):
            if i == 0 and j == 0:
                if "FEED" not in name_content[i][j]:
                    Partner_map[i][j] = "90"
            if i == 0 and j > 0:
                if "FEED" not in name_content[i][j]:
                    Partner_map[i][j] = ""
            else: 
                if "FEED" not in name_content[i][j]:
                    Partner_map[i][j] = "90"
            
    return Partner_map

def replace_elements_id(name_content):
    id_map = [ ["", "", "", "", "", "", ""],
            ["", "", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", ""],
            ["", "", "", ""],
            ["", ""]]
    for i in range(len(name_content)):
        for j in range(len(name_content[i])):
            if "FEED" in name_content[i][j]:
                id_map[i][j] = "id"
    
    return id_map

# converts the "name =" back into the correct format for the .in file
def convert_to_original_format(name_content):
    formatted_lines = []

    for inner_list in name_content:
        formatted_lines.append("                        "+", ".join(inner_list))


    original_format = "\n".join(formatted_lines)

    return original_format

def AssemblyPairs(position):
    # anny assembly on the left most column will not have a mirror
    if position[1] == 0:
        mirrorPos = position
    else:
        mirrorPos = [position[1],position[0]]
    return mirrorPos
    
def LPChangeType():
    # decides wich method of change to use
    Type = ""
    RandType = random.uniform(0, 1)
    if RandType < 0.4: # can change this number depending on how we want to optimize
        Type = "Swap"
    else:
        Type = "Change"
    return Type

def LPChange(ChangeType,LP):
    # manipulates the assembly for the change type
    if ChangeType == "Change":
        Initpositions = LPBoundsInit("Change", LP)
        mirrorPos = AssemblyPairs(Initpositions)
        oldAssembly = LP[Initpositions[0]][Initpositions[1]].strip()
        newAssembly = copy.deepcopy(oldAssembly)


        while oldAssembly == newAssembly:
            AssemblyType = random.randint(0,len(FeedTypes)-1)
            newAssembly = FeedTypes[AssemblyType]

            
        LP[Initpositions[0]][Initpositions[1]] = newAssembly
        LP[mirrorPos[0]][mirrorPos[1]] = newAssembly
   

    # maniuplates the assembly for the swap type
    if ChangeType == "Swap":
        Initpositions = LPBoundsInit("Swap", LP)
        Secpositions = LPBoundsSec(Initpositions, LP)
        mirrorPos1 =  AssemblyPairs(Initpositions)
        mirrorPos2 =  AssemblyPairs(Secpositions)

        Assembly1 =  LP[Initpositions[0]][Initpositions[1]] 
        Assembly2 = LP[Secpositions[0]][Secpositions[1]] 
        MirrorAssembly1 = LP[mirrorPos1[0]][mirrorPos1[1]]
        MirrorAssembly2 = LP[mirrorPos2[0]][mirrorPos2[1]]

        LP[Initpositions[0]][Initpositions[1]] = Assembly2
        LP[Secpositions[0]][Secpositions[1]] = Assembly1
        LP[mirrorPos1[0]][mirrorPos1[1]] =   MirrorAssembly2    
        LP[mirrorPos2[0]][mirrorPos2[1]] = MirrorAssembly1

    return LP
    

def EnrichAVG(LP, FeedTypes):
    # this will be somewhat hard coded
    # this checks which assembly types are in the LP
    FEED_BX = 0
    FEED_A108X = 0
    FEED_A1X = 0
    for Row in LP:
        for Assembly in Row:
            if Assembly.strip() in FeedTypes:
                if Assembly.strip() == "FEED_BX":
                    FEED_BX += 1
                if Assembly.strip() == "FEED_A108X":
                    FEED_A108X += 1
                if Assembly.strip() == "FEED_A1X":
                    FEED_A1X += 1

    averageEnrich = ((FEED_BX * 4.8) + (FEED_A108X * 4.95) + (FEED_A1X * 4.95))/(FEED_A1X+FEED_A108X+FEED_BX)
    
    return averageEnrich


def SAStart():
    with open("Initial_Parent1/cycle_N_cy34.in", "r") as file:
        data = file.readlines()
        file.close()

    comment_substring = "name =  #DoNOTRemove"
    for j, line in enumerate(data):
        if comment_substring in line:
            start_index = j + 1
            end_index = start_index + 7
            name_map=[x.strip().split(',') for x in data[start_index:end_index]]
    
    return name_map

def SolutionCheck(Generation, Population):
    Errors = 0
    if os.path.exists("child"+"_"+str(Generation)+"_"+str(Population)+"/cycle_N_cy34.h5") == False:
        Errors = 1
    if os.path.exists("child"+"_"+str(Generation)+"_"+str(Population)+"/cycle_35.h5") == False:
        Errors = 1
    if os.path.exists("child"+"_"+str(Generation)+"_"+str(Population)+"/cycle_36.h5") == False:
        Errors = 1
    if os.path.exists("child"+"_"+str(Generation)+"_"+str(Population)+"/cycle_37.h5") == False:
        Errors = 1
    if os.path.exists("child"+"_"+str(Generation)+"_"+str(Population)+"/cycle_38.h5") == False:
        Errors = 1
    return Errors

def deleteSol(Generation,Child):
    os.chdir("child_"+str(Generation)+"_"+str(Child))
    current_directory = os.getcwd()
    for filename in os.listdir(current_directory):
        if filename.endswith(".out"):
            os.remove(filename)
        if filename.endswith(".h5"):
            os.remove(filename)  
        if filename.endswith(".log"):
            os.remove(filename)

    os.chdir("..")

def BestLPTrack(Generation,Sol):
    if Sol ==0:
        with open('Best_Track.txt', 'w') as f:
            f.write("child_"+str(Generation)+"_"+str(Sol)+"\n")
    else: 
        with open('Best_Track.txt', 'a') as f:
            f.write("child_"+str(Generation)+"_"+str(Sol)+"\n")
    f.close()




xy_map =  [ ["7_7", "", "", "", "", "", ""],
            ["7_8", "8_8", "9_8", "10_8", "11_8", "12_8", "13_8"],
            ["7_9", "8_9", "9_9", "10_9", "11_9", "12_9"],
            ["7_10", "8_10", "9_10", "10_10", "11_10", "12_10"],
            ["7_11", "8_11", "9_11", "10_11", "11_11"],
            ["7_12", "8_12", "9_12", "10_12"],
            ["7_13", "8_13"]]


FeedTypes = ["FEED_BX", "FEED_A108X",  "FEED_A1X"]

NumErrors = 0

InitialTemp = 500
FinalTemp = 10
CurrentTemp = InitialTemp
TotalSol= 25

OGLP = SAStart()
NewLP = copy.deepcopy(OGLP) 
OGFit = -100000000
NewFit = -1000000

BestLP = copy.deepcopy(OGLP) 
BestFit =  NewFit
BestLPTrack(0,0)


if __name__ == '__main__':
    for Sol in range(TotalSol):
        # generates the LP change type and creates the new LP


        if Sol > 0:
            ChangeType = LPChangeType()
            NewLP = LPChange(ChangeType,OGLP)

        # creates input and runs ANC
        createChild(0, Sol, NewLP, FeedTypes)

        p = multiprocessing.Process(target=runANC, args=(0, Sol))
        # runANC(0,Sol)
        p.start()
        p.join(1800)

        # this is to make sure ANC actually worked

        # there are 3 situations
        # anc runs properly
        # anc does nothing and never completes
        # anc runs with error and general_se_general.txt is created
        if os.path.exists("child"+"_"+str(0)+"_"+str(Sol)+"/general_se_general.txt") == False:
            # kills process if it's taking too long 
            p.terminate()
            p.join()
            TerminationTrack(0, Sol)


        elif os.path.exists("child"+"_"+str(0)+"_"+str(Sol)+"/general_se_general.txt") and int(os.path.getsize("child"+"_"+str(0)+"_"+str(Sol)+"/general_se_general.txt")) < 5000:
            # makes sure no errors if anc doesn't work
            TerminationTrack(0, Sol)

        else:  
            # post processing of LP
            minkeff, RodFDH, maxBoron, minBoron, Burnup = readOutput(0, Sol)
            AverageEnrich = EnrichAVG(NewLP, FeedTypes)
            fit = fitness(minkeff, RodFDH, maxBoron, minBoron, Burnup, AverageEnrich)
            optimizationTrack(RodFDH, maxBoron, minBoron, Burnup, fit, 0, Sol, NumErrors, CurrentTemp, AverageEnrich)

            NewFit = fit

            if NewFit > BestFit:
                BestFit = NewFit
                BestLP = copy.deepcopy(NewLP)
                BestLPTrack(0,Sol)

            # space reserved for probabilty function

            OGLP = copy.deepcopy(NewLP)
            OGFit = NewFit

        # updates temperature value


        CurrentTemp = Cooling(InitialTemp, FinalTemp, TotalSol, Sol+1)
        deleteSol(0,Sol)


with open('optimization_track.txt', 'a') as f:
    f.write("Optimization Complete \n")
