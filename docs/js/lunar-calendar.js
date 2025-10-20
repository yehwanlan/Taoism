// 農曆轉換模組 - 基於天文計算的陰陽合曆
class LunarCalendar {
    constructor() {
        // 常量定義
        this.SOLAR_TERMS = [
            0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165,
            180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345
        ];
        this.MONTH_DAYS_AVG = 29.530588853;  // 平均朔望月長度
        this.LUNAR_YEAR_DAYS_AVG = 365.2422;  // 回歸年
        this.NEW_MOON_OFFSET_2000 = 2451550.09765;  // 2000-01-06 的新月 JD
        
        // 農曆數據表（1900-2100）- 簡化版本
        this.lunarInfo = this.initLunarInfo();
    }

    // 初始化農曆數據表（編碼格式：每年用一個數字表示）
    initLunarInfo() {
        // 數據格式：0xABCDE
        // A: 閏月月份（0=無閏月）
        // BCDE: 12/13個月的大小月（1=大月30天，0=小月29天）
        return {
            2020: 0x04bd8, 2021: 0x04ae0, 2022: 0x0a570, 2023: 0x054d5, 2024: 0x0d260,
            2025: 0x0d950, 2026: 0x16554, 2027: 0x056a0, 2028: 0x09ad0, 2029: 0x055d2,
            2030: 0x04ae0, 2031: 0x0a5b6, 2032: 0x0a4d0, 2033: 0x0d250, 2034: 0x1d255,
            2035: 0x0b540, 2036: 0x0d6a0, 2037: 0x0ada2, 2038: 0x095b0, 2039: 0x14977,
            2040: 0x04970, 2041: 0x0a4b0, 2042: 0x0b4b5, 2043: 0x06a50, 2044: 0x06d40,
            2045: 0x1ab54, 2046: 0x02b60, 2047: 0x09570, 2048: 0x052f2, 2049: 0x04970,
            2050: 0x06566
        };
    }

    // 陽曆轉 Julian Day
    gregorianToJD(year, month, day) {
        if (month <= 2) {
            year -= 1;
            month += 12;
        }
        const a = Math.floor(year / 100);
        const b = 2 - a + Math.floor(a / 4);
        const jd = Math.floor(365.25 * (year + 4716)) + 
                   Math.floor(30.6001 * (month + 1)) + day + b - 1524.5;
        return jd;
    }

    // 陽曆轉農曆（主要功能）
    solarToLunar(year, month, day) {
        // 使用查表法（更準確且快速）
        const baseDate = new Date(1900, 0, 31);  // 1900年1月31日 = 農曆1900年正月初一
        const targetDate = new Date(year, month - 1, day);
        
        let offset = Math.floor((targetDate - baseDate) / 86400000);
        
        let lunarYear = 1900;
        let daysInYear = 0;
        
        // 計算農曆年份
        while (lunarYear < 2101 && offset > 0) {
            daysInYear = this.getLunarYearDays(lunarYear);
            if (offset < daysInYear) break;
            offset -= daysInYear;
            lunarYear++;
        }
        
        // 計算農曆月份
        const leapMonth = this.getLeapMonth(lunarYear);
        let isLeap = false;
        let lunarMonth = 1;
        
        for (let m = 1; m <= 13; m++) {
            const isLeapMonth = (leapMonth > 0 && m === leapMonth + 1);
            const daysInMonth = this.getLunarMonthDays(lunarYear, isLeapMonth ? leapMonth : m, isLeapMonth);
            
            if (offset < daysInMonth) {
                if (isLeapMonth) {
                    isLeap = true;
                    lunarMonth = leapMonth;
                } else {
                    lunarMonth = m > leapMonth && leapMonth > 0 ? m - 1 : m;
                }
                break;
            }
            offset -= daysInMonth;
        }
        
        const lunarDay = offset + 1;
        
        return {
            year: lunarYear,
            month: lunarMonth,
            day: lunarDay,
            isLeap: isLeap
        };
    }

