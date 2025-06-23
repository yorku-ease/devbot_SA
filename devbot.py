import re
import os, subprocess, platform
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from prompts import software_architecture_assistant_prompt_1, software_architecture_assistant_prompt_2
from prompts import software_architecture_zero_shot_prompt, software_architecture_in_context_prompt, software_architecture_chain_of_thought_prompt
from prompts import software_architecture_refine_prompt, software_architecture_fill_prompt, software_architecture_remove_prompt
import pdfGenerator


def get_llm(model):
    if model in ["gpt-4o", "gpt-4o-mini", "o3", "o1"]:
        openai_api_key = load_api_key_from_file('openai_api_key')
        #instantiate the chosen model by the user
        llm = ChatOpenAI(api_key=openai_api_key,model= model, temperature=1)
    elif model in ["gemini-2.0-flash", "gemini-1.5-pro"]:
        google_api_key = load_api_key_from_file('google_api_key')
        llm = ChatGoogleGenerativeAI(model=model, google_api_key=google_api_key, temperature=1, top_p=0.8)
    else:
        groq_api_key = load_api_key_from_file('groq_api_key')
        llm = ChatGroq(api_key=groq_api_key, model_name=model, temperature=1, top_p=0.8)
    return llm


def last_puml_diagram(text):
    return re.findall(r"```plaintext\n(.*?)```", text, re.DOTALL)


# this function gets called from the gui after user enter system description and model they want to use
def query_llm(description, model, docType, refine='', fill=False, remove=False):
    llm = get_llm(model)
    llm_chain = ''
    fileName = ''
    if docType == "SDD":
        #create a chain with the required prompt and the llm
        llm_chain = LLMChain(llm=llm, prompt=software_architecture_assistant_prompt_2)
        fileName = 'Software Design Document.pdf'
    elif docType == "Details":
        #create a chain with the required prompt and the llm
        llm_chain = LLMChain(llm=llm, prompt=software_architecture_assistant_prompt_1)
        fileName = 'Software Architecture Details.pdf'
    elif docType == "Zero-Shot":
        llm_chain = LLMChain (llm=llm,prompt=software_architecture_zero_shot_prompt)
        fileName = 'Software Architecture Zero Shot.pdf'
    elif docType == "In-Context":
        llm_chain = LLMChain (llm=llm,prompt=software_architecture_in_context_prompt)
        fileName = 'Software Architecture In Context.pdf'
    elif docType == "Chain-of-Thought":
        llm_chain = LLMChain (llm=llm,prompt=software_architecture_chain_of_thought_prompt)
        fileName = 'Software Architecture Chain of Thought.pdf'
    #query the chosen large language model and get the output.
    output = llm_chain.invoke({'description': description})['text']

    if refine or fill or remove:
        if refine:
            prompt = software_architecture_refine_prompt
        elif fill:
            refine = 'gpt-4o'
            prompt = software_architecture_fill_prompt
        elif remove:
            refine = 'llama-3.1-8b-instant'
            prompt = software_architecture_remove_prompt

        llm_refine = get_llm(refine)
        llm_refine_chain = LLMChain(llm=llm_refine, prompt=prompt)
        refined = llm_refine_chain.invoke({'description': description,
                                           'llm_diagram': last_puml_diagram(output)})['text']
        refined = last_puml_diagram(refined)

        matches = list(re.finditer(r"```plaintext\n(.*?)```", output, re.DOTALL))
        last_match = matches[-1]
        start, end = last_match.span()
        output = output[:start] + f"```plaintext\n{refined}```" + output[end:]

    # get directory where script is downloaded to create output file
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_file = os.path.join(script_dir, "output")

    # write llm output to the a file to read later
    with open(output_file, "w") as file:
        file.write(output)


    # generate the software specification document in pdf form from gpt output file generated
    pdfGenerator.generate_pdf(output_file, script_dir, fileName)

    current_dir = os.getcwd()
    # move to where script was downloaded by user to open the pdf file
    os.chdir(script_dir)

    # making sure it runs on all operating systems
    if platform.system() == "Windows":
        os.startfile(fileName)
    else:
        subprocess.run(["open", fileName])

    # move back to current working directory from where script is being run
    os.chdir(current_dir)


def load_api_key_from_file(filename):
    """
    Reads the API key from a file and returns it.
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    api_file = os.path.join(script_dir, filename)
    with open(api_file, "r") as f:
        api_key = f.read().strip()
    return api_key
