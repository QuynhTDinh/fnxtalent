/**
 * FNX Factory Demo - Running the Full Pipeline
 */
import { FactoryCoordinator } from './src/lib/agents/FactoryCoordinator.js';

const factory = new FactoryCoordinator();

const sampleCandidate = {
    fullName: "Nguyễn Văn A",
    major: "Kỹ thuật Hóa học"
};

const sampleJD = `
    Cần tuyển Kỹ sư Hóa dầu cao cấp. 
    Yêu cầu: Có tư duy hệ thống mạnh (HOS.1), 
    Kỹ năng vận hành thực tế (WF.1) 
    và kiến thức chuyên mục polymer (SCI.1).
`;

async function main() {
    const report = await factory.runFullPipeline(sampleCandidate, sampleJD);

    console.log("=== KẾT QUẢ BÁO CÁO FNX INSIGHT ===");
    console.log(JSON.stringify(report, null, 2));
}

main().catch(console.error);
