/**
 * FactoryCoordinator - System Initializer for Event-Driven Architecture
 */
import { SourcingAgent } from './SourcingAgent.js';
import { AssessmentAgent } from './AssessmentAgent.js';
import { JDDecoderAgent } from './JDDecoderAgent.js';
import { MatchingAgent } from './MatchingAgent.js';
import { ReportingAgent } from './ReportingAgent.js';

export class FactoryCoordinator {
    constructor() {
        // Khởi tạo các Agent độc lập
        // Khi khởi tạo, chúng sẽ tự động đăng ký (subscribe) vào EventBus
        this.sourcing = new SourcingAgent();
        this.assessment = new AssessmentAgent();
        this.jdDecoder = new JDDecoderAgent();
        this.matching = new MatchingAgent();
        this.reporting = new ReportingAgent();

        console.log("[FactoryCoordinator] Hệ thống FNX (Event-Driven) đã sẵn sàng.");
    }

    /**
     * Trong mô hình Event-Driven, chúng ta không gọi runFullPipeline.
     * Thay vào đó, chúng ta bắn sự kiện vào EventBus từ ngoài hệ thống (API/UI).
     */
}
