#!/usr/bin/env python

# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Creates a human readable file with the list of readers supported by the 
Connector App."""

import argparse
import string
import sys

# List of section titles that should be picked up for forming the USB devices
# list in the file.
CCID_SUPPORTED_READERS_CONFIG_SECTIONS_TO_PICK = ('supported', 'shouldwork')

def load_usb_devices(ccid_supported_readers_file):
  """Parses the specified config containing descriptions of the readers
  supported by CCID.

  Only readers from the sections listed in the
  CCID_SUPPORTED_READERS_CONFIG_SECTIONS_TO_PICK are picked up.

  Args:
    ccid_supported_readers_file: The opened config file containing descriptions
        of the readers supported by CCID.

  Returns list of strings: (name), which are the names of the usb devices.
  """

  # The CCID supported readers config file format is the following.
  #
  # There are several sections, each of which starts with a comment block
  # containing the title of the section (e.g. "supported"), followed by a number
  # of lines containing reader descriptions.
  #
  # The reader description line has the following format:
  # "vendor_id:product_id:name", where vendor_id and product_id are hexadecimal
  # integers.
  #
  # Empty lines should be ignored.
  #
  # Comment lines, which start from the hash character, should also be ignored
  # with the only exception of special-formatted comments containing section
  # titles.

  # Prefix marker used for determining section titles.
  SECTION_HEADER_PREFIX = '# section:'
  # Prefix marker used for determining comment lines.
  COMMENT_PREFIX = '#'

  usb_devices = []
  ignored_usb_devices = []
  current_section = None
  for line in ccid_supported_readers_file:
    if not line.strip():
      # Ignore empty line
      continue
    line = line.strip('\n')
    if line.startswith(SECTION_HEADER_PREFIX):
      # Parse section title line
      current_section = line[len(SECTION_HEADER_PREFIX):].strip()
      if not current_section:
        raise RuntimeError('Failed to extract section title from the CCID '
                           'supported readers config')
      continue
    if line.startswith(COMMENT_PREFIX):
      # Ignore comment line
      continue
    # Parse reader description line
    parts = line.split(':', 2)
    if len(parts) != 3:
      raise RuntimeError('Failed to parse the reader description from the CCID '
                         'supported readers config: "{0}"'.format(line))
    name = parts[2]
    if (name in usb_devices) or (name in ignored_usb_devices):
      continue
    if current_section is None:
      raise RuntimeError('Unexpected reader definition met in the CCID '
                         'supported readers config before any section title')
    if current_section in CCID_SUPPORTED_READERS_CONFIG_SECTIONS_TO_PICK:
      usb_devices.append(name)
    else:
      ignored_usb_devices.append(name)

  if not usb_devices:
    raise RuntimeError('No supported USB devices were extracted from the CCID '
                       'supported readers config')
  print >>sys.stderr, ('Extracted {0} supported USB devices from the CCID '
                       'supported readers config, and ignored {1} '
                       'items.'.format(
                           len(usb_devices), len(ignored_usb_devices)))

  return usb_devices

def create_readers_list(ccid_supported_readers_file):
  usb_devices = load_usb_devices(ccid_supported_readers_file)
  return '\n'.join(sorted(usb_devices))

def main():
  args_parser = argparse.ArgumentParser(
      description="Creates a human readable file with the list of readers "
      "supported by the Connector App.")
  args_parser.add_argument(
      '--ccid-supported-readers-config-path',
      type=argparse.FileType('r'),
      required=True,
      metavar='"path/to/ccid_supported_readers_file"',
      dest='ccid_supported_readers_file')
  args_parser.add_argument(
      '--target-file-path',
      type=argparse.FileType('w'),
      required=True,
      metavar='"path/to/target_file"',
      dest='target_file')
  args = args_parser.parse_args()

  readers_list = create_readers_list(args.ccid_supported_readers_file)
  args.target_file.write(readers_list)

if __name__ == '__main__':
  main()
