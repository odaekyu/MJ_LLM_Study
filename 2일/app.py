import streamlit as st
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnableMap, RunnableLambda
from datetime import datetime

# Function to execute the chains
def run_chains(question, lang, model):
    # Chain1
    llm1 = ChatOllama(model=model, base_url="http://192.168.0.57:11434/")
    prompt1 = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template("당신은 인공지능 전문가입니다. 사용자의 질문에 답해주세요."),
                HumanMessagePromptTemplate.from_template("{input}")
                                                ])
    output_parser = StrOutputParser()
    chain1 = prompt1 | llm1 | output_parser

    # Chain2
    llm2 = ChatOllama(model=model, base_url="http://192.168.0.57:11434/")
    prompt2 = ChatPromptTemplate.from_messages([SystemMessagePromptTemplate.from_template("""
                                                # Instruction 
                                                당신은 번역가입니다. 다음에 주어진 문장을 {lang}로 번역해주세요.                                                                                      
                                                """),
                                                HumanMessagePromptTemplate.from_template("""
                                                # Text
                                                {text}                                           
                                                # Result""")])
    chain2 = RunnableMap({"text": RunnableLambda(lambda x: chain1.invoke({"input": question})), "lang": RunnableLambda(lambda x: lang)}) | prompt2 | llm2 | output_parser
    
    # Run chain2
    result = chain2.invoke({"input": question})
    return result

def SaveResult(result):
        # Save result to a file
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".txt"
    with open(filename, "w") as file:
        file.write(result)    
    return filename


# Streamlit app
st.title("Ollama 정보 번역 App")

# User inputs
question = st.text_input("질문:", "여기에 질문을 입력하세요")
lang = st.selectbox("언어를 선택해주세요:", ["English", "한국어", "프랑스어", "Español"])
model = st.selectbox("Ollama model을 선택해주세요", ["qwen2:1.5b-instruct", "aya:latest"])

# Run the chains and display the result
if st.button("실행"):
    if question and lang:
        with st.spinner("잠시만 기다려 주세요..."):
            result = run_chains(question, lang, model)
            st.success("완료!")
            st.write("번역 결과:", result)
            filename = SaveResult(result)
            st.write("번역 결과 저장 완료 : ", filename)
            
            with open(filename, "rb") as file:
                btn = st.download_button(
                    label="결과 다운로드",
                    data=file,
                    file_name=filename,
                    mime="text/plain"
                )                
    else:
        st.error("질문과 언어를 모두 입력해주세요.")