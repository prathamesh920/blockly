#!/usr/bin/python

# Converts .xlf files into .json files for use at http://translatewiki.net.
#
# Copyright 2013 Google Inc.
# http://blockly.googlecode.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import codecs  # for codecs.open(..., 'utf-8')
import json    # for json.load()
import os      # for os.path()
from common import InputError

# Store parsed command-line arguments in global variable.
args = None


def _insert_breaks(s, min_length, max_length):
    """Inserts line breaks to try to get line lengths within the given range.

    This tries to minimize raggedness and to break lines at punctuation
    (periods and commas).  It never splits words or numbers.  Multiple spaces
    may be converted into single spaces.

    Args:
        s: The string to split.
        min_length: The requested minimum number of characters per line.
        max_length: The requested minimum number of characters per line.

    Returns:
        A copy of the original string with zero or more line breaks inserted.
    """
    newline = '\\n'
    if len(s) < min_length:
        return s
    # Try splitting by sentences.  This assumes sentences end with periods.
    sentences = s.split('.')
    # Remove empty sentences.
    sentences = [sen for sen in sentences if sen]

    # If all sentences are at least min_length and at most max_length,
    # then return one per line.
    if not [sen for sen in sentences if
            len(sen) > max_length or len(sen) < min_length]:
        return newline.join([sen.strip() for sen in sentences])

    # Otherwise, divide into words, and use a greedy algorithm for the first
    # line, and try to get later lines as close as possible in length.
    words = [word for word in s.split(' ') if word]
    line1 = ''
    while (len(line1) + 1 + len(words[0]) < max_length and
           # Preferentially split on periods and commas.
           (not ((line1.endswith('. ') or line1.endswith(', ')) and
                 len(line1) > min_length))):
        line1 += words.pop(0) + ' '
        # If it all fits on one line, return that line.
        if not words:
            return line1
    ideal_length = len(line1)
    output = line1
    line = ''
    while words:
        line += words.pop(0) + ' '
        if words:
            potential_len = len(line) + len(words[0])
            if (potential_len > max_length or
                potential_len - ideal_length > ideal_length - len(line) or
                (line.endswith('. ') and len(line) > min_length)):
                output += newline + line
                line = ''
    output += newline + line
    return output


def _create_xlf(target_lang):
    """Creates a <target_lang>.xlf file for Soy.

    Args:
        target_lang: The ISO 639 language code for the target language.
            This is used in the name of the file and in the metadata.

    Returns:
        A pointer to a file to which the metadata has been written.

    Raises:
        IOError: An error occurred while opening or writing the file.
    """
    filename = os.path.join(os.curdir, args.output_dir, target_lang + '.xlf')
    out_file = codecs.open(filename, 'w', 'utf-8')
    print 'Created file: ' + filename
    out_file.write("""<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file original="SoyMsgBundle"
        datatype="x-soy-msg-bundle"
        xml:space="preserve"
        source-language="{0}"
        target-language="{1}">
    <body>""".format(args.source_lang, target_lang))
    return out_file


def _close_xlf(xlf_file):
    """Closes a <target_lang>.xlf file created with create_xlf().

    This includes writing the terminating XML.

    Args:
        xlf_file: A pointer to a file created by _create_xlf().

    Raises:
        IOError: An error occurred while writing to or closing the file.
    """
    xlf_file.write("""
    </body>
  </file>
</xliff>
""")
    xlf_file.close()


def _process_file(filename, key_dict):
    """Creates an .xlf file corresponding to the specified .json input file.

    The base name of the file will be the locale specified in the input file's
    metadata.

    Args:
        filename: The name of a .json file produced directly or indirectly by
            xliff_to_json.py.
        key_dict: Dictionary mapping Blockly keys (e.g., Maze.turnLeft) to
            Closure keys (hash numbers).

    Raises:
        IOError: An I/O error occurred with an input or output file.
        ValueError: Input JSON could not be parsed.
        InputError: Input JSON lacked required fields.
    """
    in_file = open(filename)
    try:
        j = json.load(in_file)
        in_file.close()
    except ValueError, e:
        raise InputError(file, str(e))
    metadata = j['@metadata']
    if not metadata:
        raise InputError(filename, 'metadata not found')
    if not metadata.get('locale'):
        raise InputError(filename, 'metadata does not contain "locale"')
    target_lang = metadata.get('locale')
    out_file = _create_xlf(target_lang)
    for key in j:
        if key != '@metadata':
            identifier = key_dict[key]
            target = j.get(key)
            # Only insert line breaks for tooltips.
            if key.lower().find('tooltip') != -1:
                target = _insert_breaks(
                    j.get(key), args.min_length, args.max_length)
            out_file.write(u"""
      <trans-unit id="{0}" datatype="html">
        <target>{1}</target>
      </trans-unit>""".format(identifier, target))
    _close_xlf(out_file)


def main():
    """Parses arguments and iterates over files."""

    # Set up argument parser.
    parser = argparse.ArgumentParser(description='Convert JSON files to XLF.')
    parser.add_argument('--source_lang', default='en',
                        help='ISO 639-1 source language code')
    parser.add_argument('--output_dir', default='.',
                        help='relative directory for output files')
    parser.add_argument('--key_file', default='keys.json',
                        help='relative path to input keys file')
    parser.add_argument('--min_length', default=30,
                        help='minimum line length (not counting last line)')
    parser.add_argument('--max_length', default=50,
                        help='maximum line length (not guaranteed)')
    parser.add_argument('files', nargs='+', help='input files')

    # Initialize global variables.
    global args
    args = parser.parse_args()

    # Read in keys.json, mapping descriptions (e.g., Maze.turnLeft) to
    # Closure keys (long hash numbers).
    key_file = open(args.key_file)
    key_dict = json.load(key_file)
    key_file.close()

    # Process each input file.
    for filename in args.files:
        _process_file(filename, key_dict)


if __name__ == '__main__':
    main()

