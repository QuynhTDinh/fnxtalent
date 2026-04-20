from core.agents.base_agent import BaseAgent
from core.agents.llm_client import create_llm_client
from core.agents.prompts import SLIDE_MAKER_SYSTEM_PROMPT
import re

class SlideAgent(BaseAgent):
    def __init__(self, name="SlideAgent", framework_path=None):
        super().__init__(name, framework_path)
        self.llm = create_llm_client("gemini")
    
    def handle_event(self, event_name, data):
        """
        Handle incoming logic for Slide Generation
        Expects data to have:
        - 'topic': User instructions / topic for the presentation
        - 'context_materials': Optional text, materials to base the slide on.
        """
        if event_name == "GENERATE_SLIDE":
            topic = data.get("topic", "")
            materials = data.get("context_materials", "")
            
            self.log(f"Triggers slide generation for topic: {topic}")
            
            prompt_content = f"CHỦ ĐỀ/YÊU CẦU: {topic}\n\n"
            if materials:
                prompt_content += f"TÀI LIỆU THAM KHẢO:\n{materials}\n\n"
                
            prompt_content += "Hãy thiết kế bộ Slide (Markdown) theo quy tắc của bạn ngay bây giờ."
            
            try:
                # Gọi LLM sử dụng Gemini-Pro hoặc model config định sẵn
                result_text = self.llm.generate(
                    system_prompt=SLIDE_MAKER_SYSTEM_PROMPT,
                    user_prompt=prompt_content,
                    temperature=0.7 # Tính sáng tạo vừa phải cho format
                )
                
                # Cleanup potential ```markdown wrappers that LLM loves to output
                cleaned_text = re.sub(r'^```markdown\s*', '', result_text)
                cleaned_text = re.sub(r'```$', '', cleaned_text).strip()
                
                return {
                    "status": "success", 
                    "markdown": cleaned_text
                }
            except Exception as e:
                self.log(f"Error generating slides: {str(e)}")
                return {"status": "error", "message": str(e)}
        
        return {"status": "ignored"}
