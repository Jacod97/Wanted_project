from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, List
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from google.cloud import texttospeech_v1 as tts
from langchain.storage import InMemoryStore
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.ddg_search import DuckDuckGoSearchRun
from langchain.tools import Tool
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import initialize_agent, AgentType

import os

load_dotenv("../.env")

image_model_params = {
    "model": "gpt-4o-mini",
    "temperature": 0.1,
    "max_tokens": 1024,
    "timeout": 60,
}

page_script_model_params = {
    "model": "gpt-4o",
    "temperature": 0.6,
    "timeout": 60,
}

chat_model_params = {
    "model": "gpt-4o-mini",
    "temperature": 0.0,
    "timeout": 60,
}

# tool 추가
ddg_search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="duckduckgo_search",
    func=ddg_search.run,
    description="사용자의 질문과 관련된 정보를 웹에서 검색할 수 있는 도구입니다."
)

class GPTModel():
    def __init__(self, prompt_path, output_parser, model_params, use_memory=False):
        self.prompt_path = prompt_path
        self.llm = ChatOpenAI(**model_params)
        self.output_parser = output_parser
        self.use_memory = use_memory
        self.memory = None
        self.chain = self._make_chain()

    def _make_chain(self):
        if self.use_memory:
            self.memory = ConversationSummaryMemory(llm=self.llm, return_messages=True)
            return ConversationChain(llm=self.llm, memory=self.memory)
        else:
            return self.llm | self.output_parser

    def _get_template(self):
        prompt_abs_path = Path(__file__).parent / self.prompt_path
        with open(prompt_abs_path, "r", encoding="utf-8") as f:
            template = f.read()
        return template

    def _set_prompt(self, **inputs):
        pass

    def invoke(self, inputs):
        prompt = self._set_prompt(inputs)
        if self.use_memory:
            response = self.chain.run(prompt)
        else:
            response = self.chain.invoke(prompt)
        return response

class ImageDescriptAI(GPTModel):
    def __init__(self, prompt_path, output_parser, model_params, use_memory=False):
        super().__init__(prompt_path, output_parser, model_params, use_memory)

    def _set_prompt(self, inputs):
        inputs["format_instructions"] = self.output_parser.get_format_instructions()
        template = self._get_template().format(**inputs)

        prompt = [
            HumanMessage(
                content=[
                    {"type": "text", "text": template},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64, {inputs['image_base64']}"},
                    },
                ]
            )
        ]
        return prompt

class PageScriptAI(GPTModel):
    def __init__(self, prompt_paths: dict, output_parser, model_params, use_memory=True):
        self.prompt_paths = prompt_paths
        super().__init__(None, output_parser, model_params, use_memory)

    def _get_template(self, page_type="body"):
        path = Path(__file__).parent / self.prompt_paths[page_type]
        with open(path, "r", encoding="utf-8") as f:
            template = f.read()
        return template

    def _set_prompt(self, inputs):
        page_idx = inputs.get("page", 1)
        total_pages = inputs.get("total_pages", 1)

        if page_idx == 1:
            page_type = "head"
        elif page_idx == total_pages:
            page_type = "end"
        else:
            page_type = "body"

        prompt = self._get_template(page_type).format(**inputs)
        return prompt

class ImageCategory(BaseModel):
    is_chart: bool = Field(..., description="데이터 관련 이미지 여부 (True/False)")  
    description: str = Field("", description="이미지에 대한 설명")

class ChatRequest(BaseModel):
    question: str
    session_id: str

class ChatResponse(BaseModel):
    answer: str

class PresentationState(BaseModel):
    is_completed: bool = Field(default=False)
    chat_enabled: bool = Field(default=False)

class PageScript(BaseModel):
    page: int
    script: str

class QAEnableRequest(BaseModel):
    full_document: str
    script_data: list[PageScript]

