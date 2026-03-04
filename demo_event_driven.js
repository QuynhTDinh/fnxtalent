/**
 * FNX Event-Driven Factory Demo
 */
import { eventBus } from './src/lib/agents/EventBus.js';
import { SourcingAgent } from './src/lib/agents/SourcingAgent.js';
import { AssessmentAgent } from './src/lib/agents/AssessmentAgent.js';
import { JDDecoderAgent } from './src/lib/agents/JDDecoderAgent.js';
import { MatchingAgent } from './src/lib/agents/MatchingAgent.js';
import { ReportingAgent } from './src/lib/agents/ReportingAgent.js';

// Khởi tạo các Agent (Chúng sẽ tự động subscribe)
const sourcing = new SourcingAgent();
const assessment = new AssessmentAgent();
const jdDecoder = new JDDecoderAgent();
const matching = new MatchingAgent();
const reporting = new ReportingAgent();

// Lắng nghe kết quả cuối cùng để hiển thị
eventBus.on('REPORT_FINALIZED', (report) => {
    console.log("\n=== [EVENT-DRIVEN] BÁO CÁO CUỐI CÙNG HIỆN THỊ TRÊN DASHBOARD ===");
    console.log(JSON.stringify(report, null, 2));
});

// Giả lập luồng công việc bắt đầu bằng các sự kiện độc lập
console.log("--- BẮT ĐẦU LUỒNG SỰ KIỆN ---");

// 1. Có dữ liệu ứng viên mới từ Kỷ yếu
eventBus.publish('RAW_DATA_RECEIVED', { id: 'cand_999', fullName: 'Lê Văn C' });

// 2. Doanh nghiệp submit JD
eventBus.publish('JD_SUBMITTED', {
    text: "Tuyển kỹ sư Hóa dầu am hiểu polymer và quản lý hệ thống."
});
