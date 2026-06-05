import re

files = [
    ("common_params.py", "Physical Parameters"),
    ("cavity_model.py", "Analytical Cavity Model"),
    ("sim_hamiltonian.py", "Master Equation Hamiltonian & Operators"),
    ("sim_reflection.py", "Steady-State Reflection Solver"),
    ("sim_dynamics.py", "Time-Domain Dynamics (Rabi & Purcell)"),
    ("sim_cnot.py", "CNOT Polarization & Truth Table Logic"),
    ("figure2.py", "Figure 2: CW Spectroscopy & Resonance Spectra"),
    ("figure3.py", "Figure 3: Rabi Oscillations & Pumped Spectra"),
    ("figure4.py", "Figure 4: CNOT Operation Spectra"),
    ("figure_s2.py", "Figure S2: Second-Order Correlation (g2)"),
    ("figure_s4.py", "Figure S4: Purcell Lifetime vs. Detuning")
]

latex_header = r"""\documentclass[11pt, a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{hyperref}
\usepackage{titlesec}

% Section formatting for readability
\titleformat{\subsection}
  {\normalfont\Large\bfseries}{\thesubsection}{1em}{}

% Code beautification configuration
\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.96,0.96,0.94}
\definecolor{keywordcolor}{rgb}{0.0,0.4,0.8}

\lstdefinestyle{pythonstyle}{
    backgroundcolor=\color{backcolour},   
    commentstyle=\color{codegreen}\itshape,
    keywordstyle=\color{keywordcolor}\bfseries,
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\footnotesize,
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=8pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=4,
    frame=single,
    rulecolor=\color{codegray!40},
    framesep=3pt,
    xleftmargin=12pt,
    xrightmargin=4pt
}
\lstset{style=pythonstyle}

\begin{document}

\title{\Huge\textbf{Appendix \\ \Large Simulation and Analysis Code}}
\author{}
\date{}
\maketitle

\noindent This appendix presents the complete Python codebase developed to simulate the quantum dot-cavity system and generate both the analytical and computational figures. The codebase is organized into modular components separating physical constants, analytical derivation, master equation simulation, and visualization.

\tableofcontents
\newpage

"""

out = [latex_header]

for f, desc in files:
    try:
        with open(f, 'r') as fp:
            content = fp.read()
            
        # 1. Remove the first module-level docstring explicitly to reduce verbosity
        content = re.sub(r'^r?\"\"\"[\s\S]*?\"\"\"\n', '', content, count=1)
        
        # 2. Remove all print statements on their own line
        content = re.sub(r'^[ \t]*print\(.*?\)\n', '', content, flags=re.MULTILINE)
        
        # 3. Clean up huge comment blocks like # ===== or # ──── 
        content = re.sub(r'^[ \t]*#[ =─]+[ \t]*\n', '', content, flags=re.MULTILINE)
        
        # 4. Remove inline print statements
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.strip() == "import time": continue
            if "time.time()" in line: continue
            if line.strip().startswith("print("): continue
            
            # Reduce some extra blank lines
            if line.strip() == "" and len(new_lines) > 0 and new_lines[-1].strip() == "":
                continue
                
            new_lines.append(line)
        
        cleaned_content = "\n".join(new_lines)
        
        # Format the file section
        name = f.replace('_', '\\_')
        out.append(f"\\section{{{name}: {desc}}}")
        out.append(f"\\begin{{lstlisting}}[language=Python, caption={{{name}}}]")
        out.append(cleaned_content.strip())
        out.append("\\end{lstlisting}\n")
        out.append("\\newpage\n")
    except Exception as e:
        print(f"Failed on {f}: {e}")

out.append("\\end{document}")

with open("appendix_code.tex", "w") as fp:
    fp.write("\n".join(out))
print("Standalone Appendix generated successfully.")
