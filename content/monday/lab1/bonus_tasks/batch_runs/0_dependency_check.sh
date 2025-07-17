#!/bin/bash
# dependency_checker.sh
#
# A shell script to check dependencies required for MESA batch_runs functionality.
# Produces a formatted terminal report showing installed and missing dependencies.

# Define color codes for terminal output
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;36m"
PURPLE="\033[0;35m"
RESET="\033[0m"

# Check if terminal supports colors
if [ -t 1 ]; then
    USE_COLORS=true
else
    USE_COLORS=false
fi

colorize() {
    local text="$1"
    local color="$2"
    
    if [ "$USE_COLORS" = true ]; then
        echo -e "${color}${text}${RESET}"
    else
        echo "$text"
    fi
}

check_python_module() {
    local module_name="$1"
    local min_version="$2"
    local installed=false
    local version=""
    
    # Check if module is installed
    if python3 -c "import $module_name" &>/dev/null; then
        installed=true
        
        # Get module version
        version=$(python3 -c "import $module_name; print(getattr($module_name, '__version__', 'unknown'))" 2>/dev/null)
        if [ "$version" = "unknown" ]; then
            # Try another common version attribute
            version=$(python3 -c "import $module_name; print(getattr($module_name, 'version', 'unknown'))" 2>/dev/null)
        fi
    fi
    
    # Return results
    echo "$installed:$version"
}

check_command() {
    local command_name="$1"
    local version_flag="$2"
    local installed=false
    local version=""
    
    # Check if command exists
    if command -v "$command_name" &>/dev/null; then
        installed=true
        
        # Get version
        if [ -n "$version_flag" ]; then
            version_output=$("$command_name" "$version_flag" 2>&1 | head -n 1)
            # Extract version number
            version=$(echo "$version_output" | grep -o -E '[0-9]+(\.[0-9]+)+' | head -n 1)
        fi
    fi
    
    # Return results
    echo "$installed:$version"
}

check_mesa_environment() {
    local mesa_dir="${MESA_DIR:-}"
    local mesasdk_root="${MESASDK_ROOT:-}"
    local mesa_threads="${OMP_NUM_THREADS:-}"
    local properly_set=false
    
    if [ -n "$mesa_dir" ] && [ -n "$mesasdk_root" ]; then
        if [ -d "$mesa_dir" ] && [ -d "$mesasdk_root" ]; then
            properly_set=true
        fi
    fi
    
    # Return results
    echo "$properly_set:$mesa_dir:$mesasdk_root:$mesa_threads"
}

check_batch_directories() {
    local result=""
    
    # Check required directories
    for dir in "../runs" "../batch_inlists"; do
        if [ -d "$dir" ]; then
            result="${result}${dir}:true "
        else
            result="${result}${dir}:false "
        fi
    done
    
    # Return results
    echo "$result"
}

# Print header
print_header() {
    local text="$1"
    printf "\n%s\n" "$(colorize "$text" "$PURPLE")"
}

# Print report section header
print_section_header() {
    local text="$1"
    printf "\n%s\n" "$(colorize "$text" "$BLUE")"
}

