#!/bin/bash

# Parse arguments
OPTS=$(getopt -o ""   --long dataset_path:,mcmicro_template:,markers_csv:,params_yml:   -n 'submission.sh' -- "$@")

if [ $? != 0 ]; then
  echo "Failed parsing options." >&2
  exit 1
fi

eval set -- "$OPTS"

dataset_path=""
mcmicro_template=""
markers_csv=""
params_yml=""

# Extract arguments
while true; do
  case "$1" in
    --dataset_path ) dataset_path="$2"; shift 2 ;;
    --mcmicro_template ) mcmicro_template="$2"; shift 2 ;;
    --markers_csv ) markers_csv="$2"; shift 2 ;;
    --params_yml ) params_yml="$2"; shift 2 ;;
    -- ) shift; break ;;
    * ) break ;;
  esac
done

# Check dataset_path
if [[ -z "$dataset_path" || ! -d "$dataset_path" ]]; then
  echo "Error: dataset_path is required and must exist: $dataset_path"
  exit 1
fi

# Assign default paths if optional ones are not provided
if [[ -z "$mcmicro_template" ]]; then
  mcmicro_template="${dataset_path%/}/mcmicro_template.sh"
  echo "No mcmicro_template provided. Using default: $mcmicro_template"
fi

if [[ -z "$markers_csv" ]]; then
  markers_csv="${dataset_path%/}/markers.csv"
  echo "No markers_csv provided. Using default: $markers_csv"
fi

if [[ -z "$params_yml" ]]; then
  params_yml="${dataset_path%/}/params.yml"
  echo "No params_yml provided. Using default: $params_yml"
fi

# Check that all necessary files exist now
if [[ ! -f "$mcmicro_template" ]]; then
  echo "Error: mcmicro_template not found at $mcmicro_template"
  exit 1
fi

if [[ ! -f "$markers_csv" ]]; then
  echo "Error: markers_csv not found at $markers_csv"
  exit 1
fi

if [[ ! -f "$params_yml" ]]; then
  echo "Error: params_yml not found at $params_yml"
  exit 1
fi

# Submit jobs for each raw folder
for raw_folder in "$dataset_path"/raw/*_frames; do
  if [ -d "$raw_folder" ]; then
    echo "Submitting job for: $raw_folder"
    sbatch "$mcmicro_template" "$raw_folder"
  fi
done
