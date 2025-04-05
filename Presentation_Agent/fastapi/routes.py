from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from typing import List, Optional, Dict, Union
from fastapi.responses import JSONResponse, StreamingResponse
from core.chatbot_qa import ChatbotService
from models import ChatRequest, ChatResponse
from utils import export_pdf_with_audio_to_pptx, export_pptx_with_wavs_as_zip
from core.TTS_tunning import TTSEngine
from core.script_generate import ScriptGenerator
from models import QAEnableRequest

router = APIRouter()
chatbot_service = ChatbotService()

@router.post("/generate-script")
async def generate_script(
    file: UploadFile = File(...),
    full_document: str = Form(...)
):
    try:
        script_generator = ScriptGenerator(file, full_document)
        script_data = script_generator.process()
        return JSONResponse(content=script_data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/chatpdf")
# async def chat_with_pdf(r):
#     # PDF 기반 Q&A
#     pass

@router.post("/qa/enable")
async def enable_qa(payload: QAEnableRequest):
    full_document = payload.full_document
    script_data = [s.model_dump() for s in payload.script_data]  # dict로 변환
    chatbot_service.update_context(full_document, script_data)
    chatbot_service.set_presentation_complete()
    return {"status": "success"}

# @router.get("/chat/status")
# async def get_chat_status():
#     """챗봇 활성화 상태를 확인합니다."""
#     try:
#         return chatbot_service.get_status()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """챗봇 질문에 대한 답변을 생성합니다."""
    chatbot_service.set_presentation_complete()
    try:
        answer = await chatbot_service.process_qa_request(
            request.question,
            request.session_id
        )
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/generate-audio")
async def generate_audio(data: Dict[str, Union[Dict[str, str], List[str], str]]):
    try:
        scripts = data["scripts"]
        keywords = data["keywords"]
        gender = data.get("gender", "MAN")  # 기본값은 MAN으로 설정
        print("📥 /generate-audio 요청 도착")
        print(f"▶️ scripts: {len(scripts)}, keywords: {keywords}, gender: {gender}")

        tts_engine = TTSEngine(gender=gender)  # 성별 파라미터 전달
        tts_engine.clear_audio_dir()          # 기존 WAV 제거
        result = tts_engine.synthesize_pages(pages=scripts, keywords=keywords)  # 음성 생성
        print("✅ 음성 생성 완료")

        return result
    except Exception as e:
        print(f"❌ TTS 생성 중 예외 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    
    
@router.post("/export-presentation")
async def export_presentation(
    file: UploadFile = File(...),
    wav_dir: str = Form(...)
):
    """
    PDF를 PPTX로 변환하고 오디오 삽입 후 PPTX + WAV ZIP 반환
    """
    try:
        pdf_bytes = await file.read()
        pptx_bytes = export_pdf_with_audio_to_pptx(pdf_bytes, wav_dir)
        zip_bytes = export_pptx_with_wavs_as_zip(pptx_bytes, wav_dir)

        return StreamingResponse(
            iter([zip_bytes]),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=presentation_bundle.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))