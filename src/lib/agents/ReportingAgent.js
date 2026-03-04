import { eventBus } from './EventBus.js';

/**
 * ReportingAgent - Insight Report Generation
 */
export class ReportingAgent {
    constructor() {
        this.name = "ReportingAgent";
        this.role = "Insight Editor";
        this.init();
    }

    init() {
        eventBus.subscribe('MATCH_COMPLETE', async (data) => {
            await this.finalizeReport(data);
        });
    }

    async finalizeReport(data) {
        console.log(`[${this.name}] Finalizing report for match score: ${data.fitScore}%`);
        const report = {
            candidateId: data.candidateId,
            fitScore: data.fitScore,
            gaps: data.gaps,
            recommendation: data.fitScore > 80 ? "Sẵn sàng phỏng vấn" : "Cần đào tạo thêm",
            timestamp: new Date().toISOString()
        };

        eventBus.publish('REPORT_FINALIZED', report);
    }
}
