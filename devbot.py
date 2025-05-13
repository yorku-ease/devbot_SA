import os, subprocess, platform
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from prompts import software_architecture_assistant_prompt_1, software_architecture_assistant_prompt_2
import pdfGenerator


# this function gets called from the gui after user enter system description and model they want to use
def query_llm(description, model, docType):
    if model in ["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini"]:
        openai_api_key = load_api_key_from_file()
        #instantiate the chosen model by the user
        llm = ChatOpenAI(api_key=openai_api_key,model= model, temperature=1)

    else:
        groq_api_key = load_api_key_from_file('groq_api_key')
        llm = ChatGroq(api_key=groq_api_key, model_name=model, temperature=1)

    llm_chain = ''
    if docType == "SDD":
        #create a chain with the required prompt and the llm
        llm_chain = LLMChain(llm=llm, prompt=software_architecture_assistant_prompt_2)
    elif docType == "Details":
        #create a chain with the required prompt and the llm
        llm_chain = LLMChain(llm=llm, prompt=software_architecture_assistant_prompt_1)
    #query the chosen large language model and get the output.
    output = llm_chain.invoke({'description': description})['text']

    # get directory where script is downloaded to create output file
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_file = os.path.join(script_dir, "output")

    # write llm output to the a file to read later
    with open(output_file, "w") as file:
        file.write(output)

    # generate the software specification document in pdf form from gpt output file generated
    pdfGenerator.generate_pdf(output_file, script_dir)

    current_dir = os.getcwd()
    # move to where script was downloaded by user to open the pdf file
    os.chdir(script_dir)

    # making sure it runs on all operating systems
    if platform.system() == "Windows":
        os.startfile("Software Design document.pdf")
    else:
        subprocess.run(["open", "Software Design document.pdf"])

    # move back to current working directory from where script is being run
    os.chdir(current_dir)


def load_api_key_from_file(filename='api_key'):
    """
    Reads the API key from a file and returns it.
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    api_file = os.path.join(script_dir, filename)
    with open(api_file, "r") as f:
        api_key = f.read().strip()
    return api_key
