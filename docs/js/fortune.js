// 拜拜好日子查詢系統
class FortuneChecker {
    constructor() {
        this.fortuneData = this.initFortuneData();
        this.stemBranch = this.initStemBranch();
    }

    // 初始化天干地支
    initStemBranch() {
        const stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
        const branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
        return { stems, branches };
    }

    // 初始化拜拜好日子資料
    initFortuneData() {
        return {
            '甲子': { status: 'good', description: '諸神在地，求福設醮，收福十倍，大吉之兆' },
            '乙丑': { status: 'good', description: '諸神在地，求福設醮，收福十倍，大吉之兆' },
            '丙寅': { status: 'bad', description: '諸神在天，求福還願返受其殃，大凶' },
            '丁卯': { status: 'good', description: '諸神在地，求福拜表，收福十倍，大吉利' },
            '戊辰': { status: 'good', description: '諸神在地，求福拜表，收福十倍，大吉利' },
            '己巳': { status: 'good', description: '諸神在地，求福拜表，收福十倍，大吉利' },
            '庚午': { status: 'bad', description: '諸神在天，求福祭祀主人疾病，大凶' },
            '辛未': { status: 'bad', description: '諸神在天，求福祭祀主人疾病，大凶' },
            '壬申': { status: 'good', description: '諸神在天止於地府，求福祭祀收福十倍，大吉利' },
            '癸酉': { status: 'neutral', description: '祭祀河泊水官大吉，其餘求福者凶' },
            '甲戌': { status: 'bad', description: '諸神在天不在人間，小求福卻受其殃' },
            '乙亥': { status: 'bad', description: '諸神在天不在人間，小求福卻受其殃' },
            '丙子': { status: 'bad', description: '諸神破，天曹追上門，求福返諸橫禍，大凶' },
            '丁丑': { status: 'bad', description: '諸神破，天曹追上門，求福返諸橫禍，大凶' },
            '戊寅': { status: 'bad', description: '諸神破，天曹追上門，求福返諸橫禍，大凶' },
            '己卯': { status: 'good', description: '諸神下地府，求福利益子孫榮華富貴，大吉' },
            '庚辰': { status: 'good', description: '諸神下地府，求福利益子孫榮華富貴，大吉' },
            '辛巳': { status: 'bad', description: '諸神在天運石土塔，求福即死三代，大凶' },
            '壬午': { status: 'bad', description: '諸神在天，求福主人死田蚤不收，大凶' },
            '癸未': { status: 'bad', description: '諸神在天，求福主人死田蚤不收，大凶' },
            '甲申': { status: 'good', description: '諸神降下地府人間，求福祭祀收福十倍，大吉利' },
            '乙酉': { status: 'good', description: '諸神降下地府人間，求福祭祀收福十倍，大吉利' },
            '丙戌': { status: 'good', description: '諸神降下地府人間，求福祭祀，大吉' },
            '丁亥': { status: 'good', description: '諸神降下地府人間，求福祭祀，大吉' },
            '戊子': { status: 'good', description: '諸神在地府，求福祭祀了願酬恩，大吉' },
            '己丑': { status: 'good', description: '諸神在地府，求福祭祀了願酬恩，大吉' },
            '庚寅': { status: 'bad', description: '諸神在天會筭簿案，求福令人落水，大凶' },
            '辛卯': { status: 'neutral', description: '諸神在地府，小小立願召魂代命，平吉利' },
            '壬辰': { status: 'bad', description: '諸神在天勘會生死文簿，求福主疾病，大凶' },
            '癸巳': { status: 'bad', description: '諸神在天勘會生死文簿，求福主疾病，大凶' },
            '甲午': { status: 'good', description: '諸神普降人間，求福收福大利十倍，大吉利' },
            '乙未': { status: 'neutral', description: '諸神在天，作福不得，小吉' },
            '丙申': { status: 'bad', description: '諸神在天玉帝殿前造死文簿，求福祭祀大凶' },
            '丁酉': { status: 'bad', description: '諸神在天玉帝殿前造死文簿，求福祭祀大凶' },
            '戊戌': { status: 'bad', description: '諸神在天玉帝殿前造死文簿，求福祭祀大凶' },
            '己亥': { status: 'good', description: '諸神從玉皇差降人問地府，祭祀求福主人壽長，大吉利' },
            '庚子': { status: 'bad', description: '諸神在天，求福祭祀主見疾病瘟疫，大凶' },
            '辛丑': { status: 'bad', description: '諸神在天，求福祭祀主見疾病瘟疫，大凶' },
            '壬寅': { status: 'good', description: '記會之簿，求福許願謝天地，百事大吉' },
            '癸卯': { status: 'good', description: '記會之簿，求福許願謝天地，百事大吉' },
            '甲辰': { status: 'bad', description: '諸神在天宮，求福大凶' },
            '乙巳': { status: 'good', description: '諸神在人間地府，求福祭祀收福十倍，大吉' },
            '丙午': { status: 'bad', description: '諸神在天不在人間，求福大凶' },
            '丁未': { status: 'good', description: '諸神在地府，求福了願拜章，大吉' },
            '戊申': { status: 'bad', description: '諸神在天不在人間地府，求福損家長，大凶' },
            '己酉': { status: 'good', description: '上界天赦，求福進田蠶，大吉' },
            '庚戌': { status: 'neutral', description: '諸神在天上，小小祈福半吉，上章拜表大凶' },
            '辛亥': { status: 'neutral', description: '諸神在天上，小小祈福半吉，上章拜表大凶' },
            '壬子': { status: 'bad', description: '諸神在天宮，求福了願主殺人口，大凶' },
            '癸丑': { status: 'bad', description: '諸神在天宮，求福了願主殺人口，大凶' },
            '甲寅': { status: 'good', description: '諸神在人間地府，求福上章延生度厄，大吉' },
            '乙卯': { status: 'good', description: '諸神在人間地府，求福上章延生度厄，大吉' },
            '丙辰': { status: 'bad', description: '諸神在天，求福祭祀招禍損六畜，大凶' },
            '丁巳': { status: 'bad', description: '諸神在天，求福祭祀招禍損六畜，大凶' },
            '戊午': { status: 'bad', description: '諸神在天，求福祭祀招禍損六畜，大凶' },
            '己未': { status: 'bad', description: '諸神在天，求福祭祀招禍損六畜，大凶' },
            '庚申': { status: 'good', description: '五福開道，天門開，作福祭祀，大吉' },
            '辛酉': { status: 'bad', description: '諸神從玉帝差降人間地府，求福大凶' },
            '壬戌': { status: 'bad', description: '六神窮日，人間祈福主孤寡貧窮，大凶' },
            '癸亥': { status: 'bad', description: '六神窮日，人間祈福主孤寡貧窮，大凶' }
        };
    }

