# -*- coding: utf-8 -*-
"""
Alternative SICS implementation that does not require pytest to run.
"""

from collections import defaultdict
from operator import itemgetter
import time

class event_log:
    """A simple non-interactive UI that timestamps events.
    Events and timestamps are stored in a dict {event: timestamp} which can be exported to Excel or similar"""
    def __init__(self) -> None:
        self.perf_counter_reference = time.perf_counter() # use time.perf_counter() because time.time() is not recommended for measuring small intervals (e.g. can count backwards!)
        self.start_time = time.time() # start time is the number of seconds since 1st Jan 1970, roughly corresponding to the first airing of Monty Python
        self.events = {}
    def record_event(self, event_name: str, display: bool = True) -> None:
        elapsed_time = time.perf_counter() - self.perf_counter_reference
        event_time = self.start_time + elapsed_time
        self.events[event_name] = event_time
        if display: print(event_name.ljust(60), time.ctime(event_time))

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

def run_tests() -> None:
    """Test the SICS compression and decompression algorithms.
    Each test case is compressed and the result is verified by comparison with a pre-calculated hex string.
    The results are also decompressed and the combined compression/decompression result is verified by comparison with the original input."""
    clock = event_log()
    clock.record_event('SICS testing started')
    case_1 = ("Marley was dead: to begin with. There is no doubt whatever about that. The register of his burial was signed by the clergyman, the clerk, the undertaker, and the chief mourner. Scrooge signed it: and Scrooge’s name was good upon ’Change, for anything he chose to put his hand to. Old Marley was as dead as a door-nail. Mind! I don’t mean to say that I know, of my own knowledge, what there is particularly dead about a door-nail. I might have been inclined, myself, to regard a coffin-nail as the deadest piece of ironmongery in the trade. But the wisdom of our ancestors is in the simile; and my unhallowed hands shall not disturb it, or the Country’s done for. You will therefore permit me to repeat, emphatically, that Marley was as dead as a door-nail.",
             "f826b1d0e2a08128fd0340f61f0750e739f50fe916107a054084cf630e9231ff01602f64c303923f50fe91061f07a31604f3097a0f6c672b0e2a0a7f05180f6d03910f2b16f0df125f403910f2b16f9f403910c581632f916f4025803910f2971f30f14c6516f50ff1f2644f010a7f0518073fd02580ff1f2644f01faa052f110e2a0f04480cf7450faff2925f01f40f346025d3975f00910f294a10340f7c3097a09258034f50ff3b80f826b1d0e2a02a0812802a0208446fb527bf50f8758ff40fc0845fa30f11250340a2d039230fc0f954ef404f30f1d04e50f954eb18f01f40e92303916107a0f72637f2cb26bd0812802f64c30208446fb527bf50fc0f17f093092ff010f6115075f2b7518f40f1da1bf3f4034061f0268020f24f3f375fb527b02a0391081281a30f771f2104f307645f145f016d0750391036281f50ff5c303910e7a84f104f304c6025f21a346a07a07503910a7f17b1ff602580f1d0c592bb4e1809258a0a92bb0543087a3c6f6073f404603910ff24c536dfaa084510f346f50ff74c0e7bb039161f34610f716f1730f11034061f7123f401f1f79237f22bbdf4039230f826b1d0e2a02a0812802a0208446fb527bf5")
    case_2 = ('aaabbc', '000112')
    case_3 = ('ab', '01')
    test_cases = [case_1, case_2, case_3]
    for num, case in enumerate(test_cases):
        original_text = case[0]
        target_text = case[1]
        compressed_text, translator = compress(original_text)
        decompressed_text = decompress(compressed_text, translator)
        if compressed_text == target_text: clock.record_event(f'Test case {num}: compression matches target text')
        else: clock.record_event(f'Test case {num}: failed (compressed text does not match target)')
        if decompressed_text == original_text: clock.record_event(f'Test case {num}: decompression successful')
        else: clock.record_event(f'Test case {num}: failed (decompressed text does not match original)')
    clock.record_event('All tests completed')
    
if __name__ == '__main__':
    run_tests()
