import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from core.taxonomy import get_taxonomy

def run_benchmark():
    taxonomy = get_taxonomy()
    
    # 02 Profiles mẫu (Mô phỏng kết quả đánh giá ASK)
    profiles = [
        {
            "name": "Nguyễn Văn A (Kỹ sư chuyên gia)",
            "scores": {
                "K1": 5, "K2": 4, "K3": 4,  # Knowledge
                "S1": 3, "S2": 5, "S3": 3, "S4": 4, "S5": 3, # Skill
                "A1": 4, "A2": 3, "A3": 3  # Attitude
            }
        },
        {
            "name": "Lê Thị B (Quản lý dự án)",
            "scores": {
                "K1": 3, "K2": 2, "K3": 3,
                "S1": 5, "S2": 3, "S3": 5, "S4": 4, "S5": 5,
                "A1": 4, "A2": 5, "A3": 5
            }
        }
    ]

    print("="*60)
    print("BÁO CÁO ĐỐI SOÁT KIẾN TRÚC 3 LỚP (FNX BENCHMARK)")
    print("="*60)

    for p in profiles:
        print(f"\nỨng viên: {p['name']}")
        print("-" * 30)
        
        # 1. Tính toán theo Katz (Cây phả hệ cũ - Legacy)
        katz_results = {}
        for zone_id, zone in taxonomy.katz_zones.items():
            comp_scores = [p['scores'].get(cid, 0) for cid in zone.competency_ids]
            avg = sum(comp_scores) / len(comp_scores) if comp_scores else 0
            katz_results[zone_id] = avg

        # 2. Tính toán theo T-L-D (Lõi tính toán mới - New Engine)
        tld_results = {}
        for zone_id, zone in taxonomy.tld_zones.items():
            comp_scores = [p['scores'].get(cid, 0) for cid in zone.competency_ids]
            avg = sum(comp_scores) / len(comp_scores) if comp_scores else 0
            tld_results[zone_id] = avg

        # 3. Hiển thị so sánh
        print(f"{'Nhãn hiển thị (UI)':<20} | {'Điểm (Katz)':<12} | {'Lõi nội bộ (TLD)':<15} | {'Điểm (TLD)':<10}")
        print("-" * 65)
        
        # Mapping: Technical -> Technique
        print(f"{'Technical (Kỹ thuật)':<20} | {katz_results['TECHNICAL']:<12.2f} | {'Technique':<15} | {tld_results['TECHNIQUE']:<10.2f}")
        
        # Mapping: Interpersonal (Human) -> Language
        print(f"{'Interpersonal (Người)':<20} | {katz_results['INTERPERSONAL']:<12.2f} | {'Language':<15} | {tld_results['LANGUAGE']:<10.2f}")
        
        # Mapping: Conceptual (Tư duy) -> Digital
        print(f"{'Conceptual (Tư duy)':<20} | {katz_results['CONCEPTUAL']:<12.2f} | {'Digital':<15} | {tld_results['DIGITAL']:<10.2f}")
        
        # Nhận xét về sự thay đổi
        diff = tld_results['TECHNIQUE'] - katz_results['TECHNICAL']
        if diff > 0:
            print(f"\n[!] Nhận xét: Điểm Technical tăng {diff:.2f} do S2 (Giải quyết vấn đề) đã được đưa vào lõi Technique.")
        elif diff < 0:
            print(f"\n[!] Nhận xét: Điểm Technical thay đổi do cấu trúc lại nhóm năng lực.")

    print("\n" + "="*60)
    print("KẾT LUẬN: Backend T-L-D đã sẵn sàng. Giao diện vẫn bảo trì nhãn cũ.")
    print("="*60)

if __name__ == "__main__":
    run_benchmark()
