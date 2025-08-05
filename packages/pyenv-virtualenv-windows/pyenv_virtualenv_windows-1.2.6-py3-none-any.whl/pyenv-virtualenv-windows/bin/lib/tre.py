##
#  @package tre
#  @file tre.py
#  @author Michael Paul Korthals
#  @date 2025-07-10
#  @version 1.0.0
#  @copyright © 2025 Michael Paul Korthals. All rights reserved.
#  See License details in the documentation.
#
#  Library to output the project properties "pyenv-virtualenv"
#  folder tree in the CLI terminal.
#  I derived this code for "pyenv-virtualenv" from a StackOverflow article.
#  Many thanks to its contributor.
#  @see https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
#

# --- IMPORTS ----------------------------------------------------------

# Python
from itertools import islice
from pathlib import Path
import sys

# Community
# (None)

# My
try:
	# noinspection PyUnresolvedReferences
	import lib.log as log
except ImportError():
	try:
		# noinspection PyUnresolvedReferences
		import log
	except ImportError():
		# noinspection PyUnresolvedReferences
		import log

# --- GLOBAL VARIABLES -------------------------------------------------

space =  '\x1b[94m    \x1b[0m'
branch = '\x1b[94m│   \x1b[0m'
tee =    '\x1b[94m├───\x1b[0m'
last =   '\x1b[94m└───\x1b[0m'

# --- HELPER -----------------------------------------------------------

## Get the content of project property file.
#
# @param file_path Path to project property file.
# @return Text, which the file is containing or empty string in case of error.
def getProjectPropertyFileStr(file_path: str) -> str:
	result = ''
	# noinspection PyBroadException
	try:
		with open(file_path, 'r') as f:
			result = f.read().strip()
		return result
	except:
		log.error(sys.exc_info())
		return ''

## Given a directory path, print a visual tree structure.
# Output and highlight the content of 'pyenv-virtualenv'
# project property files with colors:
#   * LIGHT CYAN: Python version.
#   * LIGHT YELLOW: Virtual environment name.
#
#  @param root_path Folder path, from which the tree will be parsed.
#  @param recursion_level Max recursion level to parse.
#  Default: -1 = unlimited recursion.
#  @param limit_to_directories Flag to permit parsing for folders only.
#  Default: False = parse for both, files and folders
#  @param length_limit Max. output length of the tree in lines.
#  Default: 1000.
#  @param exclude List of folder names to exclude.
#  Default empty list = nothing to exclude.
def tree(
	root_path: (Path, str),
	recursion_level: int = -1,
	limit_to_directories: bool = False,
	length_limit: int = 1000,
	exclude: tuple = ()
):
	# Accept type "str" coercible to "Path"
	if isinstance(root_path, str):
		root_path = Path(root_path)
	# Initialize
	files = 0
	directories = 0

	def is_junction(path: str) -> bool:
		import os
		try:
			return bool(os.readlink(path))
		except OSError:
			return False

	def inner(
		dir_path: Path,
		prefix: str= '',
		level: int = -1,
		excl: tuple = ()
	):
		nonlocal files, directories
		if not level:
			return # 0, stop iterating
		# Scan for files and folders Path objects
		if limit_to_directories:
			objects = dir_path.iterdir()
			contents = [d for d in objects if d.is_dir()]
			contents1 = list(objects)
		else:
			contents = list(dir_path.iterdir())
			contents1 = contents
		# Detect file ".tree-excludes" in files
		excl1 = excl
		for content in contents1:
			if content.is_file() and (content.name == '.tree-excludes'):
				with open(content, 'r') as f:
					excl1 = eval(f.read())
				if content not in contents:
					contents.insert(0, content)
				break
			# End if
		# End for
		pointers = [tee] * (len(contents) - 1) + [last]
		for pointer, path in zip(pointers, contents):
			if path.is_dir():
				# Exclude spam folders
				excluded = False
				for item in excl1:
					if path.parts[-1] == item:
						excluded = True
						break
					# End if
				# End for
				if excluded: continue
				# OUTPUT: colorized directory
				name = path.name
				if (
					(hasattr(path, 'is_junction') and path.is_junction())  # Python 3.12+
					or
					(is_junction(str(path)))  # Python 3.11-
				):
					name = '\x1b[105m {} \x1b[0m \x1b[95m→\x1b[0m \x1b[104m {} \x1b[0m'.format(
						name,
						str(path.readlink()).split('\\\\?\\')[-1]
					)
				else:  # Is directory
					name = '\x1b[104m {} \x1b[0m'.format(name)
				yield prefix + pointer + name
				directories += 1
				extension = branch if pointer == tee else space
				# OUTPUT: path recursively
				yield from inner(
					path,
					prefix=prefix+extension,
					level=level - 1,
					excl=excl1
				)
			elif not limit_to_directories:
				# OUTPUT: colorized file
				name = path.name
				if path.is_symlink():
					name1 = '\x1b[95m● {}\x1b[0m'.format(name)
					if name == '.python-version':
						name1 += ' \x1b[96m({})\x1b[0m'.format(
							getProjectPropertyFileStr(str(path))
						)
					elif name == '.python-env':
						name1 += ' \x1b[93m({})\x1b[0m'.format(
							getProjectPropertyFileStr(str(path))
						)
					elif name == '.tree-excludes':
						name1 += ' \x1b[95m{}\x1b[0m'.format(
							getProjectPropertyFileStr(str(path))
						)
					else:
						name1 = '\x1b[95m● {} → \x1b[37m● {}\x1b[0m'.format(
							name,
							str(path.readlink())
						)
				else:  # Is file
					name1 = '\x1b[37m● {}\x1b[0m'.format(name)
					if name == '.python-version':
						name1 += ' \x1b[96m({})\x1b[0m'.format(
							getProjectPropertyFileStr(str(path))
						)
					elif name == '.python-env':
						name1 += ' \x1b[93m({})\x1b[0m'.format(
							getProjectPropertyFileStr(str(path))
						)
					elif name == '.tree-excludes':
						name1 += ' \x1b[95m{}\x1b[0m'.format(
							getProjectPropertyFileStr(str(path))
						)
					else:
						name1 = '\x1b[37m● {}\x1b[0m'.format(name)
				yield prefix + pointer + name1
				files += 1

	# Output the root directory path in the beginning
	print('\x1b[104m {} \x1b[0m'.format(str(root_path)))
	# Exclude spam folders
	for excl_item in exclude:
		if root_path.parts[-1] == excl_item:
			return
	# Iterate through the folder tree
	iterator = inner(
		root_path,
		level=recursion_level,
		excl=exclude
	)
	# OUTPUT: folder tree
	for line in islice(iterator, length_limit):
		print(line)
	if next(iterator, None):
		# Obey to the length_limit
		print('... length_limit, {}, reached, counted:'.format(length_limit))
	# OUTPUT: statistics
	print(
		'\n{} directories'.format(directories) + (
			', {} files'.format(files) if files else ''
		)
	)


# --- END OF CODE ------------------------------------------------------