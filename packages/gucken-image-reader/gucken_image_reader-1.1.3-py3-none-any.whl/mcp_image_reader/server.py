import os
import base64
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from openai import OpenAI

# Load environment variables
load_dotenv()


# Create MCP server
mcp = FastMCP("gucken")

@mcp.tool()
def describe_image(image_path: str) -> str:
    """
    로컬 이미지 파일을 읽어 OpenAI Vision 모델로 묘사(description)된 텍스트를 반환합니다.
    """
    # 1) 클라이언트 초기화 (환경변수 OPENAI_API_KEY에서 API 키를 가져옵니다)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # 2) 이미지 파일을 읽고 base64로 인코딩 (data URL 형식)
    with open(image_path, "rb") as img_file:
        img_b64 = base64.b64encode(img_file.read()).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{img_b64}"
    
    # 3) Vision 모델에 묘사 요청
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "이 이미지를 자세히 묘사해주세요."},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ],
            }
        ],
        max_tokens=300,
    )
    
    # 4) 결과 텍스트 반환
    return response.choices[0].message.content

def serve():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    serve()