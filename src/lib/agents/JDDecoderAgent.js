import { eventBus } from './EventBus.js';

/**
 * JDDecoderAgent - Job Description Analysis & Requirement Matrix
 */
export class JDDecoderAgent {
    constructor() {
        this.name = "JDDecoderAgent";
        this.role = "Requirement Strategist";
        this.init();
    }

    init() {
        eventBus.subscribe('JD_SUBMITTED', async (data) => {
            await this.processJD(data);
        });
    }

    /**
     * Skill: Trích xuất yêu cầu rõ ràng và tiềm ẩn từ JD
     */
    async processJD(data) {
        console.log(`[${this.name}] Decoding Job Description...`);

        // AI Logic simulation
        // In reality, this would use an LLM prompt to map text to Building 21 codes
        const requirements = [
            { code: "HOS.1", level: 4, weight: 0.3 },
            { code: "WF.1", level: 3, weight: 0.2 },
            { code: "SCI.1", level: 5, weight: 0.5 }
        ];

        eventBus.publish('REQUIREMENTS_READY', { jdId: data.id || 'default_jd', requirements });
    }
}
