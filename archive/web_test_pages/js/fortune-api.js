// 道教日干支 API 封裝
class TaoismFortuneAPI {
    constructor() {
        this.fortuneChecker = new FortuneChecker();
        this.cache = new Map();
        this.cacheExpiry = 24 * 60 * 60 * 1000; // 24小時快取
    }

    // 獲取今日資訊 API
    getTodayAPI(timezone = 'Asia/Taipei', useTraditionalTime = true) {
        const cacheKey = `today-${timezone}-${useTraditionalTime}`;

        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheExpiry) {
                return cached.data;
            }
        }

        const now = new Date();
        const localDate = this.convertToTimezone(now, timezone);
        const fortune = this.fortuneChecker.getTodayFortune();

        const result = {
            success: true,
            data: {
                date: localDate.toISOString().split('T')[0],
                localTime: localDate.toLocaleString('zh-TW', { timeZone: timezone }),
                timezone: timezone,
                useTraditionalTime: useTraditionalTime,
                stemBranch: fortune.stemBranch,
                status: fortune.status,
                statusText: this.fortuneChecker.getStatusText(fortune.status),
                description: fortune.description,
                emoji: fortune.emoji,
                calculation: fortune.calculationInfo
            },
            timestamp: Date.now()
        };

        this.cache.set(cacheKey, { data: result, timestamp: Date.now() });
        return result;
    }

    // 查詢特定日期 API
    getDateAPI(dateString, timezone = 'Asia/Taipei', useTraditionalTime = true) {
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return {
                    success: false,
                    error: '無效的日期格式，請使用 YYYY-MM-DD 格式'
                };
            }

            const localDate = this.convertToTimezone(date, timezone);
            const stemBranch = this.fortuneChecker.getStemBranch(localDate, useTraditionalTime);
            const fortune = this.fortuneChecker.fortuneData[stemBranch];
            const calculationInfo = this.fortuneChecker.getCalculationInfo(localDate);

            return {
                success: true,
                data: {
                    date: dateString,
                    localTime: localDate.toLocaleString('zh-TW', { timeZone: timezone }),
                    timezone: timezone,
                    useTraditionalTime: useTraditionalTime,
                    stemBranch: stemBranch,
                    stemBranchIndex: calculationInfo.stemBranchIndex,
                    status: fortune ? fortune.status : 'neutral',
                    statusText: this.fortuneChecker.getStatusText(fortune ? fortune.status : 'neutral'),
                    description: fortune ? fortune.description : '資料不詳',
                    calculation: calculationInfo
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    // 批量查詢月份 API
    getMonthAPI(year, month, timezone = 'Asia/Taipei', useTraditionalTime = true) {
        try {
            if (year < 1900 || year > 2100 || month < 1 || month > 12) {
                return {
                    success: false,
                    error: '年份必須在1900-2100之間，月份必須在1-12之間'
                };
            }

            const monthData = this.fortuneChecker.getMonthStemBranch(year, month);

            return {
                success: true,
                data: {
                    year: year,
                    month: month,
                    timezone: timezone,
                    useTraditionalTime: useTraditionalTime,
                    totalDays: monthData.length,
                    statistics: this.calculateMonthStatistics(monthData),
                    days: monthData.map(day => ({
                        ...day,
                        statusText: this.fortuneChecker.getStatusText(day.status)
                    }))
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    // 六十甲子查表 API
    getStemBranchTableAPI() {
        const table = [];
        for (let i = 0; i < 60; i++) {
            const stemBranch = this.fortuneChecker.getStemBranchByIndex(i);
            const fortune = this.fortuneChecker.fortuneData[stemBranch];

            table.push({
                index: i,
                stemBranch: stemBranch,
                pinyin: this.getStemBranchPinyin(stemBranch),
                english: this.getStemBranchEnglish(stemBranch),
                status: fortune ? fortune.status : 'neutral',
                statusText: this.fortuneChecker.getStatusText(fortune ? fortune.status : 'neutral'),
                description: fortune ? fortune.description : '資料不詳'
            });
        }

        return {
            success: true,
            data: {
                total: 60,
                table: table,
                statistics: this.calculateTableStatistics(table)
            }
        };
    }

    // 驗證計算準確性 API
    getValidationAPI() {
        const validationResults = [];

        // 基準驗證
        const baseTests = [
            { date: new Date(1900, 0, 31), expected: '庚子', note: '基準日期' },
            { date: new Date(1900, 1, 1), expected: '辛丑', note: '基準+1天' },
            { date: new Date(1900, 1, 2), expected: '壬寅', note: '基準+2天' }
        ];

        baseTests.forEach(test => {
            const calculated = this.fortuneChecker.getStemBranch(test.date);
            validationResults.push({
                date: test.date.toISOString().split('T')[0],
                expected: test.expected,
                calculated: calculated,
                isCorrect: calculated === test.expected,
                note: test.note
            });
        });

        // 循環驗證
        const baseDate = new Date(1900, 0, 31);
        const after60Days = new Date(baseDate.getTime() + 60 * 24 * 60 * 60 * 1000);
        const baseStemBranch = this.fortuneChecker.getStemBranch(baseDate);
        const after60StemBranch = this.fortuneChecker.getStemBranch(after60Days);

        validationResults.push({
            date: after60Days.toISOString().split('T')[0],
            expected: baseStemBranch,
            calculated: after60StemBranch,
            isCorrect: baseStemBranch === after60StemBranch,
            note: '60天循環驗證'
        });

        return {
            success: true,
            data: {
                totalTests: validationResults.length,
                passedTests: validationResults.filter(r => r.isCorrect).length,
                failedTests: validationResults.filter(r => !r.isCorrect).length,
                results: validationResults
            }
        };
    }

    // 時區轉換輔助函數
    convertToTimezone(date, timezone) {
        return new Date(date.toLocaleString('en-US', { timeZone: timezone }));
    }

    // 計算月份統計
    calculateMonthStatistics(monthData) {
        const stats = { good: 0, bad: 0, neutral: 0 };
        monthData.forEach(day => {
            stats[day.status]++;
        });

        return {
            good: { count: stats.good, percentage: (stats.good / monthData.length * 100).toFixed(1) },
            bad: { count: stats.bad, percentage: (stats.bad / monthData.length * 100).toFixed(1) },
            neutral: { count: stats.neutral, percentage: (stats.neutral / monthData.length * 100).toFixed(1) }
        };
    }

    // 計算表格統計
    calculateTableStatistics(table) {
        const stats = { good: 0, bad: 0, neutral: 0 };
        table.forEach(item => {
            stats[item.status]++;
        });

        return {
            good: { count: stats.good, percentage: (stats.good / 60 * 100).toFixed(1) },
            bad: { count: stats.bad, percentage: (stats.bad / 60 * 100).toFixed(1) },
            neutral: { count: stats.neutral, percentage: (stats.neutral / 60 * 100).toFixed(1) }
        };
    }

    // 獲取拼音
    getStemBranchPinyin(stemBranch) {
        const pinyinMap = {
            '甲': 'Jiǎ', '乙': 'Yǐ', '丙': 'Bǐng', '丁': 'Dīng', '戊': 'Wù',
            '己': 'Jǐ', '庚': 'Gēng', '辛': 'Xīn', '壬': 'Rén', '癸': 'Guǐ',
            '子': 'Zǐ', '丑': 'Chǒu', '寅': 'Yín', '卯': 'Mǎo', '辰': 'Chén',
            '巳': 'Sì', '午': 'Wǔ', '未': 'Wèi', '申': 'Shēn', '酉': 'Yǒu',
            '戌': 'Xū', '亥': 'Hài'
        };

        return pinyinMap[stemBranch[0]] + ' ' + pinyinMap[stemBranch[1]];
    }

    // 獲取英文
    getStemBranchEnglish(stemBranch) {
        const stemMap = {
            '甲': 'Wood', '乙': 'Wood', '丙': 'Fire', '丁': 'Fire', '戊': 'Earth',
            '己': 'Earth', '庚': 'Metal', '辛': 'Metal', '壬': 'Water', '癸': 'Water'
        };

        const branchMap = {
            '子': 'Rat', '丑': 'Ox', '寅': 'Tiger', '卯': 'Rabbit', '辰': 'Dragon',
            '巳': 'Snake', '午': 'Horse', '未': 'Goat', '申': 'Monkey', '酉': 'Rooster',
            '戌': 'Dog', '亥': 'Pig'
        };

        return stemMap[stemBranch[0]] + ' ' + branchMap[stemBranch[1]];
    }

    // 清除快取
    clearCache() {
        this.cache.clear();
        return { success: true, message: '快取已清除' };
    }

    // 獲取快取狀態
    getCacheStatus() {
        return {
            success: true,
            data: {
                cacheSize: this.cache.size,
                cacheExpiry: this.cacheExpiry,
                cacheKeys: Array.from(this.cache.keys())
            }
        };
    }
}

// 全域 API 實例
const taoismAPI = new TaoismFortuneAPI();

// RESTful API 模擬器
class TaoismAPIServer {
    constructor() {
        this.api = new TaoismFortuneAPI();
        this.setupRoutes();
    }

    setupRoutes() {
        // 模擬 API 路由
        this.routes = {
            'GET /api/today': (params) => this.api.getTodayAPI(params.timezone, params.useTraditionalTime),
            'GET /api/date/:date': (params) => this.api.getDateAPI(params.date, params.timezone, params.useTraditionalTime),
            'GET /api/month/:year/:month': (params) => this.api.getMonthAPI(parseInt(params.year), parseInt(params.month), params.timezone, params.useTraditionalTime),
            'GET /api/table': () => this.api.getStemBranchTableAPI(),
            'GET /api/validation': () => this.api.getValidationAPI(),
            'DELETE /api/cache': () => this.api.clearCache(),
            'GET /api/cache/status': () => this.api.getCacheStatus()
        };
    }

    // 模擬 API 調用
    call(method, path, params = {}) {
        const route = `${method} ${path}`;
        if (this.routes[route]) {
            return this.routes[route](params);
        } else {
            return {
                success: false,
                error: `API 路由不存在: ${route}`
            };
        }
    }
}

// 全域 API 服務器實例
const taoismAPIServer = new TaoismAPIServer();