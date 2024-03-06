import shutil 
import os
import time



all_cycles = ["bw_cycle32","cycle_n-1_cy33","cycle_N_cy34","cycle_35","cycle_36","cycle_37"]

new_cycles = ["cycle_N_cy34","cycle_35","cycle_36","cycle_37"]

new_cycles_identifier = ["34", "35", "36", "37"]

current_directory = os.getcwd()


xy_map = [  ["7_7", "", "", "", "", "", ""],
            ["7_8", "8_8", "9_8", "10_8", "11_8", "12_8", "13_8"],
            ["7_9", "8_9", "9_9", "10_9", "11_9", "12_9"],
            ["7_10", "8_10", "9_10", "10_10", "11_10", "12_10"],
            ["7_11", "8_11", "9_11", "10_11", "11_11"],
            ["7_12", "8_12", "9_12", "10_12"],
            ["7_13", "8_13"]]



# this creates the input files
def file_edit(new_file, current, past, past2, identifier):
    identifier_num = int(identifier)

    with open(new_file,"r") as f:
        file = f.readlines()

    for j, line in enumerate(file):
        
        if "model_file" in line:
            file[j] = "            model_file =  ./"+current+".h5 \n"
        if "secondary_file = /usr1/westinghouse/boundary_waters/cycle_n-1_cy33.h5" in line:
            file[j] = "                secondary_file = ./"+past+".h5 \n"
        if "secondary_file = /usr1/westinghouse/boundary_waters/bw_cycle32.h5" in line:
            if past2 == "cycle_n-1_cy33":
                file[j] = "                secondary_file = /usr1/westinghouse/boundary_waters/"+past2+".h5 \n"
            else: 
                file[j] = "                secondary_file = ./"+past2+".h5 \n"
        if "NSP34" in line:
            file[j] = line.replace("NSP34", "NSP"+identifier)
        if "NSP33" in line:
            identifier_num1 = identifier_num-1
            file[j] = line.replace("NSP33", "NSP"+str(identifier_num1))
        if "BW32___NW" in line:
            identifier_num2 = identifier_num-2
            file[j] = line.replace("BW32___NW", "NSP"+str(identifier_num2)+"__EOC")
        if "number = 34" in line:
            file[j] = line.replace("number = 34", "number = "+identifier)
        if "Boundary Waters Cycle 34 Model" in line:
            file[j] = line.replace("34", identifier)
        if "default_previous_cycle = 33" in line:
            file[j] = line.replace("33", str(identifier_num1))

        if line.strip() == "previous_cycle =":
            del file[j:j+8]

        comment_substring = "name =  #DoNOTRemove"
        if comment_substring in line:
            start_index = j + 1
            end_index = start_index + 7
            Partner_map=[x.strip().split(',') for x in file[start_index:end_index]]
            id_map = replace_elements_id(Partner_map)
            Partner_map = replace_elements(Partner_map)
            Partner_map_map_str = convert_to_original_format(Partner_map)
            id_map_str = convert_to_original_format(id_map)

        if "partner = #DoNotRemove" in line:   
            start_index = j + 1
            end_index = start_index + 7
            file[start_index:end_index] = Partner_map_map_str+"\n"
        
        if "placement_specification_type = #DoNOTRemove" in line:
            start_index = j + 1
            end_index = start_index + 7
            file[start_index:end_index] = id_map_str+"\n"


        if "prefix=A" in line:
            file[j] = line.replace("A", "A"+str(identifier))
        if "prefix=B" in line:
            file[j] = line.replace("B", "B"+str(identifier))
        if "prefix=C" in line:
            file[j] = line.replace("C", "C"+str(identifier))

    with open(new_file,"w") as f:
        f.writelines(file)

# # this changes "name =" for all cycles > 34
# def replace_elements(name_content, xy_map):
#     for i in range(len(name_content)):
#         for j in range(len(name_content[i])):
#             if "FEED" not in name_content[i][j]:
#                 name_content[i][j] = xy_map[i][j]
#     return name_content
        
# this changes "name =" for all cycles > 34
def replace_elements(name_content):
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


# this checks if the current run is finished 
def check_run(out_file):
    Run_done = False
    check = False
    while Run_done == False:
        with open(out_file,"r") as f:
            file = f.readlines()
            last_lines = file[-5:]
        
        for line in last_lines:
            if "=== ANC execution complete ===" in line:
                check = True
        Run_done = check

        if Run_done == False:
            time.sleep(30)


def FirstRunChange(new_file):

    with open(new_file,"r") as f:
        file = f.readlines()

    for j, line in enumerate(file):

        comment_substring = "name =  #DoNOTRemove"
        if comment_substring in line:
            start_index = j + 1
            end_index = start_index + 7
            Partner_map=[x.strip().split(',') for x in file[start_index:end_index]]
            Partner_map = replace_elements(Partner_map)
            Partner_map_map_str = convert_to_original_format(Partner_map)

        if "partner = # DoNotRemove" in line:   
            start_index = j + 1
            end_index = start_index + 7 
            file[start_index:end_index] = Partner_map_map_str+"\n"


    with open(new_file,"w") as f:
        f.writelines(file)

# this iterates through the 8 cycles
for i in range(len(new_cycles)):
    if i > 0:
        first_file = new_cycles[0]+".in"
        new_file = new_cycles[i]+".in"
        shutil.copyfile(first_file, new_file)
        file_edit(new_file, new_cycles[i], all_cycles[i+1], all_cycles[i], new_cycles_identifier[i])

        os.system("run_anc -i "+new_cycles[i]+".in &")
        time.sleep(60)
        for filename in os.listdir(current_directory):
            if filename.startswith(new_cycles[i]) and filename.endswith(".out"):
                out_file = filename

        check_run(out_file)
    
    if i == 0:
        FirstRunChange(new_cycles[i]+".in")
        os.system("run_anc -i "+new_cycles[i]+".in &")
        time.sleep(60)
        for filename in os.listdir(current_directory):
            if filename.startswith(new_cycles[i]) and filename.endswith(".out"):
                out_file = filename

        check_run(out_file)
    



cycles = ["cycle_N_cy34","cycle_35","cycle_36","cycle_37"]

with open("general_se_general.txt","w") as f:
    f.write("start \n")

for i in range(len(cycles)):

    for filename in os.listdir(current_directory):
        if filename.startswith(cycles[i]) and filename.endswith(".out"):
            out_file = filename

    with open(out_file,"r") as f:
        file = f.readlines()
        newlines = ""
        for j, line in enumerate(file):
            if "SE-General         Summary of ANC Cases" in line:
                newlines = file[j+1:j+28]

    with open("general_se_general.txt","a") as f:
        f.write(cycles[i]+"\n")
        for k in newlines:
            f.write(k)
        f.write("\n \n")

