import numpy as np

boolean_mapping = ["00", "01", "10", "11"]
def boolean_to_blif(sudoku_results, output_file):
    # Part 1: Handle the fixed formula
    def handle_fixed_formula():
        blif_content = []
        blif = f"""
.model fuck_ARTHUR
.inputs u[0] u[1] u[2] u[3] u[4] u[5] u[6] u[7] v[0] v[1] v[2] v[3] v[4] v[5] v[6] v[7] c1 c2 c3 c4 c5 c6 c7 c8 c9 d1 d2 d3 d4 d5 d6 d7 d8 d9
.outputs f
        
        
        # SPECIFICATION FOR E(u, v)
        
# Calculate the differences between u and v
.names u[0] v[0] diff0
01 1
10 1
.names u[1] v[1] diff1
01 1
10 1
.names u[2] v[2] diff2
01 1
10 1
.names u[3] v[3] diff3
01 1
10 1
.names u[4] v[4] diff4
01 1
10 1
.names u[5] v[5] diff5
01 1
10 1
.names u[6] v[6] diff6
01 1
10 1
.names u[7] v[7] diff7
01 1
10 1

.names diff0 diff1 diff2 diff3 diff4 diff5 diff6 diff7 uneqv
1------- 1
-1------ 1
--1----- 1
---1---- 1
----1--- 1
-----1-- 1
------1- 1
-------1 1
        
        # ux = vx
.names u[0] v[0] eq0
11 1
00 1
.names u[1] v[1] eq1
11 1
00 1
.names u[2] v[2] eq2
11 1
00 1
.names u[3] v[3] eq3
11 1
00 1
.names eq0 eq1 eq2 eq3 eq0123
1111 1
        
        # uy = vy
.names u[4] v[4] eq4
11 1
00 1
.names u[5] v[5] eq5
11 1
00 1
.names u[6] v[6] eq6
11 1
00 1
.names u[7] v[7] eq7
11 1
00 1
.names eq4 eq5 eq6 eq7 eq4567
1111 1
        
        # (u_1\equiv v_1)(u_2\equiv v_2)(u_5\equiv v_5)(u_6\equiv v_6)
.names u[0] v[0] eq11
11 1
00 1
.names u[1] v[1] eq22
11 1
00 1
.names u[4] v[4] eq55
11 1
00 1
.names u[5] v[5] eq66
11 1
00 1
.names eq11 eq22 eq55 eq66 eq11225566
1111 1
        
        # or above 
.names eq0123 eq4567 eq11225566 orE
1-- 1
-1- 1
--1 1
        
        # and uneqv
.names uneqv orE andE
11 1
        
        # 3*3 constraints
.names u[0] u[1] and12
00 1
01 1
10 1
.names u[2] u[3] and34
00 1
01 1
10 1
.names u[4] u[5] and56
00 1
01 1
10 1
.names u[6] u[7] and78
00 1
01 1
10 1
.names and12 and34 and56 and78 and12345678
1111 1
.names and12345678 andE finalE
11 1
        """
        blif_content.append(blif)
        for i in range(1, 10):
            blif_content.append(f".names c{i} d{i} neq{i}")
            blif_content.append("01 1")
            blif_content.append("10 1")
        blif_content.append(f"""
.names neq1 neq2 neq3 neq4 neq5 neq6 neq7 neq8 neq9 cdneq
1-------- 1
-1------- 1
--1------ 1
---1----- 1
----1---- 1
-----1--- 1
------1-- 1
-------1- 1
--------1 1
        """)
        blif_content.append("""
.names finalE cdneq implE
0- 1
-1 1
        """)
        blif_content.append(".names c1 c2 c3 c4 c5 c6 c7 c8 c9 c123456789")
        for i in range(1, 10):
            blif_content.append(f"{'0' * (i - 1)}1{'0' * (9 - i)} 1")
        # for i in range(1, 10):
        #     for j in range(i + 1, 10):
        #         blif_content.append(f".names c{i} c{j} cnand{i}{j}")
        #         blif_content.append("00 1")
        #         blif_content.append("01 1")
        #         blif_content.append("10 1")
        # blif_content.append(".names cnand12 cnand13 cnand14 cnand15 cnand16 cnand17 cnand18 cnand19 cnand23 cnand24 cnand25 cnand26 cnand27 cnand28 cnand29 cnand34 cnand35 cnand36 cnand37 cnand38 cnand39 cnand45 cnand46 cnand47 cnand48 cnand49 cnand56 cnand57 cnand58 cnand59 cnand67 cnand68 cnand69 cnand78 cnand79 cnand89 cnandall")
        # blif_content.append("111111111111111111111111111111111111 1")
        blif_content.append(".names d1 d2 d3 d4 d5 d6 d7 d8 d9 d123456789")
        for i in range(1, 10):
            blif_content.append(f"{'0' * (i - 1)}1{'0' * (9 - i)} 1")
        # for i in range(1, 10):
        #     for j in range(i + 1, 10):
        #         blif_content.append(f".names d{i} d{j} dnand{i}{j}")
        #         blif_content.append("00 1")
        #         blif_content.append("01 1")
        #         blif_content.append("10 1")
        # blif_content.append(".names dnand12 dnand13 dnand14 dnand15 dnand16 dnand17 dnand18 dnand19 dnand23 dnand24 dnand25 dnand26 dnand27 dnand28 dnand29 dnand34 dnand35 dnand36 dnand37 dnand38 dnand39 dnand45 dnand46 dnand47 dnand48 dnand49 dnand56 dnand57 dnand58 dnand59 dnand67 dnand68 dnand69 dnand78 dnand79 dnand89 dnandall")
        # blif_content.append("111111111111111111111111111111111111 1")
        blif_content.append(".names implE c123456789 d123456789 implE_out")
        blif_content.append("111 1")
        
        blif_content.append(f"""
.names u[0] v[0] phieq0
11 1
00 1
.names u[1] v[1] phieq1
11 1
00 1
.names u[2] v[2] phieq2
11 1
00 1
.names u[3] v[3] phieq3
11 1
00 1
.names u[4] v[4] phieq4
11 1
00 1
.names u[5] v[5] phieq5
11 1
00 1
.names u[6] v[6] phieq6
11 1
00 1
.names u[7] v[7] phieq7
11 1
00 1
.names phieq0 phieq1 phieq2 phieq3 phieq4 phieq5 phieq6 phieq7 phieq01234567
11111111 1
        
.names c1 d1 cdphieq1
11 1
00 1
.names c2 d2 cdphieq2
11 1
00 1
.names c3 d3 cdphieq3
11 1
00 1
.names c4 d4 cdphieq4
11 1
00 1
.names c5 d5 cdphieq5
11 1
00 1
.names c6 d6 cdphieq6
11 1
00 1
.names c7 d7 cdphieq7
11 1
00 1
.names c8 d8 cdphieq8
11 1
00 1
.names c9 d9 cdphieq9
11 1
00 1
.names cdphieq1 cdphieq2 cdphieq3 cdphieq4 cdphieq5 cdphieq6 cdphieq7 cdphieq8 cdphieq9 cdphieq123456789
111111111 1
        
.names phieq01234567 cdphieq123456789 phiimpl
0- 1
-1 1
        
.names phiimpl implE_out finalphi
11 1
        """)
        return blif_content

    # Part 2: Handle the results from sudoku_gen.py
    def handle_sudoku_results(sudoku_results):
        # initial conditions
        sudoku_lines = np.array([[int(num) for num in line.split()] for line in sudoku_results.strip().split("\n")])
        blif_content = []
        for i in range(9):
            for j in range(9):
                if sudoku_lines[i][j] != 0:
                    u1u2 = boolean_mapping[j//3]
                    u3u4 = boolean_mapping[j%3]
                    u5u6 = boolean_mapping[i//3]
                    u7u8 = boolean_mapping[i%3]
                    print(f"i, j: {i}, {j}, u12, u34, u56, u78 = {i//3}, {i%3}, {j//3}, {j%3}")
                    print(u1u2, u3u4, u5u6, u7u8)
                    truth_value = ""
                    truth_value += u1u2[0]  
                    truth_value += u1u2[1]  
                    truth_value += u3u4[0]  
                    truth_value += u3u4[1]  
                    truth_value += u5u6[0]  
                    truth_value += u5u6[1]  
                    truth_value += u7u8[0]  
                    truth_value += u7u8[1]  
                    
                    blif_content.append(f".names u[0] u[1] u[2] u[3] u[4] u[5] u[6] u[7] c{sudoku_lines[i][j]} init{i}{j}")
                    blif_content.append(f"{truth_value}1 1")
        init_conditions = " ".join([f"init{i}{j}" for i in range(9) for j in range(9) if sudoku_lines[i][j] != 0])
        blif_content.append(f".names {init_conditions} final_init")
        blif_content.append("1" * len(init_conditions.split()) + " 1")
                    
        return blif_content
    

    # Generate the .blif content
    blif_content = []
    blif_content.extend(handle_fixed_formula())
    blif_content.extend(handle_sudoku_results(sudoku_results))
    blif_content.append(".names final_init finalphi f")
    blif_content.append("11 1")
    blif_content.append(".end")
    
    # Write to the .blif file
    with open(output_file, 'w') as file:
        for line in blif_content:
            file.write(line + "\n")
    

# Example usage
import subprocess

# Call the sudoku_gen.py script
subprocess.run(["python3", "sudoku/sudoku_gen.py"])

with open("sample/sudoku.txt", "r") as f:
    sudoku_results = f.read()
output_file = "output.blif"
boolean_to_blif(sudoku_results, output_file)