    // 計算指定日期的天干地支
    getStemBranch(date) {
        // 使用更準確的算法：以公元1年1月1日為起點
        // 公元1年1月1日是甲子日（這是傳統曆法的基準）
        
        const targetDate = new Date(date);
        
        // 計算從公元1年1月1日到目標日期的天數
        // 公元1年1月1日的Julian Day Number是1721426
        const year = targetDate.getFullYear();
        const month = targetDate.getMonth() + 1; // JavaScript月份從0開始
        const day = targetDate.getDate();
        
        // 計算Julian Day Number
        let a = Math.floor((14 - month) / 12);
        let y = year + 4800 - a;
        let m = month + 12 * a - 3;
        
        let jdn = day + Math.floor((153 * m + 2) / 5) + 365 * y + 
                  Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400) - 32045;
        
        // 公元1年1月1日的JDN是1721426，對應甲子日
        // 計算天干地支索引
        const daysSinceEpoch = jdn - 1721426;
        const stemBranchIndex = daysSinceEpoch % 60;
        
        // 確保索引為正數
        const positiveIndex = stemBranchIndex >= 0 ? stemBranchIndex : stemBranchIndex + 60;
        
        // 計算天干和地支
        const stemIndex = positiveIndex % 10;
        const branchIndex = positiveIndex % 12;
        
