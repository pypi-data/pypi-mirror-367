

#: s block elements, group 1
s_block_col_1 = ["Li", "Na", "K", "Rb", "Cs", "Fr"]
#: s block elements, group 2
s_block_col_2 = ["Be", "Mg", "Ca", "Sr", "Ba", "Ra"]

#: all s block elements
s_block = s_block_col_1 + s_block_col_2

#: first row p-block elements
p_block_row_1 = ["He"]
#: second row p-block elements
p_block_row_2 = ["B", "C", "N", "O", "F", "Ne"]
#: third row p-block elements
p_block_row_3 = ["Al", "Si", "P", "S", "Cl", "Ar"]
#: fourth row p-block elements
p_block_row_4 = ["Ga", "Ge", "As", "Se", "Br", "Kr"]
#: fifth row p-block elements
p_block_row_5 = ["In", "Sn", "Sb", "Te", "I", "Xe"]
#: sixth row p-block elements
p_block_row_6 = ["Tl", "Pb", "Bi", "Po", "At", "Rn"]
#: seventh row p-block elements
p_block_row_7 = ["Nh", "Fl", "Mc", "Lv", "Ts", "Og"]

#: all p block elements
p_block = p_block_row_1 + p_block_row_2 + p_block_row_3 + p_block_row_4
p_block += p_block_row_5 + p_block_row_6 + p_block_row_7

#: first row d-block elements
d_block_row_1 = [
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"
]

#: second row d-block elements
d_block_row_2 = [
    "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd"
]

#: third row d-block elements
d_block_row_3 = [
    "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Ni", "Au", "Hg"
]

#: fourth row d-block elements
d_block_row_4 = [
    "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh"
]

#: All d-block elements
d_block = d_block_row_1 + d_block_row_2 + d_block_row_3 + d_block_row_4

#: All transition metals
transition_metals = d_block

#: first row f-block elements
f_block_row_1 = [
    "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho",
    "Er", "Tm", "Yb", "Lu"
]

#: All lanthanides
lanthanides = f_block_row_1

#: second row f-block elements
f_block_row_2 = [
    "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es",
    "Fm", "Md", "No", "Lr"
]

#: All actinides
actinides = f_block_row_1

#: All f-block elements
f_block = f_block_row_1 + f_block_row_2

#: All metals
metals = s_block + d_block + f_block
metals += ["Al", "Ge", "Ga", "In", "Sn", "Tl", "Pb", "Bi", "Po"]

#: All non-metals
non_metals = list(set(p_block).difference(metals)) + ['H']

#: All elements
elements = s_block + p_block + d_block + f_block + ['H']

#: Relative atomic masses
masses = {
    "H": 1.0076, "He": 4.0026, "Li": 6.941, "Be": 9.0122, "B": 10.811,
    "C": 12.0107, "N": 14.0067, "O": 15.9994, "F": 18.9984, "Ne": 20.1797,
    "Na": 22.9897, "Mg": 24.305, "Al": 26.9815, "Si": 28.0855, "P": 30.9738,
    "S": 32.065, "Cl": 35.453, "K": 39.0983, "Ar": 39.948, "Ca": 40.078,
    "Sc": 44.9559, "Ti": 47.867, "V": 50.9415, "Cr": 51.9961, "Mn": 54.938,
    "Fe": 55.845, "Ni": 58.6934, "Co": 58.9332, "Cu": 63.546, "Zn": 65.39,
    "Ga": 69.723, "Ge": 72.64, "As": 74.9216, "Se": 78.96, "Br": 79.904,
    "Kr": 83.8, "Rb": 85.4678, "Sr": 87.62, "Y": 88.9059, "Zr": 91.224,
    "Nb": 92.9064, "Mo": 95.94, "Tc": 98, "Ru": 101.07, "Rh": 102.9055,
    "Pd": 106.42, "Ag": 107.8682, "Cd": 112.411, "In": 114.818, "Sn": 118.71,
    "Sb": 121.76, "I": 126.9045, "Te": 127.6, "Xe": 131.293, "Cs": 132.9055,
    "Ba": 137.327, "La": 138.9055, "Ce": 140.116, "Pr": 140.9077, "Nd": 144.24,
    "Pm": 145, "Sm": 150.36, "Eu": 151.964, "Gd": 157.25, "Tb": 158.9253,
    "Dy": 162.5, "Ho": 164.9303, "Er": 167.259, "Tm": 168.9342, "Yb": 173.04,
    "Lu": 174.967, "Hf": 178.49, "Ta": 180.9479, "W": 183.84, "Re": 186.207,
    "Os": 190.23, "Ir": 192.217, "Pt": 195.078, "Au": 196.9665, "Hg": 200.59,
    "Tl": 204.3833, "Pb": 207.2, "Bi": 208.9804, "Po": 209, "At": 210,
    "Rn": 222, "Fr": 223, "Ra": 226, "Ac": 227, "Pa": 231.0359, "Th": 232.0381,
    "Np": 237, "U": 238.0289, "Am": 243, "Pu": 244, "Cm": 247, "Bk": 247,
    "Cf": 251, "Es": 252, "Fm": 257, "Md": 258, "No": 259, "Rf": 261,
    "Lr": 262, "Db": 262, "Bh": 264, "Sg": 266, "Mt": 268, "Rg": 272, "Hs": 277
}

