// 神明聖誕日查詢系統（農曆日期）
class DeityBirthdayChecker {
    constructor() {
        this.deityBirthdays = this.initDeityBirthdays();
        this.lunarCalendar = new LunarCalendar();  // 農曆轉換器
    }

    // 初始化神明聖誕日資料
    initDeityBirthdays() {
        return {
            // 正月
            '01-01': [
                { name: '彌勒佛', type: '佛', note: '天臘之辰' },
            ],
            '01-03': [
                { name: '孫真人', type: '道', note: '' },
                { name: '郝真人', type: '道', note: '' }
            ],
            '01-06': [
                { name: '走光佛', type: '佛', note: '' }
            ],
            '01-08': [
                { name: '江東神', type: '神', note: '' }
            ],
            '01-09': [
                { name: '玉皇上帝', type: '道', note: '天公生' }
            ],
            '01-13': [
                { name: '劉猛將軍', type: '神', note: '' }
            ],
            '01-15': [
                { name: '上元天官', type: '道', note: '上元節' },
                { name: '門神戶尉', type: '神', note: '' },
                { name: '佑聖真君', type: '道', note: '' },
                { name: '正一靖應真君', type: '道', note: '' },
                { name: '混元皇帝', type: '道', note: '' },
                { name: '西子帝君', type: '道', note: '' }
            ],
            '01-19': [
                { name: '長春邱真人', type: '道', note: '邱處機' }
            ],

            // 二月
            '02-01': [
                { name: '勾陳', type: '神', note: '太陽升殿之辰' },
                { name: '劉真人', type: '道', note: '' }
            ],
            '02-02': [
                { name: '土地正神', type: '神', note: '土地公' }
            ],
            '02-03': [
                { name: '文昌梓潼帝君', type: '道', note: '文昌帝君' }
            ],
            '02-04': [
                { name: '曹大將軍', type: '神', note: '' }
            ],
            '02-05': [
                { name: '東華帝君', type: '道', note: '' }
            ],
            '02-08': [
                { name: '張大帝', type: '神', note: '' },
                { name: '昌福真君', type: '道', note: '' },
                { name: '釋迦文佛', type: '佛', note: '出家日' }
            ],
            '02-13': [
                { name: '葛真君', type: '道', note: '' }
            ],
            '02-15': [
                { name: '太上老君', type: '道', note: '道祖' },
                { name: '精忠岳元帥', type: '神', note: '岳飛' }
            ],
            '02-17': [
                { name: '東方杜將軍', type: '神', note: '' }
            ],
            '02-19': [
                { name: '觀音菩薩', type: '佛', note: '觀世音菩薩' }
            ],
            '02-21': [
                { name: '普賢菩薩', type: '佛', note: '' },
                { name: '水母', type: '神', note: '' }
            ],
            '02-25': [
                { name: '玄天聖父明真帝', type: '道', note: '' }
            ],

            // 三月
            '03-03': [
                { name: '北極真武玄天上帝', type: '道', note: '玄天上帝' }
            ],
            '03-06': [
                { name: '眼光娘娘', type: '神', note: '' },
                { name: '張老相公', type: '神', note: '' }
            ],
            '03-12': [
                { name: '中央五道', type: '神', note: '' }
            ],
            '03-15': [
                { name: '昊天大帝', type: '道', note: '' },
                { name: '玄壇趙元帥', type: '道', note: '趙公明' },
                { name: '雷霆驅魔大將軍', type: '神', note: '雷萬春' },
                { name: '祖天師', type: '道', note: '張道陵' }
            ],
            '03-16': [
                { name: '准提菩薩', type: '佛', note: '' },
                { name: '山神', type: '神', note: '' }
            ],
            '03-18': [
                { name: '后土娘娘', type: '神', note: '' },
                { name: '三茅真君', type: '道', note: '得道日' },
                { name: '中嶽大帝', type: '神', note: '' },
                { name: '玉陽真人', type: '道', note: '' }
            ],
            '03-20': [
                { name: '子孫娘娘', type: '神', note: '註生娘娘' }
            ],
            '03-23': [
                { name: '天妃娘娘', type: '神', note: '媽祖' }
            ],
            '03-28': [
                { name: '東嶽大帝', type: '神', note: '' },
                { name: '蒼頡至聖先師', type: '神', note: '造字聖人' }
            ],

            // 四月
            '04-01': [
                { name: '蕭公', type: '神', note: '' }
            ],
            '04-04': [
                { name: '文殊菩薩', type: '佛', note: '' },
                { name: '狄梁公', type: '神', note: '狄仁傑' }
            ],
            '04-08': [
                { name: '釋迦文佛', type: '佛', note: '佛誕日' }
            ],
            '04-13': [
                { name: '天尹真人', type: '道', note: '' },
                { name: '葛孝先真人', type: '道', note: '' }
            ],
            '04-14': [
                { name: '呂純陽祖師', type: '道', note: '呂洞賓' }
            ],
            '04-15': [
                { name: '鐘離祖師', type: '道', note: '鐘離權' },
                { name: '釋迦如來', type: '佛', note: '成佛日' }
            ],
            '04-18': [
                { name: '紫微大帝', type: '道', note: '' },
                { name: '泰山頂上娘娘', type: '神', note: '碧霞元君' }
            ],
            '04-20': [
                { name: '眼光聖母娘娘', type: '神', note: '' }
            ],
            '04-26': [
                { name: '鐘山蔣公', type: '神', note: '' }
            ],
            '04-28': [
                { name: '藥王', type: '神', note: '藥王菩薩' }
            ],

            // 五月
            '05-01': [
                { name: '南極長生大帝', type: '道', note: '' }
            ],
            '05-05': [
                { name: '地祗溫元帥', type: '神', note: '地臘之辰' },
                { name: '雷霆鄧天君', type: '神', note: '' }
            ],
            '05-07': [
                { name: '朱太尉', type: '神', note: '' }
            ],
            '05-08': [
                { name: '南方五道', type: '神', note: '' }
            ],
            '05-11': [
                { name: '都城隍', type: '神', note: '' }
            ],
            '05-12': [
                { name: '炳靈公', type: '神', note: '' }
            ],
            '05-13': [
                { name: '關聖帝君', type: '神', note: '關公降神' }
            ],
            '05-18': [
                { name: '張天師', type: '道', note: '' }
            ],
            '05-20': [
                { name: '丹陽馬真人', type: '道', note: '' }
            ],
            '05-29': [
                { name: '許威顯王', type: '神', note: '許遠' }
            ],

            // 六月
            '06-06': [
                { name: '崔府君', type: '神', note: '' },
                { name: '楊四將軍', type: '神', note: '' }
            ],
            '06-10': [
                { name: '劉海蟾帝君', type: '道', note: '' }
            ],
            '06-11': [
                { name: '井泉龍王', type: '神', note: '' }
            ],
            '06-19': [
                { name: '觀音菩薩', type: '佛', note: '成道日' }
            ],
            '06-23': [
                { name: '火神', type: '神', note: '' },
                { name: '關聖帝君', type: '神', note: '關公聖誕' },
                { name: '王靈官', type: '道', note: '' },
                { name: '馬神', type: '神', note: '' }
            ],
            '06-24': [
                { name: '雷祖', type: '道', note: '' }
            ],
            '06-26': [
                { name: '二郎真君', type: '道', note: '二郎神' }
            ],
            '06-29': [
                { name: '天樞左相莫君', type: '神', note: '文天祥' }
            ],

            // 七月
            '07-12': [
                { name: '長真譚真人', type: '道', note: '' }
            ],
            '07-13': [
                { name: '大勢至菩薩', type: '佛', note: '' }
            ],
            '07-15': [
                { name: '中元地官', type: '道', note: '中元節' },
                { name: '靈濟真君', type: '道', note: '' }
            ],
            '07-18': [
                { name: '王母娘娘', type: '道', note: '西王母' }
            ],
            '07-19': [
                { name: '值年太歲', type: '神', note: '' }
            ],
            '07-21': [
                { name: '普庵祖師', type: '佛', note: '' },
                { name: '上元道化其君', type: '道', note: '許真君' }
            ],
            '07-22': [
                { name: '增福財神', type: '神', note: '' }
            ],
            '07-23': [
                { name: '天樞上相真君', type: '神', note: '諸葛亮' }
            ],
            '07-24': [
                { name: '龍樹王菩薩', type: '佛', note: '' }
            ],
            '07-30': [
                { name: '地藏王菩薩', type: '佛', note: '' }
            ],

            // 八月
            '08-01': [
                { name: '神功妙濟真君', type: '道', note: '許真君' }
            ],
            '08-03': [
                { name: '灶君', type: '神', note: '灶王爺' }
            ],
            '08-05': [
                { name: '雷聲大帝', type: '道', note: '' }
            ],
            '08-10': [
                { name: '北嶽大帝', type: '神', note: '' }
            ],
            '08-12': [
                { name: '西方五道', type: '神', note: '' }
            ],
            '08-18': [
                { name: '酒仙', type: '神', note: '' }
            ],
            '08-22': [
                { name: '燃燈佛', type: '佛', note: '' }
            ],
            '08-23': [
                { name: '伏魔副將張顯王', type: '神', note: '張飛' }
            ],

            // 九月
            '09-03': [
                { name: '五瘟', type: '神', note: '五瘟神' }
            ],
            '09-09': [
                { name: '斗母元君', type: '道', note: '' },
                { name: '玄天上帝', type: '道', note: '飛升日' },
                { name: '重陽帝君', type: '道', note: '' },
                { name: '酆都大帝', type: '神', note: '' },
                { name: '蒿裏', type: '神', note: '' },
                { name: '梅葛二仙翁', type: '道', note: '' }
            ],
            '09-16': [
                { name: '機神', type: '神', note: '' }
            ],
            '09-17': [
                { name: '金龍四大王', type: '神', note: '' },
                { name: '洪恩真君', type: '道', note: '' }
            ],
            '09-23': [
                { name: '薩真人', type: '道', note: '' }
            ],
            '09-28': [
                { name: '五顯靈宮', type: '神', note: '' },
                { name: '馬元帥', type: '神', note: '' }
            ],
            '09-30': [
                { name: '藥師琉璃光王佛', type: '佛', note: '' }
            ],

            // 十月
            '10-01': [
                { name: '東皇大帝', type: '道', note: '民歲臘之辰' },
                { name: '下元定志周真君', type: '道', note: '' }
            ],
            '10-03': [
                { name: '三茅應化真君', type: '道', note: '' }
            ],
            '10-05': [
                { name: '達摩祖師', type: '佛', note: '' }
            ],
            '10-06': [
                { name: '天曹諸司五嶽五帝', type: '神', note: '' }
            ],
            '10-15': [
                { name: '下元水官', type: '道', note: '下元節' },
                { name: '痘神劉使者', type: '神', note: '' }
            ],
            '10-20': [
                { name: '虛靖天師', type: '道', note: '張弘悟' }
            ],
            '10-27': [
                { name: '北極紫微大帝', type: '道', note: '' }
            ],

            // 十一月
            '11-04': [
                { name: '大成至聖先師文宣王', type: '神', note: '孔子' }
            ],
            '11-06': [
                { name: '西嶽大帝', type: '神', note: '' }
            ],
            '11-11': [
                { name: '太乙救苦天尊', type: '道', note: '' }
            ],
            '11-17': [
                { name: '阿彌陀佛', type: '佛', note: '' }
            ],
            '11-19': [
                { name: '日光天子', type: '神', note: '' },
                { name: '大慈至聖九蓮菩薩', type: '佛', note: '' }
            ],
            '11-23': [
                { name: '張仙', type: '神', note: '南斗下降' }
            ],
            '11-26': [
                { name: '北方五道', type: '神', note: '' }
            ],

            // 十二月
            '12-08': [
                { name: '張英濟王', type: '神', note: '張巡，王侯臘之辰' },
                { name: '釋達如來', type: '佛', note: '成佛日' }
            ],
            '12-16': [
                { name: '南嶽大帝', type: '神', note: '' }
            ],
            '12-20': [
                { name: '魯班', type: '神', note: '工匠祖師' }
            ],
            '12-21': [
                { name: '天猷上帝', type: '道', note: '' }
            ],
            '12-24': [
                { name: '司命灶君', type: '神', note: '上天朝玉帝' }
            ],
            '12-29': [
                { name: '華嚴菩薩', type: '佛', note: '' }
            ]
        };
    }

