# -*- coding: utf-8 -*-
"""
Searchlight Inefficient Compression Scheme
==========================================
Write a compression and decompression algorithm for SICS which works as follows:
Find the most popular characters, and in order of popularity assign them a hex value 0 to E, F0
to FE, FF0 to FFE, etc. Note, an F indicates that there are more nibbles to follow, anything else
is the terminal nibble. Compress the message by replacing characters with their assigned
value.
==========================================

Comments:
    - the code presented below is optimised for readability, rather than computation speed
        * lots of speed optimisations can be made: parallelisation, use of f-strings, or implementation in a more performative language 
    - no custom error handling as any exceptions are likely to manifest as a KeyError (which is already very transparent)
    - the hex() function has not been used because it is largely incompatible with the compression scheme selected (base 16 vs base 15)
    - if the compressed data were to be saved then it would be useful to attach the software version as metadata

Also:
The instructions are slightly ambiguous because they do not specify a secondary sorting/ordering rule.
The issue is that if you have an input string which contains multiple characters with the same frequency
then it is not clear which one is "first". For example, if the input string is 'ab' then the compression
could be either '01' or '10' depending on the secondary ordering rule that is used (which is not specified).

Based on the test case given I believe that the secondary ordering rule is:
    - If two characters are equally popular then sort them by order of appearance in the text
      (the character that appears first should be assigned a lower hex value)
The compression scheme has been implemented based on this assumption.
"""

from collections import defaultdict
from operator import itemgetter
import pytest

def compress(text: str) -> tuple[str, dict]:
    """Compress a string by translating characters into hex values.
    Returns the compressed text plus a dictionary which allows the text to be decrypted."""
    index = build_index(text) # index is a dictionary of {char: hex_value} which will be used to encrypt the text
    compressed_text = ''
    for char in text:
        compressed_text += index[char]
    translator = {hex_string: char for char, hex_string in index.items()} # invert the dictionary to provide easy backward translation
    return(compressed_text, translator)

def build_index(text: str) -> dict:
    """Construct a dictionary of {char: hex_value}.
    Characters are ordered by frequency and assigned a hex value from 0 to E, F0 to FE, FF0 to FFE, etc.
    F indicates that there are more nibbles to follow, anything else is a terminal nibble.
    Characters with larger frequencies are assigned a smaller hex value.
    If two characters have the same frequency then sort them by order of appearance in the text"""
    char_instances = defaultdict(int)
    for char in text:
        char_instances[char] += 1 # counts the number of times each character appears, stores the results as {char: frequency}
    ordered_list = [char for char, instances in sorted(char_instances.items(), key=itemgetter(1), reverse=True)] # sort by charcter frequency, with larger frequencies coming first
    i = '0' # i is a hex value
    index = {}
    for char in ordered_list:
        index[char] = i
        i = increment(i)
    return(index)

def increment(hex_value: str) -> str:
    """Returns a hex value which is one higher than the input hex value."""
    increment_rule = {'0':'1', '1':'2', '2':'3', '3':'4', '4':'5',
                      '5':'6', '6':'7', '7':'8', '8':'9', '9':'a',
                      'a':'b', 'b':'c', 'c':'d', 'd':'e', 'e':'f0'}
    body = hex_value[:-1]
    trailing_character = hex_value[-1]
    suffix = increment_rule[trailing_character]
    new_value = body + suffix
    return(new_value)

def decompress(compressed_text: str, translator: dict) -> str:
    """Transform compressed text back to its original value.
    A {hex_value: character} translation dictionary is required in addition to the compressed text."""
    f_count = 0
    original_text = ''
    for char in compressed_text:
        if char == 'f': f_count += 1 # if an 'f' is encountered then store the information and procede until a terminal nibble is reached
        else:
            stub = ('f' * f_count) + char
            original_text += translator[stub]
            f_count = 0
    return(original_text)
    
if __name__ == '__main__':
    pytest.main(['Tests/test_compression_demo.py'])
