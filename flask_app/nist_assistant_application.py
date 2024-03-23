from flask import Flask, Response, render_template, request
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer, util
import pickle
from typing import Final

# The path to the embedding model for the NIST SP-800 documents
EMBEDDING_SAVE_FILE: Final[str] = '../models/nist_sp800_embeddingsv1.pkl'

# The path to the Mistral-instruct LLM
LLM_PATH: Final[str] = "../models/mistral-7b-instruct-v0.2.Q6_K.gguf"

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world() -> str:
    """
    Endpoint that renders the primary webpage the user sees when they go to the root of the website. 

    Returns:
        str: html home page. 
    """
    return render_template('index.html')

@app.route("/nist_assistant", methods=['POST'])
def nist_assistant() -> Response:
    """
    Endpoint that provides a stream of data from the LLM to the web front-end. 
    The "get_answer_from_llm" function acts as a continious generator for the flask
    Response.  It will stream generated text via the yield statement in get_answer_from_llm
    until the LLM stops producing output.

    Returns:
        Response: Stream of text data from LLM
    """
    question_from_frontend = request.json['messages']

    return Response(get_answer_from_llm(question_from_frontend),  mimetype='text/event-stream')


def get_answer_from_llm(user_question: str):
    """
    Takes the user's question and combines it with relevant NIST and passes those to the LLM
    for analysis.  The LLM "looks" through all of the data and extracts relevant sections to provide
    an answer to the user. Returns the response as a stream from the LLM as it is being generated using yeild. 

    Args:
        user_question (str): The user's question to be answered
    """
    
    # First we need to get documents that are related to the user's question using our sentence embeddings
    relevant_documents: list[str] = get_most_similar_pages(user_question)

    # Need to open and close the json data properly for the final form of the data that gets passed to the LLM.
    relevant_documents_str: str = "nist_document_data{\n"
    for i, document in enumerate(relevant_documents):
        if i < len(relevant_documents) - 1:
            relevant_documents_str = relevant_documents_str + document + ',\n'
        else:
            relevant_documents_str = relevant_documents_str + document + '\n}'

    # Setup the system prompt, giving the LLM a "Role"
    system_prompt: str = ("You are an assistant providing information to cybersecurity researchers working with NIST requirements. "
                        "Use only the information in the provided JSON, which contains titles, page numbers, and the text content for"
                        " a specific page out of a NIST document, to generate an answer."
                        "Tell the user the title of the NIST document the information is being referenced from along with the page number. " 
                        "If the information is being referenced from multiple documents, list all of the document names where the information is coming from."
                        "Only use the information provided in the JSON data!")

    # Setup the user question, need to concatanate the user's question with the relevant NIST documents
    user_question_with_docs: str = (f"Using only the information from the NIST documents provided below as JSON, provide an answer to the following question: {user_question}\n\n"
                        f"\n\n {relevant_documents_str}")

    print(str(user_question_with_docs))

    # Init model
    llm = Llama(model_path=LLM_PATH, 
                n_gpu_layers=-1, # set this value to 0 if you are going to use CPU only
                n_ctx=16384, # Mistral instruct V02 should be able to handle 32768 tokens, but due to my GPU VRAM limitations I had to cut that in half.
                chat_format='llama-2',
                )

    # Query the LLM using our system prompt and user question + NIST documents
    response = llm.create_chat_completion(
                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": user_question_with_docs
                    }
                ],
                max_tokens=1000,  # This can be increased, but I found 1000 to work well. 
                temperature=0.0,  # Set to 0 since we do not want the chatbot to be creative and make up stuff that's not in the NIST docs.
                stream=True
                )

    # Stream the answer to the user
    for chunk in response:
        if "content" in chunk['choices'][0]['delta']:
            yield chunk['choices'][0]['delta']['content']


def get_most_similar_pages(user_question: str) -> list[str]:
    """Gets the most relevant NIST documents based on the user's question using
    embeddings
    Args:
        user_question (str): The user's question

    Returns:
        list[str]: The list of relevant documents
    """

    # Download the sentence transformer base model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # will hold all of our NIST text data
    corpus: list[str] = []

    # Load NIST SP-800 sentences & embeddings from disc
    with open(EMBEDDING_SAVE_FILE, "rb") as fIn:
        stored_data = pickle.load(fIn)
        corpus = stored_data["sentences"]
        corpus_embeddings = stored_data["embeddings"]

    # Encode the user's query
    query_embedding = model.encode(user_question)

    # Find the top 10 corpus documents matching the user's query
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=10)

    # Add the relevant documents to a list to be returned to the LLM
    relevant_docs: list[str] = []
    for hit in hits[0]:
        relevant_docs.append(corpus[hit['corpus_id']])

    return relevant_docs