    // 獲取指定日期的神明聖誕（使用農曆）
    getDeityBirthdays(date) {
        // 將陽曆轉換為農曆
        const lunar = this.lunarCalendar.solarToLunar(
            date.getFullYear(), 
            date.getMonth() + 1, 
            date.getDate()
        );
        
        const month = String(lunar.month).padStart(2, '0');
        const day = String(lunar.day).padStart(2, '0');
        const key = `${month}-${day}`;
        
        return this.deityBirthdays[key] || [];
    }
    
    // 獲取農曆日期字符串
    getLunarDateString(date) {
        const lunar = this.lunarCalendar.solarToLunar(
            date.getFullYear(), 
            date.getMonth() + 1, 
            date.getDate()
        );
        return this.lunarCalendar.formatLunarDate(lunar);
    }

    // 獲取近期神明聖誕（未來N天內）
    getUpcomingBirthdays(days = 7) {
        const today = new Date();
        const upcoming = [];
        
        for (let i = 0; i <= days; i++) {
            const checkDate = new Date(today);
            checkDate.setDate(today.getDate() + i);
            
            const deities = this.getDeityBirthdays(checkDate);
            if (deities.length > 0) {
                const month = checkDate.getMonth() + 1;
                const day = checkDate.getDate();
                const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
                const weekday = weekdays[checkDate.getDay()];
                
                upcoming.push({
                    date: checkDate,
                    dateString: `${month}月${day}日 (週${weekday})`,
                    daysFromNow: i,
                    deities: deities,
                    isToday: i === 0,
                    isTomorrow: i === 1
                });
            }
        }
        
        return upcoming;
    }

