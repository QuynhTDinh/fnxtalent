import { eventBus } from './EventBus.js';

/**
 * MatchingAgent - Competency Alignment & Fit Scoring
 */
export class MatchingAgent {
    constructor() {
        this.name = "MatchingAgent";
        this.role = "Alignment Engineer";
        this.candidateComp = null;
        this.jdRequirements = null;
        this.init();
    }

    init() {
        eventBus.subscribe('COMPETENCY_MEASURED', (data) => {
            this.candidateComp = data;
            this.tryMatch();
        });

        eventBus.subscribe('REQUIREMENTS_READY', (data) => {
            this.jdRequirements = data;
            this.tryMatch();
        });
    }

    tryMatch() {
        if (this.candidateComp && this.jdRequirements) {
            this.performMatch();
        }
    }

    /**
     * Skill: Tính toán điểm phù hợp dựa trên ma trận năng lực
     */
    async performMatch() {
        console.log(`[${this.name}] Calculating Fit Score...`);

        let totalScore = 0;
        let gaps = [];

        this.jdRequirements.requirements.forEach(req => {
            const candSkill = this.candidateComp.competencies.find(s => s.code === req.code) || { level: 0 };
            const diff = candSkill.level - req.level;

            // Basic scoring logic
            if (diff >= 0) {
                totalScore += req.weight;
            } else {
                totalScore += (candSkill.level / req.level) * req.weight;
                gaps.push({
                    code: req.code,
                    gap: req.level - candSkill.level,
                    recommendation: `Tăng cường năng lực ${req.code} thêm ${Math.abs(diff)} cấp độ.`
                });
            }
        });

        eventBus.publish('MATCH_COMPLETE', {
            candidateId: this.candidateComp.candidateId,
            fitScore: Math.round(totalScore * 100),
            gaps
        });
    }
}