        const stem = this.stemBranch.stems[stemIndex];
        const branch = this.stemBranch.branches[branchIndex];
        
        return stem + branch;
    }
    
    // 驗證天干地支計算的輔助方法
    validateStemBranch() {
        // 一些已知的日期和對應的天干地支，用於驗證
        const knownDates = [
            { date: new Date(2024, 0, 1), expected: '癸卯' }, // 2024年1月1日
            { date: new Date(2024, 1, 10), expected: '甲子' }, // 2024年2月10日是甲子日（春節）
            { date: new Date(2025, 0, 1), expected: '戊申' }, // 2025年1月1日
        ];
        
        console.log('=== 天干地支計算驗證 ===');
        knownDates.forEach(item => {
            const calculated = this.getStemBranch(item.date);
            const isCorrect = calculated === item.expected;
            console.log(`${item.date.toLocaleDateString()}: 計算=${calculated}, 預期=${item.expected}, ${isCorrect ? '✓' : '✗'}`);
        });
    }

    // 獲取今日拜拜資訊
    getTodayFortune() {
        const today = new Date();
        const stemBranch = this.getStemBranch(today);
        const fortune = this.fortuneData[stemBranch];
        
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
        const weekday = weekdays[today.getDay()];
        
        return {
            date: `${year}年${month}月${day}日 (週${weekday})`,
            stemBranch: stemBranch,
            status: fortune ? fortune.status : 'neutral',
            description: fortune ? fortune.description : '資料不詳',
            emoji: this.getStatusEmoji(fortune ? fortune.status : 'neutral'),
            calculationInfo: this.getCalculationInfo(today)
        };
    }
    
    // 獲取計算過程資訊（用於調試和說明）
    getCalculationInfo(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        
        // 計算Julian Day Number的過程
        let a = Math.floor((14 - month) / 12);
        let y = year + 4800 - a;
        let m = month + 12 * a - 3;
        
        let jdn = day + Math.floor((153 * m + 2) / 5) + 365 * y + 
                  Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400) - 32045;
        
        const daysSinceEpoch = jdn - 1721426;
        const stemBranchIndex = daysSinceEpoch % 60;
        const positiveIndex = stemBranchIndex >= 0 ? stemBranchIndex : stemBranchIndex + 60;
        
        return {
            julianDayNumber: jdn,
            daysSinceEpoch: daysSinceEpoch,
            stemBranchIndex: positiveIndex,
            stemIndex: positiveIndex % 10,
            branchIndex: positiveIndex % 12
        };
    }

    // 獲取狀態對應的表情符號
    getStatusEmoji(status) {
        switch (status) {
            case 'good': return '✨';
            case 'bad': return '⚠️';
            case 'neutral': return '📅';
            default: return '📅';
        }
    }

    // 獲取狀態文字
    getStatusText(status) {
        switch (status) {
            case 'good': return '宜拜拜';
            case 'bad': return '不宜拜拜';
            case 'neutral': return '謹慎拜拜';
            default: return '普通日子';
        }
    }
}

// 初始化拜拜好日子系統
const fortuneChecker = new FortuneChecker();

// 更新頁面顯示
function updateFortuneDisplay() {
    const fortuneInfo = document.getElementById('fortune-info');
    const dailyFortune = document.getElementById('daily-fortune');
    
    if (fortuneInfo && dailyFortune) {
        const todayFortune = fortuneChecker.getTodayFortune();
        
        // 更新內容
        fortuneInfo.innerHTML = `
            ${todayFortune.emoji} ${todayFortune.date} ${todayFortune.stemBranch}日 - ${fortuneChecker.getStatusText(todayFortune.status)}<br>
            <small>${todayFortune.description}</small>
        `;
        
        // 更新樣式
        dailyFortune.className = `daily-fortune fortune-${todayFortune.status}`;
    }
}

// 頁面載入完成後執行
document.addEventListener('DOMContentLoaded', updateFortuneDisplay);