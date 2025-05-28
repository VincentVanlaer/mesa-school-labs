#!/bin/bash
# make_batch.sh - Script to create batch inlists from a CSV file of parameters
# Improved version with better handling of missing parameters

# Check if CSV file is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <csv_file>"
    exit 1
fi

CSV_FILE=$1
BATCH_DIR="../batch_inlists"
TEMPLATE_INLIST="../../inlist_project"

# Create batch directory if it doesn't exist
mkdir -p "$BATCH_DIR"

# Ask user about pgstar settings
read -p "Do you want to enable pgstar for batch runs? (yes/no): " enable_pgstar
if [[ "$enable_pgstar" =~ ^[Yy][Ee]?[Ss]?$ ]]; then
    pgstar_setting="pgstar_flag = .true."
else
    pgstar_setting="pgstar_flag = .false."
fi

# Helper function to check if pattern exists in file
pattern_exists() {
    grep -q "$1" "$2"
    return $?
}

# Helper function to add parameter if missing
add_parameter() {
    local file=$1
    local section=$2
    local parameter=$3
    local value=$4
    local comment=$5
    
    if pattern_exists "$section" "$file"; then
        # Add parameter after section marker
        sed -i "/$section/a \ \ \ \ $parameter = $value $comment" "$file"
    else
        # Section doesn't exist, create it before controls
        if [ "$section" = "&kap" ]; then
            sed -i "/&controls/i \\$section\\n    ! kap options\\n    $parameter = $value $comment\\n/ ! end of kap namelist\\n" "$file"
        elif [ "$section" = "&star_job" ]; then
            # Add star_job at the beginning of the file
            sed -i "1i \\$section\\n    $parameter = $value $comment\\n/ ! end of star_job namelist\\n" "$file"
        fi
    fi
}

