import subprocess
import os
import platform
from collections import namedtuple

GetCleftResult = namedtuple('GetCleftResult', ['stdout', 'stderr', 'returncode', 'file_path_dict'])


class GetCleftError(Exception):
    """Custom exception for errors related to the GetCleft."""
    pass


def run_getcleft(
    pdb_file: str,
    min_sphere_radius: float = None,
    max_sphere_radius: float = None,
    output_het_atoms: bool = False,
    output_all_het_atoms: bool = False,
    chain_ids: list = None, # List of strings e.g. ['A', 'B']
    num_clefts: int = 5,
    anchor_residue_specifier: str = None, # e.g., "LIG123A-"
    anchor_mode: str = None, # 'all', 'interacting', or 'both'
    include_calpha: bool = False,
    include_cbeta: bool = False,
    include_all_residue_atoms: bool = False,
    output_spheres: bool = True,
    output_clf: bool = False,
    contact_threshold: float = None,
    output_base: str = None,
    verbose: bool = True       
):
    """
    Python function to prepare arguments and run the GetCleft executable.

    This function can be imported and used in other Python scripts or packages.

    Args:
        pdb_file (str): PDB filename (e.g., myprotein.pdb).
        min_sphere_radius (float, optional): Min sphere radius. (GetCleft default: 1.50).
        max_sphere_radius (float, optional): Max sphere radius. (GetCleft default: 4.00).
        output_het_atoms (bool, optional): Output hetero group atoms in cleft.
                                         (Corresponds to GetCleft's -h flag). Defaults to False.
        output_all_het_atoms (bool, optional): Output all atoms of hetero groups in cleft.
                                             Defaults to False.
        chain_ids (list, optional): List of chain IDs to be considered (e.g., ['A', 'B']).
                                    If None, GetCleft considers all. Defaults to None.
        num_clefts (int, optional): Maximum number of clefts to be generated. Defaults to 5.
                                    (GetCleft default: 0, meaning all). Defaults to None.
        anchor_residue_specifier (str, optional): Anchor residue/hetero molecule
                                                  (Format: RESNUMCA, e.g., LIG123A- or ---123--).
                                                  Defaults to None.
        anchor_mode (str, optional): Mode for anchor residue. Can be 'all' (outputs all atoms
                                     in selected cleft; Default), 'interacting' (outputs all atoms in contact),
                                     or 'both' (produces two output files).
                                     Corresponds to -a, -i, -b flags of GetCleft. Defaults to None.
        include_calpha (bool, optional): Include C-alpha of residues in certain outputs. Defaults to False.
        include_cbeta (bool, optional): Include C-beta of residues in certain outputs. Defaults to False.
        include_all_residue_atoms (bool, optional): Include all atoms of the residue in certain outputs.
                                                 Defaults to False.
        output_spheres (bool, optional): Output cleft spheres (centre coordinates and radii).
                                       Defaults to True.
        output_clf (bool, optional): Output cleft file (GetCleft default: True). Defaults to False.
        contact_threshold (float, optional): Threshold distance for contact definition.
                                           (GetCleft Default: 5.0). Defaults to None.
        output_base (str, optional): Output full path and filename without extension (e.g. /foo/bar/filename).
                                     Defaults to the folder where the pdb file is located.
        verbose (bool, optional): Output filepaths to files written by GetCleft as a dictionary. Defaults to True.

    Returns:
        GetCleftResult: A namedtuple containing stdout, stderr, the returncode and paths to written files in a
        dictionary (if verbose=True).

    Raises:
        FileNotFoundError: If the GetCleft executable or the input file is not found.
        ValueError: If anchor_mode is provided without anchor_residue_specifier,
                    or if an invalid anchor_mode is given.
        subprocess.CalledProcessError: If GetCleft returns a non-zero exit code.
    """

    # --- Validate executable path ---
    executable_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'GetCleft')
    if platform.system() == 'Windows':
        executable_path += '.exe'
    if not os.path.isfile(executable_path) or not os.access(executable_path, os.X_OK):
        print(f"Error: Executable '{executable_path}' not found or not executable.")
        return
    cmd = [executable_path]

    # Obligatory arguments
    pdb_file = os.path.abspath(pdb_file)
    if not os.path.isfile(pdb_file):
        raise FileNotFoundError(f"Error: File '{pdb_file}' not found.")
    else:
        cmd.extend(["-p", pdb_file])

    # Optional arguments
    if min_sphere_radius is not None:
        cmd.extend(["-l", str(min_sphere_radius)])
    if max_sphere_radius is not None:
        cmd.extend(["-u", str(max_sphere_radius)])

    if output_het_atoms:
        cmd.append("-h")
    if output_all_het_atoms:
        cmd.append("-H")

    if chain_ids:
        for chain_id_val in chain_ids:
            cmd.extend(["-c", str(chain_id_val)])
    if num_clefts is not None:
        cmd.extend(["-t", str(num_clefts)])

    if anchor_residue_specifier:
        if anchor_mode == "all":
            cmd.extend(["-a", anchor_residue_specifier])
        elif anchor_mode == "interacting":
            cmd.extend(["-i", anchor_residue_specifier])
        elif anchor_mode == "both":
            cmd.extend(["-b", anchor_residue_specifier])
        elif anchor_mode is None:
            cmd.extend(["-a", anchor_residue_specifier])
        else:
            raise ValueError(f"Invalid anchor_mode '{anchor_mode}'. Must be 'all', 'interacting', or 'both'.")
    elif anchor_mode:
        raise ValueError("anchor_mode specified without anchor_residue_specifier.")

    if include_calpha:
        cmd.append("-ca")
    if include_cbeta:
        cmd.append("-cb")
    if include_all_residue_atoms:
        cmd.append("-r")
    if output_spheres:
        cmd.append("-s")
    if not output_clf:
        cmd.append("-nc")
    if contact_threshold is not None:
        cmd.extend(["-k", str(contact_threshold)])
    if verbose:
        cmd.append("-v")
    if output_base is not None:
        cmd.extend(["-o", output_base])
    else:
        output_base = os.path.splitext(pdb_file)[0]
        cmd.extend(["-o", output_base])

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        file_path_dict = None
        if verbose:
            file_path_dict = {}
            for line in result.stdout.strip().split('\n'):
                if line:
                    key = line.split(' ')[0]
                    path = line.split(': ')[1].strip()
                    if key not in file_path_dict:
                        file_path_dict[key] = []
                    file_path_dict[key].append(path)

        return GetCleftResult(result.stdout, result.stderr, result.returncode, file_path_dict)

    except FileNotFoundError:
        raise GetCleftError(f"Executable not found at '{executable_path}'.")
    except PermissionError:
        raise GetCleftError(f"Error: Permission denied to execute '{executable_path}'.")
    except subprocess.CalledProcessError as e:
        error_message = (
            f"GetCleft failed with exit code {e.returncode}.\n"
            f"Stderr:\n{e.stderr.strip()}"
        )
        raise GetCleftError(error_message) from e
