const { FlightRadar24API } = require("flightradarapi");
const axios = require("axios");
const fs = require("fs");
const path = require("path");

// ==========================================
// 核心配置与字典池
// ==========================================
const frApi = new FlightRadar24API();

const TARGET_MODELS_CONFIG = [ //包括窄体
    // 窄体
    "A19N", "B733", "B734", "B735", "B736", "73F", "73Y", "73P", "B752", "752", "75F", "AJ27", "C919","C09", "909", "919", 
    // 宽体
    "A124", "A306", "A19N", "A332", "A333", "A339", "A343", "A345", "A346", "A359", "A35K", "A388",
    "B742", "B744", "B748", "B762", "B763", "B764", "B772", "B77L", "B773", "B77W", "B788", "B789", "B78X",
    "IL62", "IL76", "IL96", "MD11",  "IL6", "IL7", "I93",
    // IATA
    "M1F", "330", "332", "333", "339", "343", "346", "359", "351", "388",
    "742", "744", "74H", "74N", "74X", "74Y", "763", "76W", "76X", "76Y", "772", "773", "77X", "77F", "77L", "77W", "788", "789", "781"
];

const WIDE_BODY_LIST = [
    "A124", "A306", "A19N", "A332", "A333", "A339", "A343", "A345", "A346", "A359", "A35K", "A388",
    "B742", "B744", "B748", "B762", "B763", "B764", "B772", "B77L", "B773", "B77W", "B788", "B789", "B78X",
    "IL62", "IL76", "IL96", "MD11", "IL6", "IL7", "I93",
    "M1F", "330", "332", "333", "339", "343", "346", "359", "351", "388",
    "742", "744", "74H", "74N", "74X", "74Y", "763", "76W", "76X", "76Y", "772", "773", "77X", "77F", "77L", "77W", "788", "789", "781"
];

const CARGO_MODEL_DIC = {
    "73F": "732F", "73Y": "733F", "73P": "B734F", "73U": "738F", "75F": "757F",
    "76X": "762F", "76Y": "763F", "77X": "772F", "B77L": "772F", "74N": "748F",
    "74X": "742F", "74Y": "744F", "ABY": "306F", "33X": "332F", "33Y": "333F",
    "IL7": "IL76", "IL62": "IL62", "IL6": "IL62", "IL96": "IL96", "I93": "IL96",
    "MD11": "MD11F", "M1F": "MD11F"
};

// ==========================================
// 辅助工具函数
// ==========================================
// 1. 延时函数：完美复刻 Python 的 time.sleep()
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomSleep = (min, max) => sleep(Math.floor(Math.random() * (max - min + 1) * 1000));

const getChinaDate = (timestampMs) => {
    const ms = timestampMs ? timestampMs : Date.now();
    return new Date(ms + (8 * 60 * 60 * 1000));
};

