import subprocess
import sys
import os

def run_command(cmd, outfile):
    with open(outfile, 'w') as out:
        subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT)

def extract_ast_only(lines):
    """
    Extract only AST lines from RPAL.exe output.
    We'll include lines that:
    - Start with '.' (AST indentation)
    - OR look like AST node labels like 'let', 'gamma', etc.
    """
    ast_lines = []
    start_recording = False
    for line in lines:
        stripped = line.strip()
        if stripped == "":
            continue
        if stripped.startswith((".", "let", "gamma", "function_form", "within", "rec", "tau", "or", "and", "not", "eq", "ne", "aug", "@", "->", "where")) or stripped.startswith("<ID:") or stripped.startswith("<STR:") or stripped in {"true", "false", "nil", "()"}:
            ast_lines.append(stripped)
    return ast_lines

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compare_ast.py <examples/file.rpal>")
        sys.exit(1)

    test_file = sys.argv[1]
    my_output = "my_output.txt"
    rpal_output = "rpal_output.txt"

    # Path to wine-wrapped rpal.exe
    rpal_exe_path = os.path.join("rpal-wine", "rpal.exe")
    if not os.path.exists(rpal_exe_path):
        print("❌ rpal.exe not found in ./rpal-wine/")
        sys.exit(1)

    print(f"🔧 Running your parser on {test_file}")
    run_command(["python", "myrpal.py", test_file, "-ast"], my_output)

    print(f"🔧 Running rpal.exe on {test_file}")
    run_command(["wine", rpal_exe_path, "-ast", test_file], rpal_output)

    with open(my_output) as f1, open(rpal_output) as f2:
        my_lines = [line.strip() for line in f1 if line.strip()]
        rpal_raw_lines = [line.rstrip() for line in f2]

    # Filter RPAL output to get AST only
    rpal_ast_lines = [line.strip() for line in extract_ast_only(rpal_raw_lines) if line.strip()]

    if my_lines == rpal_ast_lines:
        print("✅ ASTs match perfectly!")
    else:
        print("❌ ASTs do NOT match.")
        print("\n=== Your Output ===")
        print("\n".join(my_lines))
        print("\n=== RPAL.exe Output (AST only) ===")
        print("\n".join(rpal_ast_lines))
