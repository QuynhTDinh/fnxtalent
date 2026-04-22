"""
CombatDesignerAgent — Tạo kịch bản Combat Audit theo tiêu chuẩn FNX.

Input:  Role details (role title, jd, seniority)
Output: Combat scenario JSON (scenario_title, background_context, questions)
"""

from core.agents.base_agent import BaseAgent
from core.agents.llm_client import create_llm_client
from core.agents.combat_prompts import COMBAT_DESIGNER_SYSTEM, build_combat_prompt

class CombatDesignerAgent(BaseAgent):
    def __init__(self, llm_provider="gemini", **kwargs):
        super().__init__(name="CombatDesignerAgent")
        self.llm = create_llm_client(llm_provider, **kwargs)

    def handle_event(self, event_name, data):
        if event_name == "COMBAT_DESIGN_REQUESTED":
            return self.design(data)
        return None

    def design(self, role_data: dict) -> dict:
        """Generate a combat scenario for an internal audit.
        
        Args:
            role_data: {
                "role": "Chuyên viên Vận hành DCS",
                "seniority": "Junior",
                "jd": "Giám sát hệ thống SCADA, báo cáo rủi ro..."
            }
        """
        self.log(f"Designing combat scenario for: {role_data.get('role')}")

        user_prompt = build_combat_prompt(role_data)
        
        try:
            scenario = self.llm.generate_json(
                system_prompt=COMBAT_DESIGNER_SYSTEM,
                user_prompt=user_prompt,
                temperature=0.6,  # Need creativity for scenarios
            )
            
            # Ensure basic fields
            scenario.setdefault("role", role_data.get("role", "Unknown Role"))
            scenario.setdefault("scenario_title", "Tình huống nghiệp vụ")
            scenario.setdefault("questions", [])
            
            self.log(f"Combat scenario created: {scenario['scenario_title']} ({len(scenario['questions'])} questions)")
            return scenario
            
        except Exception as e:
            error_msg = str(e)
            self.log(f"ERROR generating combat scenario: {error_msg}")
            
            # --- DEMO FALLBACK MECHANISM ---
            # Smart Mock Routing based on Group Tag
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg.upper():
                self.log("Triggering 429 Smart Demo Fallback Bypass...")
                role_name = role_data.get("role", "Ứng viên")
                company_name = role_data.get("company", "Công ty (PVCFC)")
                group_tag = role_data.get("group_tag", "Operations/Technical")
                
                # Mock Database
                if group_tag == "Support":
                    mock = {
                        "scenario_title": "[Demo Mock] Lỗi Thất thoát Ngân sách & Sai phạm HĐLĐ",
                        "background_context": f"Bối cảnh (Layer 3 - {company_name}): Lúc 15:00 ngày khóa sổ cuối tháng, hệ thống soát xét phát hiện biến động chi phí vô lý làm hao hụt tạm ứng 5 tỷ VNĐ. Đồng thời nhóm văn phòng đang râm ran phàn nàn chênh lệch đóng BHXH. Nguy cơ thanh tra nội bộ từ Tập đoàn giáng xuống vào sáng mai.",
                        "questions": [
                            {
                                "id": "Q1",
                                "targeted_competency": "Kiến thức Quy chuẩn Kế toán (SOP)",
                                "question_text": "[SOP - Bloom 3] Dựa trên quy chuẩn kế toán và chính sách tuân thủ hành chính, hãy liệt kê 3 bước truy xuất nguồn tiền tạm ứng và niêm phong chứng từ?",
                                "expected_bloom_level": 3
                            },
                            {
                                "id": "Q2",
                                "targeted_competency": "Nghiệp vụ Soát xét Kế toán (T - Technical)",
                                "question_text": "[Technical - Bloom 4] Hệ thống SAP báo lỗi lệch số dư ảo 5 tỷ do bút toán kép bị trùng lặp thời gian. Bạn sử dụng lệnh/báo cáo nào để trích xuất dòng tiền lỗi trong 15 phút?",
                                "expected_bloom_level": 4
                            },
                            {
                                "id": "Q3",
                                "targeted_competency": "Kỹ năng Điều phối (L - Leadership)",
                                "question_text": "[Leadership - Bloom 4] Nhóm văn phòng đang râm ran phàn nàn và đổ lỗi cho nhau. Bạn sẽ triệu tập ai và nói gì trong cuộc họp khẩn 5 phút để ổn định tâm lý?",
                                "expected_bloom_level": 4
                            },
                            {
                                "id": "Q4",
                                "targeted_competency": "Xử lý Khủng hoảng (D - Delivery)",
                                "question_text": "[Delivery - Bloom 5] Tập đoàn gọi điện yêu cầu giải trình ngay lập tức. Ban Giám đốc đi vắng. Không thể xin ý kiến. Bạn quyết định đóng băng tài khoản nào và trả lời ra sao?",
                                "expected_bloom_level": 5
                            },
                            {
                                "id": "Q5",
                                "targeted_competency": "Chốt chặn Rủi ro (D - Delivery)",
                                "question_text": "[Delivery - Bloom 5] Để thanh tra nội bộ không phát hiện lỗ hổng quy trình ngày mai, bạn sẽ thiết lập hệ thống cảnh báo sớm (Early Warning) như thế nào từ tháng sau?",
                                "expected_bloom_level": 5
                            }
                        ]
                    }
                elif group_tag == "Front-line":
                    mock = {
                        "scenario_title": "[Demo Mock] Khủng hoảng Truyền thông Bán lẻ",
                        "background_context": f"Bối cảnh (Layer 3 - {company_name}): Lô hàng phân bón đưa xuống Miền Tây bị một đại lý lớn tố cáo vón cục, sai hàm lượng. Đại lý này dọa tung lên Mạng xã hội. Lô hàng trị giá 20 tỷ VNĐ đang mắc kẹt tại kho.",
                        "questions": [
                            {
                                "id": "Q1",
                                "targeted_competency": "Kiến thức Sản phẩm (SOP)",
                                "question_text": "[SOP - Bloom 3] Đọc nhanh các thông số thành phần hóa học để chứng minh lô hàng xuất xưởng ban đầu không sai quy cách phòng Lab?",
                                "expected_bloom_level": 3
                            },
                            {
                                "id": "Q2",
                                "targeted_competency": "Kỹ năng Phân tích Thị trường (T - Technical)",
                                "question_text": "[Technical - Bloom 4] Dựa trên lịch sử tiêu thụ của Đại lý này, bạn nhận định nguyên nhân vón cục là do thời tiết hay do quy trình bảo quản sai của họ? Phân tích tại sao?",
                                "expected_bloom_level": 4
                            },
                            {
                                "id": "Q3",
                                "targeted_competency": "Kỹ năng Đàm phán (L - Leadership)",
                                "question_text": "[Leadership - Bloom 4] Khách hàng đang Livestream chuẩn bị ấn nút Đăng. Bạn dùng chiến thuật thương thuyết nào trong 1 phút qua điện thoại để họ dừng hành động?",
                                "expected_bloom_level": 4
                            },
                            {
                                "id": "Q4",
                                "targeted_competency": "Xử lý Rủi ro (D - Delivery)",
                                "question_text": "[Delivery - Bloom 5] Nếu Khách hàng vẫn ngoan cố đòi bồi thường 100%, bạn sẽ đề xuất phương án bảo lưu công nợ hay thu hồi hàng?",
                                "expected_bloom_level": 5
                            },
                            {
                                "id": "Q5",
                                "targeted_competency": "Phục hồi Doanh số (D - Delivery)",
                                "question_text": "[Delivery - Bloom 5] Sau khi dập tắt sự cố, bạn làm gì vào tuần tới để đại lý này nhập thêm 50 tấn hàng bù đắp chi phí bồi thường?",
                                "expected_bloom_level": 5
                            }
                        ]
                    }
                elif group_tag == "Ban QLDA":
                    mock = {
                        "scenario_title": "[Demo Mock] Trễ hạn Tiến độ EPC cấp Bách",
                        "background_context": f"Bối cảnh (Layer 3 - {company_name}): Dự án nâng cấp Cụm làm lạnh đang trễ tiến độ 4 tuần do Nhà thầu phụ thi công sai bản vẽ. Áp lực giải ngân vốn bắt buộc phải nghiệm thu giai đoạn 1 trong ngày mai.",
                        "questions": [
                            {
                                "id": "Q1",
                                "targeted_competency": "Kiến thức Pháp lý Hợp đồng (SOP)",
                                "question_text": "[SOP - Bloom 3] Lập tức trích xuất điều khoản phạt chậm tiến độ và quy định thay tướng nhà thầu phụ tại công trường theo luật Đấu thầu?",
                                "expected_bloom_level": 3
                            },
                            {
                                "id": "Q2",
                                "targeted_competency": "Kỹ năng Bóc tách (T - Technical)",
                                "question_text": "[Technical - Bloom 4] Bản vẽ As-built bị sai lệch so với thực tế 15%. Bạn yêu cầu QS lập biên bản hiện trường như thế nào để khoanh vùng khối lượng lỗi?",
                                "expected_bloom_level": 4
                            },
                            {
                                "id": "Q3",
                                "targeted_competency": "Điều phối Nhà thầu (L - Leadership)",
                                "question_text": "[Leadership - Bloom 4] Chỉ huy trưởng của Nhà thầu cãi cùn và dừng thi công. Bạn sử dụng biện pháp giao tiếp cứng rắn nào để dập tắt lãn công?",
                                "expected_bloom_level": 4
                            },
                            {
                                "id": "Q4",
                                "targeted_competency": "Crash Schedule (D - Delivery)",
                                "question_text": "[Delivery - Bloom 5] Đưa ra phương án dồn tài nguyên khẩn cấp (Crash Schedule) bất chấp giới hạn ngân sách. Bạn loại bỏ đầu mục nào và nhận rủi ro nào?",
                                "expected_bloom_level": 5
                            },
                            {
                                "id": "Q5",
                                "targeted_competency": "Bảo vệ Ngân sách (D - Delivery)",
                                "question_text": "[Delivery - Bloom 5] Làm sao để hợp thức hóa hồ sơ phê duyệt chi phí phát sinh (Variation Order) trong đêm nay để sáng mai Ngân hàng kịp giải ngân?",
                                "expected_bloom_level": 5
                            }
                        ]
                    }
                else:
                    # Default: Operations/Technical
                    mock = {
                        "scenario_title": "[Demo Mock] Rò rỉ hệ thống làm mát thứ cấp Urea",
                        "background_context": f"Bối cảnh (Layer 3 - {company_name}): Lúc 02:45 sáng, hệ thống áo động đỏ. Áp suất tháp phản ứng Urea vượt mức an toàn 15%, ban xả tự động bị kẹt. Khí Amoniac có nguy cơ bùng phát.",
                        "questions": [
                            {
                                "id": "Q1",
                                "targeted_competency": "Quy chuẩn An toàn (SOP)",
                                "question_text": "[SOP - Bloom 3] Dựa trên quy chuẩn xả áp khẩn cấp SOP, liệt kê thứ tự đóng/mở van tay cô lập hệ thống trong 2 phút tới mà không nổ tháp?",
                                "expected_bloom_level": 3
                            },
                            {
                                "id": "Q2",
                                "targeted_competency": "Phân tích Thông số DCS (T - Technical)",
                                "question_text": "[Technical - Bloom 4] Màn hình DCS báo lỗi Flowmeter. Làm sao để đánh giá chéo áp suất thực tế thông qua các cụm cảm biến nhiệt và lưu lượng bù?",
                                "expected_bloom_level": 4
                            },
                            {
                                "id": "Q3",
                                "targeted_competency": "Ca trưởng Điều phối (L - Leadership)",
                                "question_text": "[Leadership - Bloom 4] Phân rã nhiệm vụ cho 3 kỹ sư trực ca. Ai đi xả van tay, ai mặc đồ bảo hộ, ai ở lại phòng điều khiển?",
                                "expected_bloom_level": 4
                            },
                            {
                                "id": "Q4",
                                "targeted_competency": "Kỹ năng Hiện trường (D - Delivery)",
                                "question_text": "[Delivery - Bloom 5] Cửa phòng van bị kẹt do biến dạng nhiệt. Bạn phải giải cứu kỹ sư hiện trường đang mặc đồ bảo hộ bị kẹt bên trong thế nào?",
                                "expected_bloom_level": 5
                            },
                            {
                                "id": "Q5",
                                "targeted_competency": "Plant Trip Decision (D - Delivery)",
                                "question_text": "[Delivery - Bloom 5] Thiết bị hạ áp thủ công rỉ sét. Lựa chọn duy nhất là bấm 'Plant Trip' (ngừng máy). Mô phỏng chuỗi lệnh vô tuyến vô cùng căng thẳng của bạn?",
                                "expected_bloom_level": 5
                            }
                        ]
                    }

                mock["role"] = role_name
                return mock
                
            return {
                "error": error_msg,
                "role": role_data.get("role"),
                "questions": []
            }