// 警告：传入的 dateObj 必须是 getChinaDate 算出来的！
// 并且必须统一使用 getUTC***() 系列方法，彻底绕开腾讯云操作系统的本地时区！
const formatDate = (dateObj) => {
    const y = dateObj.getUTCFullYear();
    const m = String(dateObj.getUTCMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getUTCDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
};

const formatTime = (dateObj) => {
    const m = String(dateObj.getUTCMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getUTCDate()).padStart(2, '0');
    const H = String(dateObj.getUTCHours()).padStart(2, '0');
    const M = String(dateObj.getUTCMinutes()).padStart(2, '0');
    return `${m}-${d} ${H}:${M}`;
};

const getTargetDateObj = () => {
    const targetDate = getChinaDate(); // 获取当前东八区时间
    const currentHour = targetDate.getUTCHours(); // 必须用 UTC 拿小时！

    if (currentHour > 12) {
        targetDate.setUTCDate(targetDate.getUTCDate() + 1); // 往后推一天
        console.log(`[时间判定] 当前已过中午，目标日期为明天`);
    } else {
        console.log(`[时间判定] 当前未过中午，目标日期保持今天`);
    }

    return targetDate;
};

// ==========================================
// 请求 Planespotters 拿照片
// ==========================================
async function getPlaneImage(reg) {
    if (!reg || reg === "N/A") return { imgUrl: "", creator: "" };

    const url = `https://api.planespotters.net/pub/photos/reg/${reg}`;
    try {
        // 请求前随机休眠 0.2 ~ 1 秒，防止被拉黑
        await sleep(Math.random() * 800 + 200);
        
        const response = await axios.get(url, {
            headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" },
            timeout: 5000
        });

        if (response.status === 200 && response.data.photos && response.data.photos.length > 0) {
            const photoInfo = response.data.photos[0];
            return {
                imgUrl: photoInfo.thumbnail_large.src,
                creator: photoInfo.photographer || "Unknown"
            };
        }
    } catch (error) {
        console.log(`[警告] 获取 ${reg} 图片失败: ${error.message}`);
    }
    return { imgUrl: "", creator: "" };
}

// ==========================================
// 核心流水线主控程序
// ==========================================
async function runFetchingAndFiltering(airportCode, targetDateObj, targetModelLst) {
    const targetDateStr = formatDate(targetDateObj);
    
    // 计算停止日期（第二天）
    const stopDateObj = new Date(targetDateObj);
    stopDateObj.setDate(stopDateObj.getDate() + 1);
    const stopDateStr = formatDate(stopDateObj);

    const outputFileName = `${airportCode}_${targetDateStr}_selected_arrivals.json`;
    const selectedFlights = []; // 装载最终筛选结果

    console.log(`开始抓取 ${targetDateStr} ${airportCode} 的数据...`);

    let pageNum = 1;
    let totalPages = 1;
    let shouldStop = false;

    // 🌟 开启分页大循环
    while (pageNum <= totalPages && !shouldStop) {
        console.log(`正在拉取第 ${pageNum} 页...`);
        let scheduleData;
        
        try {
            // 调用 frApi 拿数据
            const airportDetails = await frApi.getAirportDetails(airportCode, 100, pageNum);
            scheduleData = airportDetails.airport.pluginData.schedule.arrivals;
            totalPages = scheduleData.page.total;
        } catch (err) {
            console.error(`获取第 ${pageNum} 页失败:`, err.message);
            break;
        }

        const arrivalsList = scheduleData.data;

        // 🌟 遍历当前页的每一个航班（内存级过筛子）
        for (const item of arrivalsList) {
            const flight = item.flight || {};
            
            // 1. 基础信息解包
            const identification = flight.identification || {};
            const flightNum = identification.callsign || (identification.number ? identification.number.default : "N/A");
            
            const airlineName = (flight.airline && flight.airline.name) ? flight.airline.name : "Unknown Airline";
            const originCode = (flight.airport && flight.airport.origin && flight.airport.origin.code) ? flight.airport.origin.code.iata : "N/A";
            
            const aircraft = flight.aircraft || {};
            const modelCode = aircraft.model ? aircraft.model.code : "N/A";
            const modelFull = aircraft.model ? aircraft.model.text : "N/A";
            const registration = aircraft.registration || "N/A";

            // 2. 处理时间逻辑与停止信号
            const timeInfo = flight.time || {};
            const scheduled = timeInfo.scheduled || {};
            let arrivalDateStr = "";
            let arrivalFullTimeStr = "N/A";

            if (scheduled.arrival) {
                // 用秒级时间戳 * 1000 变成毫秒，传入我们的东八区转换器！
                const arrivalTimeObj = getChinaDate(scheduled.arrival * 1000);
                arrivalDateStr = formatDate(arrivalTimeObj);
                
                if (arrivalDateStr >= stopDateStr) {
                    shouldStop = true;
                    break; 
                }
                arrivalFullTimeStr = formatTime(arrivalTimeObj);
            }
            if (arrivalFullTimeStr.substring(0, 5) < targetDateStr.substring(5, 10)) {
                continue;
            }

            // 3. 处理飞行状态与预计时间
            const statusInfo = flight.status || {};
            const isAirborne = statusInfo.live || false;
            let currentStatus = "Scheduled";

            if (isAirborne) {
                currentStatus = "Enroute";
                if (timeInfo.estimated && timeInfo.estimated.arrival) {
                    // 这里也要加上 getChinaDate 转换
                    const etaTimeObj = getChinaDate(timeInfo.estimated.arrival * 1000);
                    arrivalFullTimeStr = formatTime(etaTimeObj);
                }
            }

            // ==========================================
            // 进入你的硬核筛选逻辑
            // ==========================================
            let isSelected = false;
            let flightData = {
                flightNo: flightNum,
                airline: airlineName,
                time: arrivalFullTimeStr,
                origin: originCode,
                type: modelCode,
                reg: registration,
                isSpecial: false,
                isWideBody: false,
                isCargo: false,
                isForeign: false,
                title: '',
                urlImage: "",
                imageCreator: "",
                status: currentStatus
            };

            // 过滤器 1: 彩绘机
            if (airlineName.includes("(")) {
                isSelected = true;
                flightData.isSpecial = true;
                // 提取括号里的文字作为 title
                const match = airlineName.match(/\(([^)]+)\)/);
                if (match) flightData.title = match[1].trim();
            }

            // 过滤器 2: 目标机型与宽体
            if (targetModelLst.includes(modelCode)) {
                isSelected = true;
                if (WIDE_BODY_LIST.includes(modelCode)) flightData.isWideBody = true;
                if (!flightData.title) flightData.title = `${airlineName} ${modelCode}`;
            }

            // 过滤器 3: 货机
            if ((modelFull.toLowerCase().includes("f") && modelCode != 'B739') || airlineName.toLowerCase().includes("cargo") || CARGO_MODEL_DIC[modelCode]) {
                isSelected = true;
                flightData.isCargo = true;
                if (!flightData.title) flightData.title = `${airlineName} ${modelCode}`;
                
                if (CARGO_MODEL_DIC[modelCode]) {
                    flightData.type = CARGO_MODEL_DIC[modelCode]; // 替换成更具体的货机代号
                    flightData.title = `${airlineName} ${flightData.type}`;
                }
            }

            // 过滤器 4: 注册号 (外籍/稀有)
            if (registration !== "N/A") {
                if (airportCode.startsWith("Z")) {
                    // 大陆机场：排除 B- 开头且后面跟数字的 (如 B-1234)，允许 B-LAA 这种港台号
                    if (!/^B-\d/.test(registration) || registration.length > 6) {
                        isSelected = true;
                        flightData.isForeign = true;
                        if (!flightData.title) flightData.title = `${airlineName} ${modelCode}`;
                    }
                } else if (airportCode === "VHHH" || airportCode === "VMMC") {
                    // 港澳机场：排除所有 B- 开头的 (排除大陆和港澳)，但长度大于 6 允许 (台湾号等)
                    if (!/^B-/.test(registration) || registration.length > 6) {
                        isSelected = true;
                        flightData.isForeign = true;
                        if (!flightData.title) flightData.title = `${airlineName} ${modelCode}`;
                    }
                }
            }

            // ==========================================
            // 抓取照片并放进大数组
            // ==========================================
            if (isSelected) {
                if (registration !== "N/A") {
                    console.log(`[命中] 发现目标 ${registration} (${flightData.title})，正在请求图片...`);
                    const photo = await getPlaneImage(registration);
                    flightData.urlImage = photo.imgUrl;
                    flightData.imageCreator = photo.creator;
                }
                selectedFlights.push(flightData);
            }
        } // 当前页遍历结束

        // 如果已经碰到了第二天的边界，跳出整个大循环
        if (shouldStop) {
            console.log("探测到次日航班排班，停止向后抓取。");
            break;
        }

        // 翻页逻辑与防封锁休眠
        if (pageNum < totalPages) {
            const sleepTime = Math.floor(Math.random() * 3 + 2); // 随机休眠 2~4 秒
            console.log(`第 ${pageNum} 页处理完毕。伪装休眠 ${sleepTime} 秒...`);
            await sleep(sleepTime * 1000);
        }
        pageNum++;
    }

    // ==========================================
    // 最终输出本地 JSON 文件测试
    // ==========================================
    const filePath = path.join(__dirname, outputFileName);
    fs.writeFileSync(filePath, JSON.stringify(selectedFlights, null, 2), "utf-8");
    
    console.log(`\n全部完成`);
    console.log(`共筛出 ${selectedFlights.length} 架高价值航班。`);
    console.log(`数据已保存至: ${filePath}`);
}


// 执行：抓取澳门机场，今天的数据
runFetchingAndFiltering("VMMC", getTargetDateObj(), TARGET_MODELS_CONFIG);