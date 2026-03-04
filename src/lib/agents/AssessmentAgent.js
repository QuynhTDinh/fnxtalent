import { eventBus } from './EventBus.js';

export class AssessmentAgent {
    constructor(framework) {
        this.name = "AssessmentAgent";
        this.role = "Competency Auditor";
        this.framework = framework;
        this.init();
    }

    init() {
        eventBus.subscribe('PROFILE_READY', async (profile) => {
            await this.auditProfile(profile);
        });
    }

    async auditProfile(profile) {
        console.log(`[${this.name}] Auditing profile: ${profile.fullName}`);
        const competencies = [
            { code: "HOS.1", level: 4 },
            { code: "WF.1", level: 3 }
        ];

        eventBus.publish('COMPETENCY_MEASURED', { candidateId: profile.id, competencies });
    }
}
