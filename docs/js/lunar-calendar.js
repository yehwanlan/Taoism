// 農曆轉換模組 - 基於完整數據表的陰陽合曆
class LunarCalendar {
    constructor() {
        // 農曆數據表（1900-2100）- 完整版本
        this.lunarInfo = this.initLunarInfo();
    }

    // 初始化農曆數據表（編碼格式：每年用一個數字表示）
    initLunarInfo() {
        // 數據格式：0xABCDE
        // 高4位（A）: 閏月月份（0=無閏月，1-12=閏幾月）
        // 低16位（BCDE）: 12/13個月的大小月（1=大月30天，0=小月29天）
        // 最高位：閏月是大月還是小月
        return [
            0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2, // 1900-1909
            0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977, // 1910-1919
            0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970, // 1920-1929
            0x06566, 0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950, // 1930-1939
            0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557, // 1940-1949
            0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0, // 1950-1959
            0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0, // 1960-1969
            0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6, // 1970-1979
            0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570, // 1980-1989
            0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x055c0, 0x0ab60, 0x096d5, 0x092e0, // 1990-1999
            0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5, // 2000-2009
            0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930, // 2010-2019
            0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530, // 2020-2029
            0x05aa0, 0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45, // 2030-2039
            0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0, // 2040-2049
            0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6, 0x0ea50, 0x06b20, 0x1a6c4, 0x0aae0, // 2050-2059
            0x0a2e0, 0x0d2e3, 0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0, 0x0a6d0, 0x055d4, // 2060-2069
            0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0, 0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0, // 2070-2079
            0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55, 0x04b60, 0x0a570, 0x054e4, 0x0d160, // 2080-2089
            0x0e968, 0x0d520, 0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a2d0, 0x0d150, 0x0f252, // 2090-2099
            0x0d520  // 2100
        ];
    }

    // 陽曆轉農曆（主要功能）
    solarToLunar(year, month, day) {
        // 使用查表法（更準確且快速）
        const baseDate = new Date(1900, 0, 31);  // 1900年1月31日 = 農曆1900年正月初一
        const targetDate = new Date(year, month - 1, day);
        
        // 計算天數差
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
        
        // 計算農曆月份和日期
        const leapMonth = this.getLeapMonth(lunarYear);
        let isLeap = false;
        let lunarMonth = 1;
        
        // 遍歷每個月
        for (let m = 1; m <= 13; m++) {
            let daysInMonth;
            
            // 如果有閏月且當前是閏月
            if (leapMonth > 0 && m === (leapMonth + 1)) {
                daysInMonth = this.getLeapMonthDays(lunarYear);
                if (offset < daysInMonth) {
                    isLeap = true;
                    lunarMonth = leapMonth;
                    break;
                }
            } else {
                // 普通月份
                const actualMonth = (leapMonth > 0 && m > leapMonth) ? m - 1 : m;
                daysInMonth = this.getLunarMonthDays(lunarYear, actualMonth);
                if (offset < daysInMonth) {
                    lunarMonth = actualMonth;
                    break;
                }
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
        const yearIndex = year - 1900;
        if (yearIndex < 0 || yearIndex >= this.lunarInfo.length) {
            return 354;  // 默認值
        }
        
        let sum = 348;  // 12個小月的基礎天數（29*12）
        
        // 計算12個月的大小月
        for (let i = 0x8000; i > 0x8; i >>= 1) {
            sum += (this.lunarInfo[yearIndex] & i) ? 1 : 0;
        }
        
        // 加上閏月天數
        sum += this.getLeapMonthDays(year);
        
        return sum;
    }

    // 獲取農曆月份的天數
    getLunarMonthDays(year, month) {
        const yearIndex = year - 1900;
        if (yearIndex < 0 || yearIndex >= this.lunarInfo.length) {
            return 29;  // 默認小月
        }
        
        // 檢查該月是大月還是小月
        return (this.lunarInfo[yearIndex] & (0x10000 >> month)) ? 30 : 29;
    }

    // 獲取閏月月份（0表示無閏月）
    getLeapMonth(year) {
        const yearIndex = year - 1900;
        if (yearIndex < 0 || yearIndex >= this.lunarInfo.length) {
            return 0;
        }
        return this.lunarInfo[yearIndex] & 0xf;
    }

    // 獲取閏月天數
    getLeapMonthDays(year) {
        const leapMonth = this.getLeapMonth(year);
        if (leapMonth === 0) return 0;
        
        const yearIndex = year - 1900;
        // 最高位表示閏月是大月還是小月
        return (this.lunarInfo[yearIndex] & 0x10000) ? 30 : 29;
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
