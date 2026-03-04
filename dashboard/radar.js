/**
 * FNX Radar Chart Engine
 * 
 * Premium radar chart with dual-layer rendering (SHL style):
 * - Layer 1: Candidate actual competencies (filled polygon)
 * - Layer 2: Job target requirements (outline polygon)
 * 
 * Features:
 * - Smooth entrance animation
 * - Interactive hover tooltips
 * - Level ring labels (1-5)
 * - Domain-coded axis colors
 * - HiDPI/Retina support
 */

class RadarChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        // HiDPI scaling
        this.dpr = window.devicePixelRatio || 1;
        this.logicalWidth = options.width || 520;
        this.logicalHeight = options.height || 520;
        this.canvas.width = this.logicalWidth * this.dpr;
        this.canvas.height = this.logicalHeight * this.dpr;
        this.canvas.style.width = this.logicalWidth + 'px';
        this.canvas.style.height = this.logicalHeight + 'px';
        this.ctx.scale(this.dpr, this.dpr);

        this.center = { x: this.logicalWidth / 2, y: this.logicalHeight / 2 };
        this.radius = Math.min(this.logicalWidth, this.logicalHeight) / 2 - 65;
        this.levels = options.levels || 5;

        // Styling — Apple HIG colors
        this.colors = {
            candidate: options.candidateColor || '#0071e3',
            candidateFill: options.candidateFill || 'rgba(0, 113, 227, 0.08)',
            target: options.targetColor || '#ff2d55',
            targetFill: options.targetFill || 'rgba(255, 45, 85, 0.04)',
            grid: options.gridColor || 'rgba(0, 0, 0, 0.06)',
            gridText: options.gridTextColor || '#86868b',
            axisLabel: options.axisLabelColor || '#6e6e73',
            axisLabelActive: '#1d1d1f',
        };

        // Domain color mapping (Apple system colors)
        this.domainColors = {
            'HOS': '#af52de', // Mindset - purple
            'PD': '#af52de',
            'WF': '#5ac8fa',  // Skills - teal
            'ELA': '#5ac8fa',
            'SCI': '#34c759', // Knowledge - green
            'MATH': '#34c759',
            'SS': '#34c759',
        };

        // Data
        this.axes = [];
        this.candidateData = [];
        this.targetData = [];

        // Animation
        this.animationProgress = 0;
        this.isAnimating = false;

        // Hover
        this.hoveredAxis = -1;
        this._setupHover();
    }

    /**
     * Set data and begin rendering.
     * @param {Array<{code, name, area}>} axes - Competency axes
     * @param {Array<number>} candidateValues - Candidate levels (0-5)
     * @param {Array<number>} targetValues - Target levels (0-5)
     */
    setData(axes, candidateValues, targetValues = []) {
        this.axes = axes;
        this.candidateData = candidateValues;
        this.targetData = targetValues;
        this.animate();
    }

    animate() {
        this.animationProgress = 0;
        this.isAnimating = true;
        const duration = 1200;
        const startTime = performance.now();

        const tick = (now) => {
            const elapsed = now - startTime;
            // Ease out cubic
            const t = Math.min(elapsed / duration, 1);
            this.animationProgress = 1 - Math.pow(1 - t, 3);

            this.render();

            if (t < 1) {
                requestAnimationFrame(tick);
            } else {
                this.isAnimating = false;
            }
        };

        requestAnimationFrame(tick);
    }

    render() {
        const { ctx, center, radius, levels } = this;
        const n = this.axes.length;
        if (n === 0) return;

        ctx.clearRect(0, 0, this.logicalWidth, this.logicalHeight);

        // 1. Draw concentric level rings
        this._drawLevelRings(n);

        // 2. Draw axis lines
        this._drawAxes(n);

        // 3. Draw target polygon (background layer)
        if (this.targetData.length === n) {
            this._drawPolygon(this.targetData, this.colors.target, this.colors.targetFill, 1.5, true);
        }

        // 4. Draw candidate polygon (foreground layer)
        this._drawPolygon(this.candidateData, this.colors.candidate, this.colors.candidateFill, 2.5, false);

        // 5. Draw data points
        this._drawDataPoints(this.candidateData, this.colors.candidate);
        if (this.targetData.length === n) {
            this._drawTargetPoints(this.targetData, this.colors.target);
        }

        // 6. Draw axis labels
        this._drawAxisLabels(n);

        // 7. Draw level labels
        this._drawLevelLabels();
    }

    _drawLevelRings(n) {
        const { ctx, center, radius, levels } = this;

        for (let lvl = 1; lvl <= levels; lvl++) {
            const r = (radius / levels) * lvl;
            ctx.beginPath();
            for (let i = 0; i <= n; i++) {
                const angle = (Math.PI * 2 / n) * i - Math.PI / 2;
                const x = center.x + r * Math.cos(angle);
                const y = center.y + r * Math.sin(angle);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.closePath();
            ctx.strokeStyle = this.colors.grid;
            ctx.lineWidth = 1;
            ctx.stroke();

            // Subtle fill on every other ring
            if (lvl % 2 === 0) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.01)';
                ctx.fill();
            }
        }
    }

    _drawAxes(n) {
        const { ctx, center, radius } = this;

        for (let i = 0; i < n; i++) {
            const angle = (Math.PI * 2 / n) * i - Math.PI / 2;
            const x = center.x + radius * Math.cos(angle);
            const y = center.y + radius * Math.sin(angle);

            ctx.beginPath();
            ctx.moveTo(center.x, center.y);
            ctx.lineTo(x, y);

            const axisColor = this.domainColors[this.axes[i]?.area] || this.colors.grid;
            ctx.strokeStyle = this.hoveredAxis === i
                ? axisColor
                : this.colors.grid;
            ctx.lineWidth = this.hoveredAxis === i ? 1.5 : 0.5;
            ctx.stroke();
        }
    }

    _drawPolygon(data, strokeColor, fillColor, lineWidth, isDashed) {
        const { ctx, center, radius, levels } = this;
        const n = data.length;
        const progress = this.animationProgress;

        ctx.beginPath();
        for (let i = 0; i <= n; i++) {
            const idx = i % n;
            const value = data[idx] * progress;
            const r = (radius / levels) * value;
            const angle = (Math.PI * 2 / n) * idx - Math.PI / 2;
            const x = center.x + r * Math.cos(angle);
            const y = center.y + r * Math.sin(angle);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();

        // Fill
        ctx.fillStyle = fillColor;
        ctx.fill();

        // Stroke
        if (isDashed) {
            ctx.setLineDash([6, 4]);
        }
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = lineWidth;
        ctx.stroke();
        ctx.setLineDash([]);
    }

    _drawDataPoints(data, color) {
        const { ctx, center, radius, levels } = this;
        const n = data.length;
        const progress = this.animationProgress;

        for (let i = 0; i < n; i++) {
            const value = data[i] * progress;
            const r = (radius / levels) * value;
            const angle = (Math.PI * 2 / n) * i - Math.PI / 2;
            const x = center.x + r * Math.cos(angle);
            const y = center.y + r * Math.sin(angle);

            const isHovered = this.hoveredAxis === i;
            const pointRadius = isHovered ? 6 : 4;

            // Glow
            ctx.beginPath();
            ctx.arc(x, y, pointRadius + 4, 0, Math.PI * 2);
            ctx.fillStyle = color.replace(')', ', 0.15)').replace('rgb', 'rgba');
            ctx.fill();

            // Point
            ctx.beginPath();
            ctx.arc(x, y, pointRadius, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.fill();

            // Inner white dot
            ctx.beginPath();
            ctx.arc(x, y, pointRadius * 0.35, 0, Math.PI * 2);
            ctx.fillStyle = '#fff';
            ctx.fill();
        }
    }

    _drawTargetPoints(data, color) {
        const { ctx, center, radius, levels } = this;
        const n = data.length;
        const progress = this.animationProgress;

        for (let i = 0; i < n; i++) {
            const value = data[i] * progress;
            const r = (radius / levels) * value;
            const angle = (Math.PI * 2 / n) * i - Math.PI / 2;
            const x = center.x + r * Math.cos(angle);
            const y = center.y + r * Math.sin(angle);

            // Diamond shape for target
            const size = 4;
            ctx.beginPath();
            ctx.moveTo(x, y - size);
            ctx.lineTo(x + size, y);
            ctx.lineTo(x, y + size);
            ctx.lineTo(x - size, y);
            ctx.closePath();
            ctx.fillStyle = color;
            ctx.globalAlpha = 0.7;
            ctx.fill();
            ctx.globalAlpha = 1;
        }
    }

    _drawAxisLabels(n) {
        const { ctx, center, radius } = this;
        const labelOffset = 30;

        for (let i = 0; i < n; i++) {
            const angle = (Math.PI * 2 / n) * i - Math.PI / 2;
            const x = center.x + (radius + labelOffset) * Math.cos(angle);
            const y = center.y + (radius + labelOffset) * Math.sin(angle);

            const axis = this.axes[i];
            const isHovered = this.hoveredAxis === i;
            const domainColor = this.domainColors[axis?.area] || this.colors.axisLabel;

            // Code label
            ctx.font = `${isHovered ? '600' : '500'} 11px -apple-system, 'SF Mono', monospace`;
            ctx.fillStyle = isHovered ? domainColor : this.colors.axisLabel;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(axis?.code || '', x, y - 7);

            // Name label
            ctx.font = `400 9px -apple-system, 'SF Pro Text', sans-serif`;
            ctx.fillStyle = isHovered ? this.colors.axisLabelActive : this.colors.gridText;

            // Truncate long names
            let name = axis?.name || '';
            if (name.length > 18) name = name.substring(0, 16) + '…';
            ctx.fillText(name, x, y + 7);
        }
    }

    _drawLevelLabels() {
        const { ctx, center, radius, levels } = this;
        const levelNames = ['', 'Foundation', 'Developing', 'Proficient', 'Advanced', 'Mastery'];

        for (let lvl = 1; lvl <= levels; lvl++) {
            const r = (radius / levels) * lvl;
            const x = center.x + 4;
            const y = center.y - r - 3;

            ctx.font = '500 8px -apple-system, "SF Mono", monospace';
            ctx.fillStyle = this.colors.gridText;
            ctx.textAlign = 'left';
            ctx.textBaseline = 'bottom';
            ctx.fillText(`L${lvl}`, x, y);
        }
    }

    _setupHover() {
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;
            const n = this.axes.length;
            if (n === 0) return;

            let closestIdx = -1;
            let closestDist = 40; // threshold px

            for (let i = 0; i < n; i++) {
                const angle = (Math.PI * 2 / n) * i - Math.PI / 2;
                const value = this.candidateData[i] || 0;
                const r = (this.radius / this.levels) * value;
                const px = this.center.x + r * Math.cos(angle);
                const py = this.center.y + r * Math.sin(angle);
                const dist = Math.sqrt((mx - px) ** 2 + (my - py) ** 2);
                if (dist < closestDist) {
                    closestDist = dist;
                    closestIdx = i;
                }
            }

            if (this.hoveredAxis !== closestIdx) {
                this.hoveredAxis = closestIdx;
                this.canvas.style.cursor = closestIdx >= 0 ? 'pointer' : 'default';
                if (!this.isAnimating) this.render();
            }
        });

        this.canvas.addEventListener('mouseleave', () => {
            this.hoveredAxis = -1;
            this.canvas.style.cursor = 'default';
            if (!this.isAnimating) this.render();
        });
    }
}
