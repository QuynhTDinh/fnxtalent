---
name: active-hunting
category: ingestion
description: Kỹ năng chủ động tìm kiếm và khai thác hồ sơ ứng viên tiềm năng từ các nguồn công khai (LinkedIn, GitHub, Google Scholar, v.v.).
---

# SKILL: Active Hunting (External Sourcing)

## Mục tiêu
Tự động tìm kiếm ứng viên dựa trên các từ khóa (Keywords) hoặc Ma trận yêu cầu (Requirements Matrix) từ JD.

## Quy trình xử lý
1. **Target Identification**: Dựa trên JD, xác định các chức danh, kỹ năng và công ty mục tiêu (ví dụ: "Kỹ sư lọc hóa dầu" tại "Nghi Sơn").
2. **Platform Search**: Sử dụng MCP Tools để tìm kiếm trên LinkedIn, Google Scholar, và danh bạ chuyên gia.
3. **Data Pre-extraction**: Thu thập các thông tin sơ bộ (Họ tên, vị trí hiện tại, thành tựu chính).
4. **Lead Generation**: Tạo danh sách "Potential Leads" để đưa vào quy trình Enrichment.

## Công cụ sử dụng
- LinkedIn Sales Navigator (via MCP)
- Google Custom Search Engine
- GitHub Search API (cho các hồ sơ kỹ thuật)

## Templates
- `./templates/hunting_lead.json`
