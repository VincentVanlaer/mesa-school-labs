#!/usr/bin/env python3
"""
dependency_checker.py

A utility script to check for dependencies required by the MESA batch_runs functionality.
Designed to be run from within the batch_runs directory.
Produces a formatted terminal report showing what's installed and what's missing,
with instructions for fixing missing dependencies.
"""

import os
import sys
import subprocess
import importlib
import platform
import shutil

# Define color codes for terminal output
class Colors:
    HEADER = '\033[36m'
    BLUE="\033[0;36m"
    GREEN="\033[0;32m"
    YELLOW="\033[0;33m"
    RED="\033[0;31m"
    BOLD="\033[1m"
    UNDERLINE = '\033[4m'
    END = '\033[0m'




def colorize(text, color):
    """Apply color to text if terminal supports it"""
    if sys.stdout.isatty():  # Only colorize if in a terminal
        return f"{color}{text}{Colors.END}"
    return text

def check_module(module_name, min_version=None, pip_name=None):
    """
    Check if a Python module is installed and meets minimum version requirements.
    
    Args:
        module_name: Name of the module to import
        min_version: Minimum required version (optional)
        pip_name: Name to use for pip installation if different from module_name
    
    Returns:
        dict with status information
    """
    if pip_name is None:
        pip_name = module_name
        
    result = {
        "name": module_name,
        "installed": False,
        "version": None,
        "meets_version": False if min_version else None,
        "pip_name": pip_name
    }
    
    try:
        module = importlib.import_module(module_name)
        result["installed"] = True
        
        if hasattr(module, '__version__'):
            result["version"] = module.__version__
        elif hasattr(module, 'version'):
            result["version"] = module.version
        
        if min_version and result["version"]:
            # Simple version comparison - might need refinement for complex version strings
            try:
                result["meets_version"] = tuple(map(int, result["version"].split('.'))) >= tuple(map(int, min_version.split('.')))
            except (ValueError, TypeError):
                # Fall back to string comparison if parsing fails
                result["meets_version"] = result["version"] >= min_version
        
    except ImportError:
        pass
    
    return result

def check_command(command, args=None, version_flag='--version', min_version=None):
    """
    Check if a command-line tool is installed and available in PATH.
    
    Args:
        command: Command name to check
        args: List of arguments to pass (optional)
        version_flag: Flag to retrieve version information
        min_version: Minimum required version (optional)
        
    Returns:
        dict with status information
    """
    result = {
        "name": command,
        "installed": False,
        "version": None,
        "meets_version": False if min_version else None
    }
    
    if shutil.which(command):
        result["installed"] = True
        
        if version_flag:
            try:
                version_cmd = [command, version_flag]
                proc = subprocess.run(version_cmd, text=True, capture_output=True, timeout=2)
                if proc.returncode == 0:
                    # Extract first line of output and strip common text
                    version_output = proc.stdout.strip().split('\n')[0]
                    # Simple extraction - this may need to be customized per command
                    version_parts = version_output.split()
                    for part in version_parts:
                        if part[0].isdigit():
                            result["version"] = part
                            break
            except (subprocess.SubprocessError, FileNotFoundError, IndexError):
                pass
    
    return result

def check_mesa_environment():
    """Check if MESA environment variables are properly set"""
    result = {
        "mesa_dir": os.environ.get("MESA_DIR"),
        "mesasdk_root": os.environ.get("MESASDK_ROOT"),
        "mesa_threads": os.environ.get("OMP_NUM_THREADS"),
        "properly_set": False
    }
    
    if result["mesa_dir"] and result["mesasdk_root"]:
        if os.path.isdir(result["mesa_dir"]) and os.path.isdir(result["mesasdk_root"]):
            result["properly_set"] = True
    
    return result

def check_batch_directories():
    """Check for required subdirectories in the batch_runs directory"""
    required_dirs = ["../runs", "../batch_inlists"]
    
    results = {}
    for dirname in required_dirs:
        path = os.path.join(os.curdir, dirname)
        results[dirname] = os.path.isdir(path)
        
    return results

def check_all_dependencies():
    """Check all dependencies required for MESA batch runs"""
    results = {
        "system_info": {
            "python_version": platform.python_version(),
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine()
        },
        "mesa_environment": check_mesa_environment(),
        "python_modules": [
            check_module("numpy", min_version="1.17.0"),
            check_module("matplotlib", min_version="3.0.0"),
            check_module("pandas", min_version="1.0.0"),
            check_module("mesa_reader", pip_name="mesa_reader"),
            check_module("scipy", min_version="1.0.0"),
            check_module("PIL", min_version="7.0.0", pip_name="Pillow")
        ],
        "command_line_tools": [
            check_command("python3"),
            check_command("gfortran")
        ],
        "batch_directories": check_batch_directories()
    }
    
    return results

