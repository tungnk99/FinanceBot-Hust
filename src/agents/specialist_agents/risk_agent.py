from pydantic import BaseModel
from agents import Agent, AgentOutputSchema
from src.setting import settings

# A sub‑agent specializing in identifying risk factors or concerns.
RISK_PROMPT = (
    "Bạn là một chuyên gia phân tích rủi ro tài chính.\n\n"
    
    "NHIỆM VỤ CỦA BẠN:\n"
    "1. Nhận yêu cầu đánh giá rủi ro\n"
    "2. Phân tích các yếu tố rủi ro tiềm ẩn\n"
    "3. Trả về đánh giá rủi ro có cấu trúc\n\n"
    
    "QUY TRÌNH XỬ LÝ:\n"
    "1. Phân tích thông tin đầu vào để xác định các rủi ro\n"
    "2. Đánh giá mức độ nghiêm trọng của từng rủi ro\n"
    "3. Trả về tóm tắt đánh giá rủi ro (dưới 2 đoạn)\n\n"
    
    "CÁC LOẠI RỦI RO CẦN XEM XÉT:\n"
    "- Rủi ro cạnh tranh và thị trường\n"
    "- Rủi ro pháp lý và quy định\n"
    "- Rủi ro chuỗi cung ứng\n"
    "- Rủi ro tăng trưởng chậm\n"
    "- Rủi ro tài chính và thanh khoản"
)


class AnalysisSummary(BaseModel):
    summary: str
    """Short text summary for this aspect of the analysis."""


risk_agent = Agent(
    name="RiskAnalystAgent",
    instructions=RISK_PROMPT,
    output_type=AgentOutputSchema(AnalysisSummary, strict_json_schema=False),
    model=settings.OPENAI_MODEL
)