#: Atomic label to atomic number dictionary
lab_num = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7,
    "O": 8, "F": 9, "Ne": 10, "Na": 11, "Mg": 12, "Al": 13,
    "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18, "K": 19,
    "Ca": 20, "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25,
    "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30, "Ga": 31,
    "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36, "Rb": 37,
    "Sr": 38, "Y": 39, "Zr": 40, "Nb": 41, "Mo": 42, "Tc": 43,
    "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48, "In": 49,
    "Sn": 50, "Sb": 51, "Te": 52, "I": 53, "Xe": 54, "Cs": 55,
    "Ba": 56, "La": 57, "Ce": 58, "Pr": 59, "Nd": 60, "Pm": 61,
    "Sm": 62, "Eu": 63, "Gd": 64, "Tb": 65, "Dy": 66, "Ho": 67,
    "Er": 68, "Tm": 69, "Yb": 70, "Lu": 71, "Hf": 72, "Ta": 73,
    "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78, "Au": 79,
    "Hg": 80, "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84, "At": 85,
    "Rn": 86, "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90, "Pa": 91,
    "U": 92, "Np": 93, "Pu": 94, "Am": 95, "Cm": 96, "Bk": 97,
    "Cf": 98, "Es": 99, "Fm": 100, "Md": 101, "No": 102, "Lr": 103,
    "Rf": 104, "Db": 105, "Sg": 106, "Bh": 107, "Hs": 108,
    "Mt": 109, "Ds": 110, "Rg": 111, "Cn": 112, "Nh": 113,
    "Fl": 114, "Mc": 115, "Lv": 116, "Ts": 117, "Og": 118
}

#: Atomic number to atomic label dictionary
num_lab = dict(zip(lab_num.values(), lab_num.keys()))