def generate_report(results):
    """Generate a nicely formatted report of the dependency check results"""
    report = []
    
    # Header
    report.append(colorize("="*80, Colors.BOLD))
    report.append(colorize(" MESA BATCH RUNS DEPENDENCY CHECKER ", Colors.BOLD).center(80))
    report.append(colorize("="*80, Colors.BOLD))
    report.append("")
    
    # System Information
    report.append(colorize("SYSTEM INFORMATION", Colors.HEADER))
    report.append(f"Python Version: {results['system_info']['python_version']}")
    report.append(f"Operating System: {results['system_info']['os']} {results['system_info']['os_version']}")
    report.append(f"Architecture: {results['system_info']['architecture']}")
    report.append("")
    
    # MESA Environment
    report.append(colorize("MESA ENVIRONMENT", Colors.HEADER))
    mesa_env = results["mesa_environment"]
    if mesa_env["properly_set"]:
        status = colorize("PROPERLY SET", Colors.GREEN)
    else:
        status = colorize("NOT PROPERLY SET", Colors.RED)
    
    report.append(f"Status: {status}")
    report.append(f"MESA_DIR: {mesa_env['mesa_dir'] or 'Not set'}")
    report.append(f"MESASDK_ROOT: {mesa_env['mesasdk_root'] or 'Not set'}")
    report.append(f"MESA Threads: {mesa_env['mesa_threads'] or 'Not set'}")
    
    if not mesa_env["properly_set"]:
        report.append(colorize("\nAction Required:", Colors.YELLOW))
        if not mesa_env["mesa_dir"] or not mesa_env["mesasdk_root"]:
            report.append("  Set the required environment variables in your shell:")
            report.append("  - For bash/zsh: Add to ~/.bashrc or ~/.zshrc:")
            report.append("    export MESA_DIR=/path/to/mesa")
            report.append("    export MESASDK_ROOT=/path/to/mesasdk")
            report.append("  - For csh/tcsh: Add to ~/.cshrc:")
            report.append("    setenv MESA_DIR /path/to/mesa")
            report.append("    setenv MESASDK_ROOT /path/to/mesasdk")
        else:
            report.append("  The environment variables are set, but the directories don't exist.")
            report.append("  Check that MESA is properly installed and the paths are correct.")
    report.append("")
    
    # Python Modules
    report.append(colorize("PYTHON MODULES", Colors.HEADER))
    missing_modules = []
    version_issues = []
    
    for module in results["python_modules"]:
        if module["installed"]:
            if module["meets_version"] == False:
                status = colorize("VERSION TOO OLD", Colors.YELLOW)
                version_issues.append(module)
            else:
                status = colorize("INSTALLED", Colors.GREEN)
        else:
            status = colorize("MISSING", Colors.RED)
            missing_modules.append(module)
        
        version_str = f" (v{module['version']})" if module["version"] else ""
        report.append(f"{module['name']}{version_str}: {status}")
    
    if missing_modules or version_issues:
        report.append(colorize("\nAction Required:", Colors.YELLOW))
        
        if missing_modules:
            report.append("  Install missing modules with pip:")
            pip_cmd = "python -m pip install " + " ".join(m["pip_name"] for m in missing_modules)
            report.append(f"  {pip_cmd}")
        
        if version_issues:
            report.append("  Update modules with outdated versions:")
            pip_cmd = "python -m pip install --upgrade " + " ".join(m["pip_name"] for m in version_issues)
            report.append(f"  {pip_cmd}")
    report.append("")
    
    # Command Line Tools
    report.append(colorize("COMMAND LINE TOOLS", Colors.HEADER))
    missing_tools = []
    
    for tool in results["command_line_tools"]:
        if tool["installed"]:
            status = colorize("INSTALLED", Colors.GREEN)
        else:
            status = colorize("MISSING", Colors.RED)
            missing_tools.append(tool)
        
        version_str = f" (v{tool['version']})" if tool["version"] else ""
        report.append(f"{tool['name']}{version_str}: {status}")
    
    if missing_tools:
        report.append(colorize("\nAction Required:", Colors.YELLOW))
        report.append("  Install missing command line tools:")
        
        for tool in missing_tools:
            if tool["name"] == "gfortran":
                report.append(colorize("  The MESA SDK should provide gfortran:", Colors.YELLOW))
                report.append("  - Ensure your MESASDK is properly installed")
                report.append("  - Make sure you've sourced the MESA SDK environment:")
                if results["system_info"]["os"] == "Linux" or results["system_info"]["os"] == "Darwin":
                    report.append("    source $MESASDK_ROOT/bin/mesasdk_init.[b]sh")
                report.append("  - If you need to install MESA SDK, visit:")
                report.append("    https://docs.mesastar.org/en/release-r23.05.1/installation.html")
            else:
                report.append(f"  - Install {tool['name']} for your system")
    report.append("")
    
    # Batch Directory Structure
    report.append(colorize("BATCH DIRECTORY STRUCTURE", Colors.HEADER))
    
    # Check subdirectories
    missing_dirs = []
    for dirname, exists in results["batch_directories"].items():
        if exists:
            status = colorize("EXISTS", Colors.GREEN)
        else:
            status = colorize("MISSING", Colors.RED)
            missing_dirs.append(dirname)
        report.append(f"{dirname}/: {status}")
    
    if missing_dirs:
        report.append(colorize("\nAction Required:", Colors.YELLOW))
        report.append("  Create the missing directories:")
        for dirname in missing_dirs:
            report.append(f"  - mkdir -p {dirname}")
    
    # Overall status
    report.append("")
    report.append(colorize("="*80, Colors.BOLD))
    
    all_good = (
        results["mesa_environment"]["properly_set"] and
        all(m["installed"] and (m["meets_version"] != False) for m in results["python_modules"]) and
        all(t["installed"] for t in results["command_line_tools"]) and
        all(results["batch_directories"].values())
    )
    
    if all_good:
        report.append(colorize(" ALL DEPENDENCIES SATISFIED! YOU'RE READY TO RUN BATCH SIMULATIONS! ", Colors.GREEN).center(80))
    else:
        report.append(colorize(" MISSING DEPENDENCIES DETECTED! PLEASE INSTALL THEM BEFORE PROCEEDING. ", Colors.YELLOW).center(80))
    
    report.append(colorize("="*80, Colors.BOLD))
    
    return "\n".join(report)

def main():
    results = check_all_dependencies()
    report = generate_report(results)
    print(report)

if __name__ == "__main__":
    main()