# Main function to generate the report
generate_report() {
    # Header
    echo "$(colorize "================================================================" "$BOLD")"
    echo "$(colorize "              MESA BATCH RUNS DEPENDENCY CHECKER               " "$BOLD")"
    echo "$(colorize "================================================================" "$BOLD")"
    
    # System Information
    print_section_header "SYSTEM INFORMATION"
    echo "Python Version: $(python3 --version 2>&1 | awk '{print $2}')"
    echo "Operating System: $(uname -s) $(uname -r)"
    echo "Architecture: $(uname -m)"
    
    # MESA Environment
    print_section_header "MESA ENVIRONMENT"
    local mesa_env=$(check_mesa_environment)
    local properly_set=$(echo "$mesa_env" | cut -d ':' -f 1)
    local mesa_dir=$(echo "$mesa_env" | cut -d ':' -f 2)
    local mesasdk_root=$(echo "$mesa_env" | cut -d ':' -f 3)
    local mesa_threads=$(echo "$mesa_env" | cut -d ':' -f 4)
    
    if [ "$properly_set" = "true" ]; then
        echo "Status: $(colorize "PROPERLY SET" "$GREEN")"
    else
        echo "Status: $(colorize "NOT PROPERLY SET" "$RED")"
    fi
    
    echo "MESA_DIR: ${mesa_dir:-Not set}"
    echo "MESASDK_ROOT: ${mesasdk_root:-Not set}"
    echo "MESA #Threads: ${mesa_threads:-Not set}"
    
    if [ "$properly_set" != "true" ]; then
        echo
        echo "$(colorize "Action Required:" "$YELLOW")"
        if [ -z "$mesa_dir" ] || [ -z "$mesasdk_root" ]; then
            echo "  Set the required environment variables in your shell:"
            echo "  - For bash/zsh: Add to ~/.bashrc or ~/.zshrc:"
            echo "    export MESA_DIR=/path/to/mesa"
            echo "    export MESASDK_ROOT=/path/to/mesasdk"
            echo "  - For csh/tcsh: Add to ~/.cshrc:"
            echo "    setenv MESA_DIR /path/to/mesa"
            echo "    setenv MESASDK_ROOT /path/to/mesasdk"
        else
            echo "  The environment variables are set, but the directories don't exist."
            echo "  Check that MESA is properly installed and the paths are correct."
        fi
    fi
    
    # Python Modules
    print_section_header "PYTHON MODULES"
    local missing_modules=""
    
    # List of modules to check
    local modules=("numpy:1.17.0" "matplotlib:3.0.0" "pandas:1.0.0" "mesa_reader:" "scipy:1.0.0" "PIL:7.0.0")
    
    for module_spec in "${modules[@]}"; do
        local module_name=$(echo "$module_spec" | cut -d ':' -f 1)
        local min_version=$(echo "$module_spec" | cut -d ':' -f 2)
        local pip_name="$module_name"
        
        # Special cases
        if [ "$module_name" = "PIL" ]; then
            pip_name="Pillow"
        fi
        
        local check_result=$(check_python_module "$module_name" "$min_version")
        local installed=$(echo "$check_result" | cut -d ':' -f 1)
        local version=$(echo "$check_result" | cut -d ':' -f 2)
        
        local version_str=""
        if [ -n "$version" ] && [ "$version" != "unknown" ]; then
            version_str=" (v$version)"
        fi
        
        if [ "$installed" = "true" ]; then
            echo "$module_name$version_str: $(colorize "INSTALLED" "$GREEN")"
        else
            echo "$module_name: $(colorize "MISSING" "$RED")"
            missing_modules="$missing_modules $pip_name"
        fi
    done
    
    if [ -n "$missing_modules" ]; then
        echo
        echo "$(colorize "Action Required:" "$YELLOW")"
        echo "  Install missing modules with pip:"
        echo "  python -m pip install$missing_modules"
    fi
    
    # Command Line Tools
    print_section_header "COMMAND LINE TOOLS"
    local missing_tools=""
    
    # Check python3
    local python_check=$(check_command "python3" "--version")
    local python_installed=$(echo "$python_check" | cut -d ':' -f 1)
    local python_version=$(echo "$python_check" | cut -d ':' -f 2)
    
    if [ "$python_installed" = "true" ]; then
        echo "python3 (v$python_version): $(colorize "INSTALLED" "$GREEN")"
    else
        echo "python3: $(colorize "MISSING" "$RED")"
        missing_tools="$missing_tools python3"
    fi
    
    # Check gfortran
    local gfortran_check=$(check_command "gfortran" "--version")
    local gfortran_installed=$(echo "$gfortran_check" | cut -d ':' -f 1)
    local gfortran_version=$(echo "$gfortran_check" | cut -d ':' -f 2)
    
    if [ "$gfortran_installed" = "true" ]; then
        echo "gfortran (v$gfortran_version): $(colorize "INSTALLED" "$GREEN")"
    else
        echo "gfortran: $(colorize "MISSING" "$RED")"
        missing_tools="$missing_tools gfortran"
    fi
    
    if [[ "$missing_tools" == *"gfortran"* ]]; then
        echo
        echo "$(colorize "Action Required:" "$YELLOW")"
        echo "$(colorize "  The MESA SDK should provide gfortran:" "$YELLOW")"
        echo "  - Ensure your MESASDK is properly installed"
        echo "  - Make sure you've sourced the MESA SDK environment:"
        echo "    source \$MESASDK_ROOT/bin/mesasdk_init.[b]sh"
        echo "  - If you need to install MESA SDK, visit:"
        echo "    https://docs.mesastar.org/en/release-r23.05.1/installation.html"
    fi
    
    # Batch Directory Structure
    print_section_header "BATCH DIRECTORY STRUCTURE"
    local batch_dirs=$(check_batch_directories)
    local missing_dirs=""
    
    for dir_check in $batch_dirs; do
        local dir_name=$(echo "$dir_check" | cut -d ':' -f 1)
        local dir_exists=$(echo "$dir_check" | cut -d ':' -f 2)
        
        if [ "$dir_exists" = "true" ]; then
            echo "$dir_name/: $(colorize "EXISTS" "$GREEN")"
        else
            echo "$dir_name/: $(colorize "MISSING" "$RED")"
            missing_dirs="$missing_dirs $dir_name"
        fi
    done
    
    if [ -n "$missing_dirs" ]; then
        echo
        echo "$(colorize "Action Required:" "$YELLOW")"
        echo "  Create the missing directories:"
        for dir in $missing_dirs; do
            echo "  - mkdir -p $dir"
        done
    fi
    
    # Overall status
    echo
    echo "$(colorize "================================================================" "$BOLD")"
    
    # Determine if all dependencies are satisfied
    local all_good=true
    
    if [ "$properly_set" != "true" ]; then
        all_good=false
    fi
    
    if [ -n "$missing_modules" ]; then
        all_good=false
    fi
    
    if [[ "$missing_tools" == *"python3"* ]]; then
        all_good=false
    fi
    
    if [ -n "$missing_dirs" ]; then
        all_good=false
    fi
    
    if [ "$all_good" = true ]; then
        echo "$(colorize " ALL DEPENDENCIES SATISFIED! YOU'RE READY TO RUN BATCH SIMULATIONS! " "$GREEN")"
    else
        echo "$(colorize " MISSING DEPENDENCIES DETECTED! PLEASE INSTALL THEM BEFORE PROCEEDING. " "$YELLOW")"
    fi
    
    echo "$(colorize "================================================================" "$BOLD")"
}

# Execute the report generation
generate_report