class Chatbot:
    def __init__(self, prompt_path, output_parser, model_params, db_path):
        self.prompt_path = prompt_path
        self.embeddings = OpenAIEmbeddings()
        self.output_parser = output_parser
        self.retriever = self._init_retriever(db_path)
        self.llm = ChatOpenAI(**model_params)
        self.chat_history_store = {}
        self.prompt_template: Optional[ChatPromptTemplate] = None
        self.chain = None

    def _init_retriever(self, db_path):
        # ParentDocumentRetriever 설정
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=250,
            separators=['==================================================', '---.*?---', '===.*?===']
        )
        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100
        )

        vectorstore = Chroma(
            persist_directory=db_path,
            embedding_function=self.embeddings
        )
        parent_store = InMemoryStore()

        # 🔹 텍스트 파일 로드 및 분할
        text_paths = [
            "../data/txt/wikidocs_01.txt",
            "../data/txt/wikidocs_02.txt",
            "../data/txt/wikidocs_03.txt"
        ]
        documents = []

        for path in text_paths:
            abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
            if os.path.exists(abs_path):
                with open(abs_path, "r", encoding="utf-8") as f:
                    raw_text = f.read()
                    splits = parent_splitter.create_documents([raw_text])
                    documents.extend(splits)

        # 🔹 문서를 docstore에 저장 (InMemoryStore는 key-value 형태)
        parent_store.mset([(str(i), doc) for i, doc in enumerate(documents)])

        return ParentDocumentRetriever(
            vectorstore=vectorstore,
            docstore=parent_store,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
            search_kwargs={"k": 5} 
        )

    def get_template(self, system_context: str) -> ChatPromptTemplate:
        from string import Template
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            system_prompt_template = Template(f.read())
            system_prompt = system_prompt_template.safe_substitute(context=system_context)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}"),
            ("human", "문서:\n{documents}"),
            ("human", "이전 대화 내용:\n{chat_history}")
        ])
        self.prompt_template = prompt
        return prompt

    def _make_chain(self):
        def retrieve_or_search(question: str):
            docs = self.retriever.get_relevant_documents(question)
            if not docs:
                web_result = ddg_search.run(question)
                return [Document(page_content=web_result)]
            return docs

        self.chain = (
            {
                "question": lambda x: x["question"],
                "documents": lambda x: retrieve_or_search(x["question"]),
                "chat_history": lambda x: self.format_chat_history(x.get("chat_history", []))
            }
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
        self.qa_chain = RunnableWithMessageHistory(
            self.chain,
            get_session_history=self.get_chat_history,
            input_messages_key="question",
            history_messages_key="chat_history"
        )

    def invoke(self, question: str, session_id: str) -> str:
        if not self.qa_chain:
            return "체인이 준비되지 않았습니다. system_context를 먼저 설정해주세요."
        try:
            return self.qa_chain.invoke(
                {"question": question},
                config={"configurable": {"session_id": session_id}}
            )
        except Exception as e:
            return f"오류 발생: {str(e)}"

    def get_chat_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.chat_history_store:
            self.chat_history_store[session_id] = ChatMessageHistory()
        return self.chat_history_store[session_id]

    def format_chat_history(self, chat_history):
        formatted = []
        for m in chat_history:
            if hasattr(m, "type") and hasattr(m, "content"):
                formatted.append(f"{m.type}: {m.content}")
        return "\n".join(formatted)

class TTS_LLM:
    def __init__(self, voice_name):
        self.client = tts.TextToSpeechClient()
        self.voice = tts.VoiceSelectionParams(
            language_code="ko-KR",
            name=voice_name
        )
        self.audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)
    
    def _response(self, text: str):
        response = self.client.synthesize_speech(
            input=tts.SynthesisInput(ssml=text),
            voice=self.voice,
            audio_config=self.audio_config
        )
        return response

MAN_TTS = TTS_LLM(voice_name="ko-KR-Wavenet-C")
WOMAN_TTS = TTS_LLM(voice_name="ko-KR-Wavenet-A")

VISION_LLM  = ImageDescriptAI(
    prompt_path="prompts/image_script.prompt",
    output_parser=PydanticOutputParser(pydantic_object=ImageCategory),
    model_params=image_model_params,
    use_memory=False
)

PAGE_SCRIPT_LLM = PageScriptAI(
    prompt_paths={
        "head": "prompts/head_script.prompt",
        "body": "prompts/body_script.prompt",
        "end": "prompts/end_script.prompt"
    },
    output_parser=StrOutputParser(),
    model_params=page_script_model_params,
    use_memory=True
)

CHATBOT_LLM = Chatbot(
    prompt_path="prompts/chatbot.prompt",
    output_parser=StrOutputParser(),
    model_params=chat_model_params,
    db_path=os.path.join(os.path.dirname(__file__), "../../data/db/chromadb/split_knowledge")
)