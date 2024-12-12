
import math


blif_lines = []
N = 9
u_num = v_num = math.ceil(math.log2(N)/2) * 4
c_num = d_num = N

def add_main_model():
    blif_lines.append(".model sudoku\n")
    blif_lines.append(".inputs ")
    for i in range(u_num):
        blif_lines.append("u" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("v" + str(i) + " ")
    for i in range(c_num):
        blif_lines.append("c" + str(i) + " ")
    for i in range(d_num):
        blif_lines.append("d" + str(i) + " ")
    blif_lines.append("\n")
    blif_lines.append(".outputs f\n")

    blif_lines.append(".subckt graph ")
    for i in range(u_num):
        blif_lines.append("U" + str(i) + "=u" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("V" + str(i) + "=v" + str(i) + " ")
    blif_lines.append("E=e\n")

    blif_lines.append(".subckt color_not_equal ")
    for i in range(c_num):
        blif_lines.append("C" + str(i) + "=c" + str(i) + " ")
    for i in range(d_num):
        blif_lines.append("D" + str(i) + "=d" + str(i) + " ")
    blif_lines.append("O_equal=ncolor\n")

    blif_lines.append(".subckt onehot" + str(c_num) + " ")
    for i in range(c_num):
        blif_lines.append("I" + str(i) + "=c" + str(i) + " ")
    blif_lines.append("O=conehot\n")

    blif_lines.append(".subckt onehot" + str(d_num) + " ")
    for i in range(d_num):
        blif_lines.append("I" + str(i) + "=d" + str(i) + " ")
    blif_lines.append("O=donehot\n")

    blif_lines.append(".subckt imply I0=e I1=ncolor O=diffcolor\n")

    blif_lines.append(".subckt and2 I0=conehot I1=donehot O=conehotdonehot\n")

    # not same node
    blif_lines.append(".subckt UneqV" + str(u_num) + " ")
    for i in range(u_num):
        blif_lines.append("U" + str(i) + "=u" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("V" + str(i) + "=v" + str(i) + " ")
    blif_lines.append("O_equal=notsamenode\n")

    # not same color
    blif_lines.append(".subckt UneqV" + str(c_num) + " ")
    for i in range(c_num):
        blif_lines.append("U" + str(i) + "=c" + str(i) + " ")
    for i in range(d_num):
        blif_lines.append("V" + str(i) + "=d" + str(i) + " ")
    blif_lines.append("O_equal=notsamecolor\n")

    blif_lines.append(".subckt imply I0=notsamecolor I1=notsamenode O=notsamecolornode\n")

    blif_lines.append(".subckt and2 I0=diffcolor I1=conehotdonehot O=temp1\n")
    blif_lines.append(".subckt and2 I0=notsamecolornode I1=temp1 O=f\n")

    blif_lines.append(".end\n\n")

def add_implicit_graph():
    blif_lines.append(".model graph\n")
    blif_lines.append(".inputs ")
    for i in range(u_num):
        blif_lines.append("U" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("V" + str(i) + " ")
    blif_lines.append("\n")
    blif_lines.append(".outputs E\n")
    
    blif_lines.append(".subckt UneqV" + str(u_num) + " ")
    for i in range(u_num):
        blif_lines.append("U" + str(i) + "=U" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("V" + str(i) + "=V" + str(i) + " ")
    blif_lines.append("O_equal=notsamenode\n")

    half = int(u_num/2)
    blif_lines.append(".subckt UxequVx ")
    for i in range(half):
        blif_lines.append("U" + str(i) + "=U" + str(i) + " ")
    for i in range(half):
        blif_lines.append("V" + str(i) + "=V" + str(i) + " ")
    blif_lines.append("O_equal=samecolumn\n")

    blif_lines.append(".subckt UxequVx ")
    for i in range(half):
        blif_lines.append("U" + str(i) + "=U" + str(half+i) + " ")
    for i in range(half):
        blif_lines.append("V" + str(i) + "=V" + str(half+i) + " ")
    blif_lines.append("O_equal=samerow\n")
    
    quarter = int(u_num/4)
    blif_lines.append(".subckt UxequVx ")
    for i in range(half):
        if i < quarter:
            blif_lines.append("U" + str(i) + "=U" + str(i) + " ")
        else:
            blif_lines.append("U" + str(i) + "=U" + str(quarter+i) + " ")
    for i in range(half):
        if i < quarter:
            blif_lines.append("V" + str(i) + "=V" + str(i) + " ")
        else:
            blif_lines.append("V" + str(i) + "=V" + str(quarter+i) + " ")
    blif_lines.append("O_equal=samebox\n")

    ## TODO modify to exclude unused nodes

    blif_lines.append(".subckt or2 I0=samecolumn I1=samerow O=cross\n")
    blif_lines.append(".subckt or2 I0=cross I1=samebox O=alledges\n")
    blif_lines.append(".subckt and2 I0=notsamenode I1=alledges O=E\n")
    blif_lines.append(".end\n\n")
    return

def add_color_not_equal():
    blif_lines.append(".model color_not_equal\n")
    blif_lines.append(".inputs ")
    for i in range(c_num):
        blif_lines.append("C" + str(i) + " ")
    for i in range(d_num):
        blif_lines.append("D" + str(i) + " ")
    blif_lines.append("\n.outputs O_equal\n")
    for i in range(c_num):
        blif_lines.append(".subckt nequiv I0=C" + str(i) + " I1=D" + str(i) + " O=unequal" + str(i) + "\n")
    blif_lines.append(".subckt or" + str(c_num))
    for i in range(c_num):
        blif_lines.append(" I" + str(i) + "=unequal" + str(i))
    blif_lines.append(" O=O_equal\n")
    blif_lines.append(".end\n\n")
    return

### All fundamental gates
def add_not_gate():
    blif_lines.append(".model not\n")
    blif_lines.append(".inputs I\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I O\n")
    blif_lines.append("0 1\n")
    blif_lines.append(".end\n\n")
    return

def add_imply_gate():
    blif_lines.append(".model imply\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("0- 1\n")
    blif_lines.append("-1 1\n")
    blif_lines.append(".end\n\n")
    return

def add_equiv_gate():
    blif_lines.append(".model equiv\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("11 1\n")
    blif_lines.append("00 1\n")
    blif_lines.append(".end\n\n")
    return

def add_nequiv_gate():
    blif_lines.append(".model nequiv\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("01 1\n")
    blif_lines.append("10 1\n")
    blif_lines.append(".end\n\n")
    return

def add_or_num(num):
    blif_lines.append(".model or" + str(num) + "\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("\n.outputs O\n")
    blif_lines.append(".names ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("O\n")
    for i in range(num):
        line = "-" * num + " 1\n"
        line = line[:i] + '1' + line[i+1:]
        blif_lines.append(line)

    blif_lines.append(".end\n\n")
    return

def add_and_num(num):
    # num = int(u_num/2)
    blif_lines.append(".model and" + str(num) + "\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("\n.outputs O\n")
    blif_lines.append(".names ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("O\n")
    blif_lines.append("1" * num + " 1\n")

    blif_lines.append(".end\n\n")
    return

def add_UnequivV(num):
    # vector U and V are not equivalent
    blif_lines.append(".model UneqV" + str(num) + "\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append("U" + str(i) + " ")
    for i in range(num):
        blif_lines.append("V" + str(i) + " ")
    blif_lines.append("\n")
    blif_lines.append(".outputs O_equal\n")
    
    for i in range(num):
        blif_lines.append(".subckt nequiv I0=U" + str(i) + " I1=V" + str(i) + " O=unequal" + str(i) + "\n")
    blif_lines.append(".subckt or" + str(num))
    for i in range(num):
        blif_lines.append(" I" + str(i) + "=unequal" + str(i))
    blif_lines.append(" O=O_equal\n")
    blif_lines.append(".end\n\n")
    return

def add_UxequivVx():
    # vector Ux and Vx are equivalent
    num = int(u_num/2)
    blif_lines.append(".model UxequVx\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append("U" + str(i) + " ")
    for i in range(num):
        blif_lines.append("V" + str(i) + " ")
    blif_lines.append("\n")
    blif_lines.append(".outputs O_equal\n")

    for i in range(num):
        blif_lines.append(".subckt equiv I0=U" + str(i) + " I1=V" + str(i) + " O=equal" + str(i) + "\n")
    blif_lines.append(".subckt and" + str(num))
    for i in range(num):
        blif_lines.append(" I" + str(i) + "=equal" + str(i))
    blif_lines.append(" O=O_equal\n")
    blif_lines.append(".end\n\n")
    return

def add_onehot(num):
    blif_lines.append(".model onehot" + str(num) + "\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("\n.outputs O\n")
    blif_lines.append(".names ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("O\n")
    for i in range(num):
        line = "0" * num + " 1\n"
        line = line[:i] + '1' + line[i+1:]
        blif_lines.append(line)

    blif_lines.append(".end\n\n")
    return

def add_subcircuit_model():
    add_not_gate()
    add_or_num(2)
    add_and_num(2)
    add_imply_gate()
    add_equiv_gate()
    add_nequiv_gate()
    add_or_num(u_num)
    add_UnequivV(u_num)
    if u_num != c_num : 
        add_or_num(c_num)
        add_UnequivV(c_num)
    add_and_num(int(u_num/2))
    
    add_UxequivVx()
    add_onehot(c_num)
    return

if __name__ == "__main__":
    add_main_model()
    add_implicit_graph()
    add_color_not_equal()
    add_subcircuit_model()
    with open("sudoku.blif", "w") as f:
        f.writelines(blif_lines)