# Skip header line and process each row
tail -n +2 "$CSV_FILE" | while IFS=, read -r name mass metallicity scheme fov f0 rest; do
    # Skip empty lines or lines with missing data
    if [ -z "$mass" ] || [ -z "$metallicity" ]; then
        continue
    fi

    # Clean up input values by trimming whitespace
    mass=$(echo "$mass" | xargs)
    metallicity=$(echo "$metallicity" | xargs)
    scheme=$(echo "$scheme" | xargs)
    fov=$(echo "$fov" | xargs)
    f0=$(echo "$f0" | xargs)

    # Create a descriptive filename encoding the parameters
    if [ "$scheme" == "no overshooting" ] || [ "$scheme" == "none" ] || [ "$scheme" == "no overshoot" ]; then
        OUTFILE="${BATCH_DIR}/inlist_M${mass}_Z${metallicity}_noovs.inp"
        ovs_option="none"
    else
        OUTFILE="${BATCH_DIR}/inlist_M${mass}_Z${metallicity}_${scheme}_fov${fov}_f0${f0}.inp"
        ovs_option="$scheme"
    fi

    echo "Creating $OUTFILE..."

    # Copy template and modify
    cp "$TEMPLATE_INLIST" "$OUTFILE"
    
    # Handle parameters that might not exist
    # For initial_mass
    if pattern_exists "initial_mass" "$OUTFILE"; then
        sed -i "s/initial_mass\s*=\s*[0-9]*\(\.[0-9]*\)\{0,1\}/initial_mass = $mass/" "$OUTFILE"
    else
        if pattern_exists "! starting specifications" "$OUTFILE"; then
            sed -i "/! starting specifications/a \ \ \ \ initial_mass = $mass ! in Msun units" "$OUTFILE"
        else
            sed -i "/&controls/a \\n    ! starting specifications\\n    initial_mass = $mass ! in Msun units" "$OUTFILE"
        fi
    fi
    
    # For initial_z
    if pattern_exists "initial_z" "$OUTFILE"; then
        sed -i "s/initial_z\s*=\s*[0-9]*\(\.[0-9]*\)\{0,1\}/initial_z = $metallicity/" "$OUTFILE"
    else
        if pattern_exists "initial_mass" "$OUTFILE"; then
            sed -i "/initial_mass/a \ \ \ \ initial_z = $metallicity ! initial metal mass fraction" "$OUTFILE"
        else
            add_parameter "$OUTFILE" "&controls" "initial_z" "$metallicity" "! initial metal mass fraction"
        fi
    fi
    
    # For Zbase
    if pattern_exists "Zbase" "$OUTFILE"; then
        sed -i "s/Zbase\s*=\s*[0-9]*\(\.[0-9]*\)\{0,1\}/Zbase = $metallicity/" "$OUTFILE"
    else
        add_parameter "$OUTFILE" "&kap" "Zbase" "$metallicity" ""
    fi
    
    # For pgstar_flag
    if pattern_exists "pgstar_flag" "$OUTFILE"; then
        sed -i "s/pgstar_flag\s*=\s*\.[a-z]\+\./$pgstar_setting/" "$OUTFILE"
    else
        add_parameter "$OUTFILE" "&star_job" "pgstar_flag" "${pgstar_setting#*=}" ""
    fi
    
    # Handle save_model_filename
    model_filename="M${mass}_Z${metallicity}"
    if [ "$ovs_option" != "none" ]; then
        model_filename="${model_filename}_${scheme}_fov${fov}_f0${f0}"
    else
        model_filename="${model_filename}_noovs"
    fi
    
    if pattern_exists "save_model_filename" "$OUTFILE"; then
        sed -i "s/save_model_filename\s*=\s*'.*'/save_model_filename = '${model_filename}.mod'/" "$OUTFILE"
    else
        # Add save model options
        if pattern_exists "save_model_when_terminate" "$OUTFILE"; then
            sed -i "/save_model_when_terminate/a \ \ \ \ save_model_filename = '${model_filename}.mod'" "$OUTFILE"
        else
            add_parameter "$OUTFILE" "&star_job" "save_model_when_terminate" ".true." ""
            add_parameter "$OUTFILE" "&star_job" "save_model_filename" "'${model_filename}.mod'" ""
        fi
    fi
    
    # Handle overshoot parameters
    if [ "$ovs_option" == "none" ]; then
        # Comment out all overshoot lines if they exist
        if pattern_exists "overshoot_scheme" "$OUTFILE" || pattern_exists "overshoot_f(" "$OUTFILE"; then
            sed -i 's/^[[:space:]]*overshoot_scheme/!     overshoot_scheme/g' "$OUTFILE"
            sed -i 's/^[[:space:]]*overshoot_zone_type/!     overshoot_zone_type/g' "$OUTFILE"
            sed -i 's/^[[:space:]]*overshoot_zone_loc/!     overshoot_zone_loc/g' "$OUTFILE"
            sed -i 's/^[[:space:]]*overshoot_bdy_loc/!     overshoot_bdy_loc/g' "$OUTFILE"
            sed -i 's/^[[:space:]]*overshoot_f(/!     overshoot_f(/g' "$OUTFILE"
            sed -i 's/^[[:space:]]*overshoot_f0(/!     overshoot_f0(/g' "$OUTFILE"
        fi
    else
        # Check if overshooting parameters exist
        if pattern_exists "overshoot_scheme" "$OUTFILE" || pattern_exists "!.*overshoot_scheme" "$OUTFILE"; then
            # Update overshoot parameters (uncomment if commented)
            sed -i 's/^[[:space:]]*![[:space:]]*overshoot_scheme/     overshoot_scheme/g' "$OUTFILE"
            sed -i 's/^[[:space:]]*![[:space:]]*overshoot_zone_type/     overshoot_zone_type/g' "$OUTFILE"
            sed -i 's/^[[:space:]]*![[:space:]]*overshoot_zone_loc/     overshoot_zone_loc/g' "$OUTFILE"
            sed -i 's/^[[:space:]]*![[:space:]]*overshoot_bdy_loc/     overshoot_bdy_loc/g' "$OUTFILE"
            sed -i 's/^[[:space:]]*![[:space:]]*overshoot_f(/     overshoot_f(/g' "$OUTFILE"
            sed -i 's/^[[:space:]]*![[:space:]]*overshoot_f0(/     overshoot_f0(/g' "$OUTFILE"
            
            # Update parameter values
            sed -i "s/overshoot_scheme(1)\s*=\s*'.*'/overshoot_scheme(1) = '$scheme'/" "$OUTFILE"
            sed -i "s/overshoot_zone_type(1)\s*=\s*'.*'/overshoot_zone_type(1) = 'any'/" "$OUTFILE"
            sed -i "s/overshoot_zone_loc(1)\s*=\s*'.*'/overshoot_zone_loc(1) = 'core'/" "$OUTFILE"
            sed -i "s/overshoot_bdy_loc(1)\s*=\s*'.*'/overshoot_bdy_loc(1) = 'top'/" "$OUTFILE"
            sed -i "s/overshoot_f(1)\s*=\s*[0-9]*\(\.[0-9]*\)\{0,1\}/overshoot_f(1) = $fov/" "$OUTFILE"
            sed -i "s/overshoot_f0(1)\s*=\s*[0-9]*\(\.[0-9]*\)\{0,1\}/overshoot_f0(1) = $f0/" "$OUTFILE"
        else
            # Add new overshoot parameters section
            if pattern_exists "! mixing" "$OUTFILE"; then
                # Add to existing mixing section
                sed -i "/! mixing/a \ \ \ \ overshoot_scheme(1) = '$scheme'\\n    overshoot_zone_type(1) = 'any'\\n    overshoot_zone_loc(1) = 'core'\\n    overshoot_bdy_loc(1) = 'top'\\n    overshoot_f(1) = $fov\\n    overshoot_f0(1) = $f0" "$OUTFILE"
            else
                # Look for a good place to add mixing section
                if pattern_exists "! timesteps" "$OUTFILE"; then
                    sed -i "/! timesteps/i \ \ ! mixing\\n    overshoot_scheme(1) = '$scheme'\\n    overshoot_zone_type(1) = 'any'\\n    overshoot_zone_loc(1) = 'core'\\n    overshoot_bdy_loc(1) = 'top'\\n    overshoot_f(1) = $fov\\n    overshoot_f0(1) = $f0\\n" "$OUTFILE"
                elif pattern_exists "! mesh" "$OUTFILE"; then
                    sed -i "/! mesh/i \ \ ! mixing\\n    overshoot_scheme(1) = '$scheme'\\n    overshoot_zone_type(1) = 'any'\\n    overshoot_zone_loc(1) = 'core'\\n    overshoot_bdy_loc(1) = 'top'\\n    overshoot_f(1) = $fov\\n    overshoot_f0(1) = $f0\\n" "$OUTFILE"
                elif pattern_exists "! solver" "$OUTFILE"; then
                    sed -i "/! solver/i \ \ ! mixing\\n    overshoot_scheme(1) = '$scheme'\\n    overshoot_zone_type(1) = 'any'\\n    overshoot_zone_loc(1) = 'core'\\n    overshoot_bdy_loc(1) = 'top'\\n    overshoot_f(1) = $fov\\n    overshoot_f0(1) = $f0\\n" "$OUTFILE"
                else
                    # Add before end of controls
                    sed -i "/\/ ! end of controls namelist/i \ \ ! mixing\\n    overshoot_scheme(1) = '$scheme'\\n    overshoot_zone_type(1) = 'any'\\n    overshoot_zone_loc(1) = 'core'\\n    overshoot_bdy_loc(1) = 'top'\\n    overshoot_f(1) = $fov\\n    overshoot_f0(1) = $f0\\n" "$OUTFILE"
                fi
            fi
        fi
    fi
done

echo "Batch inlist creation completed."