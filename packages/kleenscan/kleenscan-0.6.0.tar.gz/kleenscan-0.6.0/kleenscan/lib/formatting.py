import yaml
import toml
# import xml.etree.ElementTree as ET
import json
from typing import Union



# def xml_dump(data: str) -> str:
#     # Turn a simple dict of key/value pairs into XML.
#     elem = ET.Element('result')
#     for key, val in data.items():
#         child = ET.SubElement(elem, key)
#         child.text = str(val)

#     return ET.tostring(elem, encoding='unicode')



def format_result(output_format: str, result: str) -> str:
	ks_dict = json.loads(result)
	if output_format:
		output_format = output_format.lower()
	
		if output_format == 'yaml':
			return yaml.dump(ks_dict, default_flow_style=False)
	
		elif output_format == 'toml':
			return toml.dumps(ks_dict)
	
		# elif output_format == 'xml':
		#	return xml_dump(ks_dict)
	
	return json.dumps(ks_dict, indent=5)