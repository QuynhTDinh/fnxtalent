---
name: data-normalization
category: common/utility
description: Kỹ năng chuẩn hóa định dạng dữ liệu (Họ tên, ngày tháng, chuyên ngành) để đảm bảo tính nhất quán trên toàn hệ thống.
---

# SKILL: Data Normalization

## Mục tiêu
Đảm bảo mọi dữ liệu thô từ các nguồn khác nhau (PDF, LinkedIn, Google Form) được đưa về một cấu trúc chuẩn duy nhất trước khi đưa vào bộ máy Assessment.

## Danh sách công việc
1. **Clean Name**: Loại bỏ ký tự đặc biệt, chuẩn hóa chữ hoa/thường cho Họ tên.
2. **Format Date**: Chuyển đổi mọi định dạng ngày tháng về ISO 8601.
3. **Map Major**: Ánh xạ các tên chuyên ngành khác nhau về bộ danh mục chuẩn của ĐHBK/FNX.

## Templates
- `./templates/normalized_profile.json`
