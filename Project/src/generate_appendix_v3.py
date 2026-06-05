import re

files = [
    ("common_params.py", "Params"),
    ("cavity_model.py", "Analytical Cavity Model"),
    ("sim_hamiltonian.py", "Hamiltonian & Operators"),
    ("sim_reflection.py", "Steady-State Reflection"),
    ("sim_dynamics.py", "Dynamics (Rabi & Purcell)"),
    ("sim_cnot.py", "CNOT Truth Table"),
    ("figure2.py", "Fig 2: Resonance"),
    ("figure3.py", "Fig 3: Rabi & Spectra"),
    ("figure4.py", "Fig 4: CNOT"),
    ("figure_s2.py", "Fig S2: g2"),
    ("figure_s4.py", "Fig S4: Purcell")
]

latex_header = r"""\documentclass[10pt, a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\geometry{a4paper, margin=0.7in}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{hyperref}
\usepackage{titlesec}
\usepackage{multicol}

% Section formatting for readability
\titleformat{\section}{\normalfont\Large\bfseries}{\thesection}{1em}{}
\titlespacing*{\section}{0pt}{2ex plus 1ex minus .2ex}{1ex plus .2ex}

% Code beautification configuration
\definecolor{codegreen}{rgb}{0,0.5,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{keywordcolor}{rgb}{0.0,0.4,0.8}

\lstdefinestyle{pythonstyle}{
    commentstyle=\color{codegreen}\itshape,
    keywordstyle=\color{keywordcolor}\bfseries,
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\scriptsize, % Smaller font to save space
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=5pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=2,
    frame=single,
    rulecolor=\color{codegray!40},
    xleftmargin=10pt,
    xrightmargin=0pt,
    aboveskip=0pt,
    belowskip=0pt
}
\lstset{style=pythonstyle}

\begin{document}
\title{\vspace{-1.5cm}\Large\textbf{Appendix: Simulation and Analysis Code}}
\date{}
\maketitle
\vspace{-1.5cm}
\tableofcontents
\vspace{0.5cm}
"""

out = [latex_header]

def process_file(content):
    # 1. Strip docstrings
    in_docstring = False
    doc_char = ""
    lines = content.split('\n')
    cleaned_lines1 = []
    
    for line in lines:
        s = line.strip()
        if not in_docstring:
            if s.startswith('"""') and s.endswith('"""') and len(s)>3:
                continue
            if s.startswith("'''") and s.endswith("'''") and len(s)>3:
                continue
            if s.startswith('"""'):
                in_docstring = True
                doc_char = '"""'
                continue
            if s.startswith("'''"):
                in_docstring = True
                doc_char = "'''"
                continue
            cleaned_lines1.append(line)
        else:
            if doc_char in line:
                in_docstring = False
            continue

    # 2. Combine comments and pack
    cleaned_lines2 = []
    pending = []
    
    for line in cleaned_lines1:
        s = line.strip()
        
        # Skip empty lines, prints, matplotlib setups
        if not s: continue
        if s.startswith('print('): continue
        if s.startswith('import matplotlib'): continue
        if s.startswith('matplotlib.use'): continue
        if s.startswith('import time'): continue
        if s.startswith('os.makedirs'): continue
        if s.startswith('t_start ='): continue
        if "time.time()" in s: continue
        if "plt.savefig" in s: continue
        if "plt.close" in s: continue
            
        if s.startswith('#'):
            c = s.lstrip('#').strip()
            # Skip massive separators
            if not c or set(c).issubset({'=','-','_','*',' '}):
                continue
            pending.append(c)
        else:
            code_part = line
            inline_cmt = ""
            if '#' in line and "color='" not in line and 'color="' not in line:
                parts = line.split('#', 1)
                code_part = parts[0]
                inline_cmt = parts[1].strip()
                
            code_part = code_part.rstrip()
            
            all_c = pending[:]
            if inline_cmt:
                all_c.append(inline_cmt)
                
            if all_c:
                combined = "; ".join(all_c)
                # Keep comments reasonably short
                if len(combined) > 100: combined = combined[:97] + "..."
                new_line = f"{code_part}  # {combined}"
            else:
                new_line = code_part
                
            cleaned_lines2.append(new_line)
            pending = []
            
    return "\n".join(cleaned_lines2)

for f, desc in files:
    try:
        with open(f, 'r') as fp:
            content = fp.read()
            
        cleaned = process_file(content)
        
        name = f.replace('_', '\\_')
        out.append(f"\\section{{{name}: {desc}}}")
        out.append(f"\\begin{{lstlisting}}[language=Python]")
        out.append(cleaned.strip())
        out.append("\\end{lstlisting}\n")
    except Exception as e:
        print(f"Failed on {f}: {e}")

out.append("\\end{document}")

with open("appendix_code.tex", "w") as fp:
    fp.write("\n".join(out))
print("Standalone Appendix generated successfully.")
