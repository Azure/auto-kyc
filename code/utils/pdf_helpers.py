import fitz  # PyMuPDF
import os
import json
from typing_extensions import Annotated, List

from ins_utils.general_helpers import *
from ins_utils.openai_helpers import *

# Create a directory to store the outputs
temp_work_dir = "sample_data/temp_outputs"
os.makedirs(temp_work_dir, exist_ok=True)



def local_open_pdf_with_fitz(pdf_doc):
    doc = fitz.open(pdf_doc)
    print(f"PDF File {os.path.basename(pdf_doc)} has {len(doc)} pages.")
    return doc


def local_extract_pages_from_pdf_as_png_files(pdf_doc, work_dir=temp_work_dir):
    doc = local_open_pdf_with_fitz(pdf_doc)
    png_files = []
    for page in doc:
        page_num = page.number
        img_path = f"{work_dir}/page_{page_num}.png"
        page_pix = page.get_pixmap(dpi=300)
        page_pix.save(img_path)
        png_files.append(img_path)
    
    print(f"Saved {len(png_files)} pages in {work_dir} as images from document {pdf_doc}.")
    return png_files



def local_extract_info_from_document_images(images, labels, extract_prompt="prompts/insurance_doc_prompt.txt"):
    ins_doc_template = read_file(extract_prompt)

    all_dd = {}
    extracted = ""

    batch_size = 3
    for i in range(0, len(images), batch_size):
        image_batch = images[i:i + batch_size]
        label_batch = labels[i:i + batch_size]

        ins_doc_prompt = ins_doc_template.format(document="No Text, only images.", extracted=extracted)
        response = ask_LLM_with_images(image_batch, label_batch, ins_doc_prompt, with_json=True)
        extracted += response + "\n"
        dd = local_recover_json(extract_json(response))
        all_dd.update(dd)
    
    return all_dd




def local_extract_info_from_pdf(doc_path, work_dir, num_pages=None, extract_prompt="prompts/insurance_doc_prompt.txt"):
    new_work_dir = os.path.join(work_dir, os.path.basename(doc_path))
    os.makedirs(new_work_dir, exist_ok=True)
    pngs = local_extract_pages_from_pdf_as_png_files(doc_path, work_dir=new_work_dir)
    labels = [f"{os.path.basename(x)} of document {os.path.basename(doc_path)}" for x in pngs]

    if num_pages is not None:
        dd = local_extract_info_from_document_images(pngs[0:num_pages], labels[0:num_pages], extract_prompt=extract_prompt)
    else:
        dd = local_extract_info_from_document_images(pngs, labels, extract_prompt=extract_prompt)
        dd['document_id'] = generate_uuid_from_string(doc_path)
        dd['md5'] = get_file_md5(doc_path)
    return dd



def extract_info_from_pdf(doc_path: Annotated[str, "Path to the PDF file from which insurance information is extracted."], 
                          cust_id: Annotated[str, "Customer Id for which this document belongs."], 
                          work_dir:  Annotated[str, "working directory where the temporary PNG image files from the PDF are extracted."] = temp_work_dir ) -> str:
    """
    Extracts information from a PDF document.

    Parameters:
        doc_path (str): The path to the PDF document.
        cust_id (str): The customer ID for which this document belongs.
        work_dir (str, optional): The working directory to store temporary files. Defaults to temp_work_dir.

    Returns:
        Output JSON file: A path to the output JSON file where the JSON dictionary containing the extracted information from the PDF document was stored.
            The dictionary includes the following keys:
                - 'uuid': A unique identifier generated from the document path.
                - 'md5': The MD5 hash of the PDF document.
                - Other extracted information from the document.
    """
    new_work_dir = os.path.join(work_dir, cust_id)
    os.makedirs(new_work_dir, exist_ok=True)
    extract_prompt = "prompts/insurance_doc_prompt.txt"
    dd = local_extract_info_from_pdf(doc_path, work_dir, first_page_only=True, extract_prompt=extract_prompt)
    out_file = os.path.join(new_work_dir, f"Cust_Id_{cust_id}-{os.path.basename(extract_prompt).split('.')[0]}-Doc_Id_{dd['document_id']}.json")
    write_to_file(json.dumps(dd, indent=4), out_file, mode='w')

    return os.path.abspath(out_file)