    // 獲取本月所有神明聖誕（陽曆月份，但查找農曆日期）
    getMonthlyBirthdays(year, month) {
        const daysInMonth = new Date(year, month, 0).getDate();
        const monthlyBirthdays = [];
        
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month - 1, day);
            const deities = this.getDeityBirthdays(date);  // 使用農曆轉換
            
            if (deities && deities.length > 0) {
                const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
                const weekday = weekdays[date.getDay()];
                const lunarStr = this.getLunarDateString(date);
                
                monthlyBirthdays.push({
                    date: date,
                    day: day,
                    weekday: weekday,
                    lunarDate: lunarStr,
                    deities: deities
                });
            }
        }
        
        return monthlyBirthdays;
    }

    // 搜尋神明聖誕日
    searchDeity(searchTerm) {
        const results = [];
        
        Object.entries(this.deityBirthdays).forEach(([dateKey, deities]) => {
            deities.forEach(deity => {
                if (deity.name.includes(searchTerm) || deity.note.includes(searchTerm)) {
                    const [month, day] = dateKey.split('-');
                    results.push({
                        month: parseInt(month),
                        day: parseInt(day),
                        dateString: `農曆${parseInt(month)}月${parseInt(day)}日`,
                        deity: deity
                    });
                }
            });
        });
        
        return results.sort((a, b) => {
            if (a.month !== b.month) return a.month - b.month;
            return a.day - b.day;
        });
    }

    // 獲取神明類型的圖示
    getDeityTypeIcon(type) {
        switch (type) {
            case '佛': return '🙏';
            case '道': return '☯️';
            case '神': return '🏮';
            default: return '✨';
        }
    }

    // 獲取神明類型的顏色
    getDeityTypeColor(type) {
        switch (type) {
            case '佛': return '#f39c12';  // 橙色
            case '道': return '#3498db';  // 藍色
            case '神': return '#e74c3c';  // 紅色
            default: return '#95a5a6';   // 灰色
        }
    }

    // 格式化神明資訊
    formatDeityInfo(deity) {
        const icon = this.getDeityTypeIcon(deity.type);
        const note = deity.note ? ` (${deity.note})` : '';
        return `${icon} ${deity.name}${note}`;
    }

    // 獲取今日神明聖誕
    getTodayDeities() {
        const today = new Date();
        const deities = this.getDeityBirthdays(today);
        
        if (deities.length === 0) {
            return null;
        }
        
        const month = today.getMonth() + 1;
        const day = today.getDate();
        const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
        const weekday = weekdays[today.getDay()];
        
        return {
            dateString: `${month}月${day}日 (週${weekday})`,
            deities: deities,
            count: deities.length
        };
    }
}

