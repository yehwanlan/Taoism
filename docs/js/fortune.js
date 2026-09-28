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

    // 計算指定日期的日干支（使用標準演算法）
    getStemBranch(date, useTraditionalTime = true) {
        let targetDate = new Date(date);
        
        // 傳統子時分界處理：23:00-00:59為下一日
        if (useTraditionalTime) {
            const hour = targetDate.getHours();
            if (hour >= 23) {
                // 子時屬於下一日
                targetDate = new Date(targetDate.getTime() + 24 * 60 * 60 * 1000);
            }
        }
        
        const year = targetDate.getFullYear();
        const month = targetDate.getMonth() + 1; // JavaScript月份從0開始
        const day = targetDate.getDate();
        
        // 計算儒略日數 (Julian Day Number) - 標準格里高利曆公式
        let a = Math.floor((14 - month) / 12);
        let y = year + 4800 - a;
        let m = month + 12 * a - 3;
        
        let jdn = day + Math.floor((153 * m + 2) / 5) + 365 * y + 
                  Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400) - 32045;
        
        // 使用標準演算法：直接從儒略日數推日干支
        // 天干索引（0–9） = (JDN + 9) % 10
        // 地支索引（0–11） = (JDN + 1) % 12
        const stemIndex = (jdn + 9) % 10;
        const branchIndex = (jdn + 1) % 12;
        
        const stem = this.stemBranch.stems[stemIndex];
        const branch = this.stemBranch.branches[branchIndex];
        
        return stem + branch;
    }
    
    // 根據索引獲取天干地支（用於查表和調試）
    getStemBranchByIndex(index) {
        if (index < 0 || index >= 60) {
            throw new Error('索引必須在0-59之間');
        }
        
        const stemIndex = index % 10;
        const branchIndex = index % 12;
        
        return this.stemBranch.stems[stemIndex] + this.stemBranch.branches[branchIndex];
    }
    
    // 獲取某月所有日期的日干支
    getMonthStemBranch(year, month) {
        const daysInMonth = new Date(year, month, 0).getDate();
        const result = [];
        
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month - 1, day);
            const stemBranch = this.getStemBranch(date);
            const fortune = this.fortuneData[stemBranch];
            
            result.push({
                date: `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`,
                weekday: ['日', '一', '二', '三', '四', '五', '六'][date.getDay()],
                stemBranch: stemBranch,
                status: fortune ? fortune.status : 'neutral',
                description: fortune ? fortune.description : '資料不詳'
            });
        }
        
        return result;
    }
    
    // 驗證日干支計算的輔助方法
    validateStemBranch() {
        console.log('=== 日干支計算驗證（使用標準演算法）===');
        console.log('⚠️ 重要說明：此處計算的是【日干支】，不是年干支！');
        console.log('標準演算法：天干索引 = (JDN + 9) % 10，地支索引 = (JDN + 1) % 12\n');
        
        // 使用正確的日干支數據進行驗證
        const knownDates = [
            { date: new Date(2000, 0, 1), expected: '戊午', note: '基準日期 (JDN=2451545)' },
            { date: new Date(2025, 0, 9), expected: '戊寅', note: '2025年1月9日' },
            { date: new Date(2025, 0, 10), expected: '己卯', note: '2025年1月10日' }
        ];
        
        knownDates.forEach(item => {
            const calculated = this.getStemBranch(item.date);
            const isCorrect = calculated === item.expected;
            console.log(`${item.date.toLocaleDateString()}: 計算=${calculated}, 預期=${item.expected}, ${isCorrect ? '✓' : '✗'} (${item.note})`);
        });
        
        // 測試連續性：檢查連續日期是否按正確順序變化
        console.log('\n=== 連續性驗證（六十甲子順序）===');
        const testDate = new Date(2000, 0, 1); // 從基準日期開始
        for (let i = 0; i < 5; i++) {
            const currentDate = new Date(testDate);
            currentDate.setDate(testDate.getDate() + i);
            const stemBranch = this.getStemBranch(currentDate);
            const jdn = this.calculateJDN(currentDate);
            console.log(`${currentDate.toLocaleDateString()}: ${stemBranch} (JDN=${jdn})`);
        }
        
        // 測試60天循環
        console.log('\n=== 六十甲子循環驗證 ===');
        const cycleTestDate = new Date(2000, 0, 1);
        const day0 = this.getStemBranch(cycleTestDate);
        
        const day60 = new Date(cycleTestDate);
        day60.setDate(cycleTestDate.getDate() + 60);
        const day60Result = this.getStemBranch(day60);
        
        console.log(`基準日 (第0天): ${day0}`);
        console.log(`60天後: ${day60Result}`);
        console.log(`循環正確: ${day0 === day60Result ? '✓' : '✗'}`);
    }
    
    // 輔助方法：計算儒略日數
    calculateJDN(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        
        let a = Math.floor((14 - month) / 12);
        let y = year + 4800 - a;
        let m = month + 12 * a - 3;
        
        return day + Math.floor((153 * m + 2) / 5) + 365 * y + 
               Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400) - 32045;
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
        const targetDate = new Date(date);
        const year = targetDate.getFullYear();
        const month = targetDate.getMonth() + 1;
        const day = targetDate.getDate();
        
        // 計算儒略日數
        let a = Math.floor((14 - month) / 12);
        let y = year + 4800 - a;
        let m = month + 12 * a - 3;
        
        let jdn = day + Math.floor((153 * m + 2) / 5) + 365 * y + 
                  Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400) - 32045;
        
        const baseJDN = 2415051; // 1900年1月31日
        const baseStemBranchIndex = 40; // 甲辰
        const daysDiff = jdn - baseJDN;
        
        let stemBranchIndex = (baseStemBranchIndex + daysDiff) % 60;
        if (stemBranchIndex < 0) {
            stemBranchIndex += 60;
        }
        
        const stemIndex = stemBranchIndex % 10;
        const branchIndex = stemBranchIndex % 12;
        
        return {
            type: '日干支計算',
            baseDate: '1900年1月31日 (甲辰日)',
            baseJDN: baseJDN,
            targetJDN: jdn,
            daysDiff: daysDiff,
            baseStemBranchIndex: baseStemBranchIndex,
            stemBranchIndex: stemBranchIndex,
            stemIndex: stemIndex,
            branchIndex: branchIndex,
            calculation: `(${baseStemBranchIndex} + ${daysDiff}) % 60 = ${stemBranchIndex}`,
            note: '此為日干支，非年干支'
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

// 共用的拜拜好日子實例（calendar.html、test-fortune.html 等頁面直接使用）
// 首頁的今日資訊由 index.html 的 initializeFortune() 負責顯示
const fortuneChecker = new FortuneChecker();