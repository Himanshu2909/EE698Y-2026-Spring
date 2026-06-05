import re

files = [
    "common_params.py",
    "cavity_model.py",
    "sim_hamiltonian.py",
    "sim_reflection.py",
    "sim_dynamics.py",
    "sim_cnot.py",
    "figure2.py",
    "figure3.py",
    "figure4.py",
    "figure_s2.py",
    "figure_s4.py"
]

out = []
out.append("\\section{Simulation and Analysis Code}")
out.append("\\label{sec:appendix_code}")
out.append("This appendix presents the Python codebase developed to simulate the quantum dot-cavity system and generate both the analytical and computational figures.\\n")

for f in files:
    try:
        with open(f, 'r') as fp:
            content = fp.read()
            
        # 1. Remove the first module-level docstring explicitly
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
        
        name = f.replace('_', '\\_')
        out.append(f"\\subsection{{{name}}}")
        out.append("\\begin{lstlisting}[language=Python]")
        out.append(cleaned_content.strip())
        out.append("\\end{lstlisting}\n")
    except Exception as e:
        print(f"Failed on {f}: {e}")

with open("appendix_code.tex", "w") as fp:
    fp.write("\n".join(out))
print("Appendix generated successfully.")
