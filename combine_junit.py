from junitparser import JUnitXml
import functools

print("Combine junit")

import sys

if __name__ == '__main__':
    print("MAIN HELLO")

    arg_list = sys.argv[1:]

    xml_out = [arg for arg in arg_list if arg.startswith("-o") and arg.endswith("xml")]

    assert len(xml_out) == 1, "Did you forget to pass exactly 1 xml output file? See python3 -m fr.combine_junit -h"

    xml_in = [arg for arg in arg_list if arg.endswith("xml") and not arg in xml_out]

    assert len(xml_in) > 0, "Did you forget to pass xml inputs? See python3 -m fr.combine_junit -h"

    print("XML IN: ", xml_in)

    xmls = [JUnitXml.fromfile(f) for f in xml_in]
    combine = lambda x,y: x+y

    newXml = functools.reduce(combine, xmls)
    
    newXml.write(xml_out[0].split("=")[-1])
