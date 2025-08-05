# Windows PowerShell Script to create a
# virtual environment directory junction.
#
# Dependencies:
# (None)
#
# © 2025 Michael Paul Korthals. All rights reserved.
# For legal details see documentation.
#
# 2025-07-31
#
# This script is located in the 'pyenv-virtualenv' plugin root directory.
#
# It has 2 command line arguments:
#   1. Absolute/relative path to the junction.
#   2. Absolute/relative path to its target.
#
# It will be called by 'pyenv-virtualenv' its parent folder.
#
# The script returns RC = 0 or another value in case of error.

$rc = 0
# Check if this script is running as 'Administrator'
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$as_admin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Get/Check argument 1 (path)
try { 
	$link_path = $args[0].Trim() 
} catch {
	$rc = 1
	Write-Host "$([char]27)[91mERROR    Missing argument 1 (path) (RC = $rc).$([char]27)[0m"
	Write-Host "$([char]27)[37mINFO     To define a directory junction, assign 2 arguments 'path' and 'target' as absolute paths.$([char]27)[0m"
	exit $rc
}

# Get/Check argument 2 (target)
try { 
	$link_target = $args[1].Trim() 
} catch {
	$rc = 1
	Write-Host "$([char]27)[91mERROR    Missing argument 2 (target) (RC = $rc).$([char]27)[0m"
	Write-Host "$([char]27)[37mINFO     To define a directory junction, assign 2 arguments 'path' and 'target' as absolute paths.$([char]27)[0m"
	exit $rc
}

# Make symbolic link to patched 'pyenv.bat'
if ($as_admin) {
	Write-Host "$([char]27)[37mINFO     Writing directory junction: $([char]27)[0m"
	Write-Host "$([char]27)[37mINFO       * Path: '$link_path'.$([char]27)[0m"
	Write-Host "$([char]27)[37mINFO       * Target: '$link_target'.$([char]27)[0m"
	Write-Host "$([char]27)[37mINFO     This could take some seconds ...$([char]27)[0m"
	try {
		New-Item -ItemType Junction -Path "$link_path" -Target "$link_target" | Out-Null
	} catch {
		$rc = 1
		Write-Host "$([char]27)[91mERROR    Unexpectedly cannot write junction (RC = $rc).$([char]27)[0m"
		Write-Host "$([char]27)[37mINFO     Analyze/configure/repair the situation, why a script running as 'Administrator' fails. Then try again.$([char]27)[0m"
		exit $rc
	}
	Write-Host "$([char]27)[37mINFO     Done.$([char]27)[0m"
} else {
	$rc = 13
	Write-Host "$([char]27)[91mERROR    Insufficient privileges. (RC = $rc).$([char]27)[0m"
	Write-Host "$([char]27)[37mINFO     To create a junction, you must call this script in a console terminal with 'Administrator' privileges. Then try again.$([char]27)[0m"
	exit $rc
}

# Return error level
exit $rc
 

# --- END OF CODE ------------------------------------------------------

