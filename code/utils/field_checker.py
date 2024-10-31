import os

from data_models.id_document import *
from data_models.name_check import *
from data_models.address_check import *
from data_models.field_check import *

from utils.general_helpers import *
from utils.cosmos_helpers import *

from rich.console import Console
console = Console()


module_directory = os.path.dirname(os.path.abspath(__file__))


address_check_prompt_template = read_file(os.path.join(module_directory, "../prompts/address_comparison_prompt.txt"))
field_check_prompt_template = read_file(os.path.join(module_directory, "../prompts/field_comparison_prompt.txt"))
name_check_prompt_template = read_file(os.path.join(module_directory, "../prompts/name_comparison_prompt.txt"))  


class FieldChecker:

    def __init__(self):
        pass

    def check_address(self, address1, address2):
        prompt = address_check_prompt_template.format(address1=address1, address2=address2)
        address_check = ask_LLM_with_structured_outputs(prompt, response_format=AddressComparisonResult)
        return address_check
    
    def check_field(self, field_name, field1, field2):
        prompt = field_check_prompt_template.format(field_name=field_name, field1=field1, field2=field2)
        field_check = ask_LLM_with_structured_outputs(prompt, response_format=FieldComparisonResult)
        return field_check
    
    def check_name(self, name1, name2):
        prompt = name_check_prompt_template.format(name1=name1, name2=name2)
        name_check = ask_LLM_with_structured_outputs(prompt, response_format=NameComparisonResult)
        return name_check