// 初始化神明聖誕日系統
const deityChecker = new DeityBirthdayChecker();

// 更新神明聖誕日顯示
function updateDeityDisplay() {
    // 更新今日神明聖誕
    const todayDeitiesElement = document.getElementById('today-deities');
    if (todayDeitiesElement) {
        const todayDeities = deityChecker.getTodayDeities();
        
        if (todayDeities) {
            const deitiesList = todayDeities.deities
                .map(deity => deityChecker.formatDeityInfo(deity))
                .join('<br>');
            
            todayDeitiesElement.innerHTML = `
                <h4>🎂 今日神明聖誕 (${todayDeities.count}位)</h4>
                <div class="deity-list">${deitiesList}</div>
            `;
            todayDeitiesElement.style.display = 'block';
        } else {
            todayDeitiesElement.innerHTML = '<p>今日無神明聖誕</p>';
            todayDeitiesElement.style.display = 'none';
        }
    }
    
    // 更新近期神明聖誕
    const upcomingDeitiesElement = document.getElementById('upcoming-deities');
    if (upcomingDeitiesElement) {
        const upcoming = deityChecker.getUpcomingBirthdays(7);
        
        if (upcoming.length > 0) {
            let upcomingHtml = '<h4>📅 近期神明聖誕 (7天內)</h4>';
            
            upcoming.forEach(item => {
                const deitiesList = item.deities
                    .map(deity => deityChecker.formatDeityInfo(deity))
                    .join(', ');
                
                const dayLabel = item.isToday ? '今天' : 
                                item.isTomorrow ? '明天' : 
                                `${item.daysFromNow}天後`;
                
                upcomingHtml += `
                    <div class="upcoming-item">
                        <strong>${item.dateString} (${dayLabel})</strong><br>
                        <span class="deity-list">${deitiesList}</span>
                    </div>
                `;
            });
            
            upcomingDeitiesElement.innerHTML = upcomingHtml;
        } else {
            upcomingDeitiesElement.innerHTML = '<p>近期無神明聖誕</p>';
        }
    }
}

