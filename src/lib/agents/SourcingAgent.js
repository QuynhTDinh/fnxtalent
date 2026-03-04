import { eventBus } from './EventBus.js';

export class SourcingAgent {
    constructor() {
        this.name = "SourcingAgent";
        this.role = "Data Ingestion Specialist";
        this.init();
    }

    init() {
        // Lắng nghe sự kiện dữ liệu thô được đưa vào
        eventBus.subscribe('RAW_DATA_RECEIVED', async (data) => {
            await this.processRawData(data);
        });
    }

    async processRawData(data) {
        console.log(`[${this.name}] Processing raw data...`);
        // Giả lập trích xuất và làm giàu
        const profile = { id: data.id, fullName: data.fullName, status: 'PROCESSED' };

        // Phát sự kiện Hồ sơ đã sẵn sàng
        eventBus.publish('PROFILE_READY', profile);
    }
}