#: Atomic radii
#:
#: Also called vdW radii
#:
#: https://www.rsc.org/periodic-table/
#:
#: CRC Handbook of Chemistry and Physics, 97th Ed.; Haynes, W. M. Ed. CRC
#: Press/Taylor and Francis: Boca Raton, 2016 (accessed 2022-10-01).
atomic_radii = {
    "H": 1.1, "He": 1.4, "Li": 1.82, "Be": 1.53, "B": 1.92, "C": 1.7,
    "N": 1.55, "O": 1.52, "F": 1.47, "Ne": 1.54, "Na": 2.27, "Mg": 1.73,
    "Al": 1.84, "Si": 2.1, "P": 1.8, "S": 1.8, "Cl": 1.75, "Ar": 1.88,
    "K": 2.75, "Ca": 2.31, "Sc": 2.15, "Ti": 2.11, "V": 2.07, "Cr": 2.06,
    "Mn": 2.05, "Fe": 2.04, "Co": 2.0, "Ni": 1.97, "Cu": 1.96, "Zn": 2.01,
    "Ga": 1.87, "Ge": 2.11, "As": 1.85, "Se": 1.9, "Br": 1.85, "Kr": 2.02,
    "Rb": 3.03, "Sr": 2.49, "Y": 2.32, "Zr": 2.23, "Nb": 2.18, "Mo": 2.17,
    "Tc": 2.16, "Ru": 2.13, "Rh": 2.1, "Pd": 2.1, "Ag": 2.11, "Cd": 2.18,
    "In": 1.93, "Sn": 2.17, "Sb": 2.06, "Te": 2.06, "I": 1.98, "Xe": 2.16,
    "Cs": 3.43, "Ba": 2.68, "La": 2.43, "Ce": 2.42, "Pr": 2.4, "Nd": 2.39,
    "Pm": 2.38, "Sm": 2.36, "Eu": 2.35, "Gd": 2.34, "Tb": 2.33, "Dy": 2.31,
    "Ho": 2.3, "Er": 2.29, "Tm": 2.27, "Yb": 2.26, "Lu": 2.24, "Hf": 2.23,
    "Ta": 2.22, "W": 2.18, "Re": 2.16, "Os": 2.16, "Ir": 2.13, "Pt": 2.13,
    "Au": 2.14, "Hg": 2.23, "Tl": 1.96, "Pb": 2.02, "Bi": 2.07, "Po": 1.97,
    "At": 2.02, "Rn": 2.2, "Fr": 3.48, "Ra": 2.83, "Ac": 2.47, "Th": 2.45,
    "Pa": 2.43, "U": 2.41, "Np": 2.39, "Pu": 2.43, "Am": 2.44, "Cm": 2.45,
    "Bk": 2.44, "Cf": 2.45, "Es": 2.45, "Fm": 2.45, "Md": 2.46, "No": 2.46,
    "Lr": 2.46
}
#: Covalent radii
#:
#: https://www.rsc.org/periodic-table/\n
cov_radii = {
    "H": 0.32, "He": 0.37, "Li": 1.3, "Be": 0.99, "B": 0.84, "C": 0.75,
    "N": 0.71, "O": 0.64, "F": 0.6, "Ne": 0.62, "Na": 1.6, "Mg": 1.4,
    "Al": 1.24, "Si": 1.14, "P": 1.09, "S": 1.04, "Cl": 1.0, "Ar": 1.01,
    "K": 2.0, "Ca": 1.74, "Sc": 1.59, "Ti": 1.48, "V": 1.44, "Cr": 1.3,
    "Mn": 1.29, "Fe": 1.24, "Co": 1.18, "Ni": 1.17, "Cu": 1.22, "Zn": 1.2,
    "Ga": 1.23, "Ge": 1.2, "As": 1.2, "Se": 1.18, "Br": 1.17, "Kr": 1.16,
    "Rb": 2.15, "Sr": 1.9, "Y": 1.76, "Zr": 1.64, "Nb": 1.56, "Mo": 1.46,
    "Tc": 1.38, "Ru": 1.36, "Rh": 1.34, "Pd": 1.3, "Ag": 1.36, "Cd": 1.4,
    "In": 1.42, "Sn": 1.4, "Sb": 1.4, "Te": 1.37, "I": 1.36, "Xe": 1.36,
    "Cs": 2.38, "Ba": 2.06, "La": 1.94, "Ce": 1.84, "Pr": 1.9, "Nd": 1.88,
    "Pm": 1.86, "Sm": 1.85, "Eu": 1.83, "Gd": 1.82, "Tb": 1.81, "Dy": 1.8,
    "Ho": 1.79, "Er": 1.77, "Tm": 1.77, "Yb": 1.78, "Lu": 1.74, "Hf": 1.64,
    "Ta": 1.58, "W": 1.5, "Re": 1.41, "Os": 1.36, "Ir": 1.32, "Pt": 1.3,
    "Au": 1.3, "Hg": 1.32, "Tl": 1.44, "Pb": 1.45, "Bi": 1.5, "Po": 1.42,
    "At": 1.48, "Rn": 1.46, "Fr": 2.42, "Ra": 2.11, "Ac": 2.01, "Th": 1.9,
    "Pa": 1.84, "U": 1.83, "Np": 1.8, "Pu": 1.8, "Am": 1.73, "Cm": 1.68,
    "Bk": 1.68, "Cf": 1.68, "Es": 1.65, "Fm": 1.67, "Md": 1.73, "No": 1.76,
    "Lr": 1.61, "Rf": 1.57, "Db": 1.49, "Sg": 1.43, "Bh": 1.41, "Hs": 1.34,
    "Mt": 1.29, "Ds": 1.28, "Rg": 1.21, "Cn": 1.22, "Nh": 1.36, "Fl": 1.43,
    "Mc": 1.62, "Lv": 1.75, "Ts": 1.65, "Og": 1.57
}