    // 農曆轉陽曆
    lunarToSolar(lunarYear, lunarMonth, lunarDay, isLeap = false) {
        const baseDate = new Date(1900, 0, 31);
        let offset = 0;
        
        // 累加年份的天數
        for (let y = 1900; y < lunarYear; y++) {
            offset += this.getLunarYearDays(y);
        }
        
        // 累加月份的天數
        const leapMonth = this.getLeapMonth(lunarYear);
        for (let m = 1; m < lunarMonth; m++) {
            offset += this.getLunarMonthDays(lunarYear, m, false);
        }
        
        // 如果是閏月
        if (isLeap && leapMonth === lunarMonth) {
            offset += this.getLunarMonthDays(lunarYear, lunarMonth, false);
        }
        
        // 加上日期
        offset += lunarDay - 1;
        
        const result = new Date(baseDate.getTime() + offset * 86400000);
        return {
            year: result.getFullYear(),
            month: result.getMonth() + 1,
            day: result.getDate()
        };
    }

    // 獲取農曆年份的總天數
    getLunarYearDays(year) {
        if (!this.lunarInfo[year]) {
            // 如果沒有數據，使用近似值
            return 354;
        }
        
        let sum = 348;  // 12個小月的天數
        for (let i = 0x8000; i > 0x8; i >>= 1) {
            sum += (this.lunarInfo[year] & i) ? 1 : 0;
        }
        
        // 加上閏月天數
        const leapDays = this.getLeapMonthDays(year);
        return sum + leapDays;
    }

    // 獲取農曆月份的天數
    getLunarMonthDays(year, month, isLeap = false) {
        if (!this.lunarInfo[year]) {
            return 29;  // 默認小月
        }
        
        if (isLeap) {
            return this.getLeapMonthDays(year);
        }
        
        return (this.lunarInfo[year] & (0x10000 >> month)) ? 30 : 29;
    }

    // 獲取閏月月份（0表示無閏月）
    getLeapMonth(year) {
        if (!this.lunarInfo[year]) {
            return 0;
        }
        return this.lunarInfo[year] & 0xf;
    }

    // 獲取閏月天數
    getLeapMonthDays(year) {
        const leapMonth = this.getLeapMonth(year);
        if (leapMonth === 0) return 0;
        
        return (this.lunarInfo[year] & 0x10000) ? 30 : 29;
    }

    // 格式化農曆日期
    formatLunarDate(lunar) {
        const monthNames = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '臘'];
        const dayNames = [
            '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
            '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
            '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十'
        ];
        
        const monthStr = (lunar.isLeap ? '閏' : '') + monthNames[lunar.month - 1] + '月';
        const dayStr = dayNames[lunar.day - 1];
        
        return `${monthStr}${dayStr}`;
    }

    // 獲取農曆月日字符串（用於匹配神明聖誕）
    getLunarMonthDay(date) {
        const lunar = this.solarToLunar(date.getFullYear(), date.getMonth() + 1, date.getDate());
        const month = String(lunar.month).padStart(2, '0');
        const day = String(lunar.day).padStart(2, '0');
        return `${month}-${day}`;
    }

    // 檢查是否為農曆特定日期
    isLunarDate(date, lunarMonth, lunarDay) {
        const lunar = this.solarToLunar(date.getFullYear(), date.getMonth() + 1, date.getDate());
        return lunar.month === lunarMonth && lunar.day === lunarDay;
    }

    // 獲取指定年份的農曆節日對應的陽曆日期
    getLunarFestivalDate(year, lunarMonth, lunarDay) {
        try {
            return this.lunarToSolar(year, lunarMonth, lunarDay, false);
        } catch (e) {
            // 如果轉換失敗，返回 null
            return null;
        }
    }

    // 獲取農曆年份的生肖
    getZodiac(lunarYear) {
        const zodiacs = ['鼠', '牛', '虎', '兔', '龍', '蛇', '馬', '羊', '猴', '雞', '狗', '豬'];
        return zodiacs[(lunarYear - 1900) % 12];
    }

    // 獲取天干地支年
    getGanZhiYear(lunarYear) {
        const gan = ['庚', '辛', '壬', '癸', '甲', '乙', '丙', '丁', '戊', '己'];
        const zhi = ['申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未'];
        return gan[lunarYear % 10] + zhi[lunarYear % 12];
    }
}

// 導出供其他模組使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LunarCalendar;
}
