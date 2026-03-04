---
name: matching-workflow
description: Quy trình tìm kiếm ứng viên phù hợp nhất cho một vị trí công việc cụ thể.
---

# WORKFLOW: Talent-Job Matching

Quy trình này được kích hoạt khi doanh nghiệp submit một Job Description (JD) mới.

## Các bước thực hiện
1. **[Skill: jd-analysis]**: Phân tích JD và tạo Ma trận yêu cầu.
2. **[Skill: fit-optimization]**: Sử dụng Vector Search và thuật toán scoring để so sánh với Database ứng viên đã được assessed.
3. **[Skill: roadmap-design]**: Phân tích Gap năng lực của Top ứng viên.
4. **[Skill: visual-insight]**: Tạo biểu đồ Radar và báo cáo Insight PDF.

## Vai trò các Agent
- **JDDecoderAgent**: Thực hiện bước 1.
- **MatchingAgent**: Thực hiện bước 2.
- **ReportingAgent**: Thực hiện bước 3, 4.