// 搜尋神明功能
function searchDeityBirthday() {
    const searchInput = document.getElementById('deity-search');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput || !searchResults) return;
    
    const searchTerm = searchInput.value.trim();
    
    if (searchTerm.length === 0) {
        searchResults.innerHTML = '';
        return;
    }
    
    const results = deityChecker.searchDeity(searchTerm);
    
    if (results.length === 0) {
        searchResults.innerHTML = '<p>找不到相關神明</p>';
        return;
    }
    
    let resultsHtml = `<h4>🔍 搜尋結果 (${results.length}筆)</h4>`;
    
    results.forEach(result => {
        resultsHtml += `
            <div class="search-result-item">
                <strong>${result.dateString}</strong> - ${deityChecker.formatDeityInfo(result.deity)}
            </div>
        `;
    });
    
    searchResults.innerHTML = resultsHtml;
}

// 顯示本月神明聖誕
function showMonthlyDeities() {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth() + 1;
    
    const monthlyElement = document.getElementById('monthly-deities');
    if (!monthlyElement) return;
    
    const monthlyBirthdays = deityChecker.getMonthlyBirthdays(year, month);
    
    if (monthlyBirthdays.length === 0) {
        monthlyElement.innerHTML = `<p>${month}月無神明聖誕</p>`;
        return;
    }
    
    let monthlyHtml = `<h4>📆 ${year}年${month}月神明聖誕 (${monthlyBirthdays.length}天)</h4>`;
    
    monthlyBirthdays.forEach(item => {
        const deitiesList = item.deities
            .map(deity => deityChecker.formatDeityInfo(deity))
            .join('<br>');
        
        monthlyHtml += `
            <div class="monthly-item">
                <strong>${month}月${item.day}日 (週${item.weekday})</strong><br>
                <div class="deity-list">${deitiesList}</div>
            </div>
        `;
    });
    
    monthlyElement.innerHTML = monthlyHtml;
}

// 頁面載入完成後執行
document.addEventListener('DOMContentLoaded', function() {
    updateDeityDisplay();
    showMonthlyDeities();
    
    // 綁定搜尋功能
    const searchInput = document.getElementById('deity-search');
    if (searchInput) {
        searchInput.addEventListener('input', searchDeityBirthday);
    }
});