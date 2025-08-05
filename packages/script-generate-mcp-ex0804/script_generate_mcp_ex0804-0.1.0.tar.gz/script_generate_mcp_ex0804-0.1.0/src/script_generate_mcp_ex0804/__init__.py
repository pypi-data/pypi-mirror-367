from mcp.server.fastmcp import FastMCP
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 创建MCP服务器
mcp = FastMCP("PhoneManufacturerPartnerAnalysis")

# 数据存储 - 包含虚假示例数据
partners: Dict[str, Dict] = {}  # 合作伙伴信息
cooperation_records: Dict[str, List[Dict]] = {}  # 合作记录，key为合作伙伴ID

# 初始化虚假数据
def initialize_demo_data():
    """初始化虚假的手机厂商合作伙伴数据"""
    # 芯片供应商
    qualcomm_id = str(uuid.uuid4())
    partners[qualcomm_id] = {
        "id": qualcomm_id,
        "name": "高通（Qualcomm）",
        "industry": "半导体",
        "contact_person": "张明",
        "contact_info": "zhangming@qualcomm.com",
        "tier": "strategic",
        "notes": "全球领先的无线通信芯片供应商",
        "added_at": (datetime.now() - timedelta(days=1500)).isoformat(),
        "last_updated": (datetime.now() - timedelta(days=30)).isoformat(),
        "status": "active",
        "country": "美国",
        "employees": 51000,
        "revenue_billion": 44.2,
        "market_share": "35%",
        "rating": 4.8
    }
    cooperation_records[qualcomm_id] = [
        {
            "record_id": str(uuid.uuid4()),
            "partner_id": qualcomm_id,
            "project_name": "骁龙8 Gen3处理器供应",
            "start_date": "2023-08-15",
            "end_date": "2024-12-31",
            "value": 850000000.0,
            "outcome": "已完成70%的供货量，性能达标",
            "notes": "为旗舰机型提供芯片",
            "recorded_at": (datetime.now() - timedelta(days=200)).isoformat(),
            "quantity": 2500000,
            "delivery_rate": 98.5,
            "quality_rate": 99.9,
            "payment_terms": "月结30天",
            "renewal_potential": "高"
        },
        {
            "record_id": str(uuid.uuid4()),
            "partner_id": qualcomm_id,
            "project_name": "5G调制解调器合作开发",
            "start_date": "2022-05-20",
            "end_date": "2023-11-30",
            "value": 320000000.0,
            "outcome": "成功开发并量产新型5G调制解调器",
            "notes": "提升了5G信号接收能力",
            "recorded_at": (datetime.now() - timedelta(days=500)).isoformat(),
            "quantity": None,
            "delivery_rate": 100.0,
            "quality_rate": 99.7,
            "payment_terms": "阶段付款",
            "renewal_potential": "已续约"
        }
    ]
    
    # 屏幕供应商
    samsung_id = str(uuid.uuid4())
    partners[samsung_id] = {
        "id": samsung_id,
        "name": "三星显示（Samsung Display）",
        "industry": "显示面板",
        "contact_person": "李华",
        "contact_info": "lihua@samsungdisplay.com",
        "tier": "strategic",
        "notes": "提供AMOLED屏幕",
        "added_at": (datetime.now() - timedelta(days=1800)).isoformat(),
        "last_updated": (datetime.now() - timedelta(days=45)).isoformat(),
        "status": "active",
        "country": "韩国",
        "employees": 32000,
        "revenue_billion": 38.7,
        "market_share": "42%",
        "rating": 4.7
    }
    cooperation_records[samsung_id] = [
        {
            "record_id": str(uuid.uuid4()),
            "partner_id": samsung_id,
            "project_name": "6.7英寸2K AMOLED屏幕供应",
            "start_date": "2023-06-01",
            "end_date": "2024-06-01",
            "value": 620000000.0,
            "outcome": "按计划供货中，质量稳定",
            "notes": "用于高端机型",
            "recorded_at": (datetime.now() - timedelta(days=250)).isoformat(),
            "quantity": 3000000,
            "delivery_rate": 97.2,
            "quality_rate": 99.6,
            "payment_terms": "月结45天",
            "renewal_potential": "高"
        }
    ]
    
    # 摄像头模组供应商
    sony_id = str(uuid.uuid4())
    partners[sony_id] = {
        "id": sony_id,
        "name": "索尼半导体（Sony Semiconductor）",
        "industry": "图像传感器",
        "contact_person": "王强",
        "contact_info": "wangqiang@sony-semicon.com",
        "tier": "key",
        "notes": "提供高端摄像头传感器",
        "added_at": (datetime.now() - timedelta(days=1600)).isoformat(),
        "last_updated": (datetime.now() - timedelta(days=60)).isoformat(),
        "status": "active",
        "country": "日本",
        "employees": 28000,
        "revenue_billion": 29.5,
        "market_share": "40%",
        "rating": 4.9
    }
    cooperation_records[sony_id] = [
        {
            "record_id": str(uuid.uuid4()),
            "partner_id": sony_id,
            "project_name": "5000万像素主摄传感器供应",
            "start_date": "2023-03-10",
            "end_date": "2024-03-10",
            "value": 480000000.0,
            "outcome": "供货完成85%，客户反馈良好",
            "notes": "用于多款主力机型",
            "recorded_at": (datetime.now() - timedelta(days=300)).isoformat(),
            "quantity": 4500000,
            "delivery_rate": 96.8,
            "quality_rate": 99.8,
            "payment_terms": "月结30天",
            "renewal_potential": "高"
        }
    ]
    
    # 电池供应商
    catl_id = str(uuid.uuid4())
    partners[catl_id] = {
        "id": catl_id,
        "name": "宁德时代（CATL）",
        "industry": "电池制造",
        "contact_person": "陈静",
        "contact_info": "chenjing@catl.com",
        "tier": "key",
        "notes": "提供高容量锂电池",
        "added_at": (datetime.now() - timedelta(days=1200)).isoformat(),
        "last_updated": (datetime.now() - timedelta(days=20)).isoformat(),
        "status": "active",
        "country": "中国",
        "employees": 120000,
        "revenue_billion": 110.3,
        "market_share": "37%",
        "rating": 4.6
    }
    cooperation_records[catl_id] = [
        {
            "record_id": str(uuid.uuid4()),
            "partner_id": catl_id,
            "project_name": "4500mAh高密度电池供应",
            "start_date": "2023-09-01",
            "end_date": "2025-03-01",
            "value": 750000000.0,
            "outcome": "初期供货阶段，性能符合预期",
            "notes": "用于中高端全系列机型",
            "recorded_at": (datetime.now() - timedelta(days=180)).isoformat(),
            "quantity": 6000000,
            "delivery_rate": 99.1,
            "quality_rate": 99.5,
            "payment_terms": "月结60天",
            "renewal_potential": "高"
        }
    ]
    
    # 操作系统供应商
    google_id = str(uuid.uuid4())
    partners[google_id] = {
        "id": google_id,
        "name": "谷歌（Google）",
        "industry": "软件与服务",
        "contact_person": "刘强",
        "contact_info": "liuqiang@google.com",
        "tier": "strategic",
        "notes": "提供Android操作系统授权",
        "added_at": (datetime.now() - timedelta(days=2000)).isoformat(),
        "last_updated": (datetime.now() - timedelta(days=10)).isoformat(),
        "status": "active",
        "country": "美国",
        "employees": 156000,
        "revenue_billion": 307.4,
        "market_share": "71% (移动操作系统)",
        "rating": 4.5
    }
    cooperation_records[google_id] = [
        {
            "record_id": str(uuid.uuid4()),
            "partner_id": google_id,
            "project_name": "Android 14操作系统授权",
            "start_date": "2023-07-01",
            "end_date": "2024-12-31",
            "value": 120000000.0,
            "outcome": "授权已完成，正在机型上适配",
            "notes": "包含Google移动服务",
            "recorded_at": (datetime.now() - timedelta(days=220)).isoformat(),
            "quantity": None,
            "delivery_rate": 100.0,
            "quality_rate": 100.0,
            "payment_terms": "按设备激活数量付费",
            "renewal_potential": "已规划"
        }
    ]

# 初始化虚假数据
initialize_demo_data()

# 工具：添加新合作伙伴
@mcp.tool()
def add_partner(name: str, industry: str, contact_person: str, 
               contact_info: str, tier: str = "general",
               notes: str = "", country: str = "",
               employees: int = 0, revenue_billion: float = 0.0,
               market_share: str = "", rating: float = 0.0) -> Dict:
    """
    添加手机厂商的新合作伙伴信息
    
    参数:
        name: 合作伙伴公司名称
        industry: 所属行业
        contact_person: 联系人姓名
        contact_info: 联系信息
        tier: 合作级别（strategic-战略级, key-关键, general-普通）
        notes: 其他备注信息
        country: 所在国家
        employees: 员工数量
        revenue_billion: 年收入（十亿美元）
        market_share: 市场份额
        rating: 合作评分（1-5）
        
    返回:
        包含新添加合作伙伴信息的字典
    """
    partner_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    partner = {
        "id": partner_id,
        "name": name,
        "industry": industry,
        "contact_person": contact_person,
        "contact_info": contact_info,
        "tier": tier,
        "notes": notes,
        "added_at": timestamp,
        "last_updated": timestamp,
        "status": "active",
        "country": country,
        "employees": employees,
        "revenue_billion": revenue_billion,
        "market_share": market_share,
        "rating": rating
    }
    
    partners[partner_id] = partner
    cooperation_records[partner_id] = []  # 初始化合作记录列表
    
    return {"status": "success", "partner": partner}

# 工具：记录合作历史
@mcp.tool()
def record_cooperation(partner_id: str, project_name: str, 
                      start_date: str, end_date: Optional[str] = None,
                      value: Optional[float] = None, 
                      outcome: str = "", notes: str = "",
                      quantity: Optional[int] = None,
                      delivery_rate: float = 0.0,
                      quality_rate: float = 0.0,
                      payment_terms: str = "",
                      renewal_potential: str = "") -> Dict:
    """
    记录与合作伙伴的合作历史
    
    参数:
        partner_id: 合作伙伴ID
        project_name: 合作项目名称
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD，未结束可留空）
        value: 合作价值（金额）
        outcome: 合作成果
        notes: 其他备注
        quantity: 供应数量（如适用）
        delivery_rate: 交付达成率（百分比）
        quality_rate: 质量合格率（百分比）
        payment_terms: 付款条件
        renewal_potential: 续约潜力（高/中/低）
        
    返回:
        包含记录结果的字典
    """
    if partner_id not in partners:
        return {"status": "error", "message": f"合作伙伴ID {partner_id} 不存在"}
    
    record_id = str(uuid.uuid4())
    
    cooperation = {
        "record_id": record_id,
        "partner_id": partner_id,
        "project_name": project_name,
        "start_date": start_date,
        "end_date": end_date,
        "value": value,
        "outcome": outcome,
        "notes": notes,
        "recorded_at": datetime.now().isoformat(),
        "quantity": quantity,
        "delivery_rate": delivery_rate,
        "quality_rate": quality_rate,
        "payment_terms": payment_terms,
        "renewal_potential": renewal_potential
    }
    
    cooperation_records[partner_id].append(cooperation)
    
    # 更新合作伙伴最后更新时间
    partners[partner_id]["last_updated"] = datetime.now().isoformat()
    
    return {"status": "success", "cooperation": cooperation}

# 工具：分析合作伙伴价值
@mcp.tool()
def analyze_partner_value(partner_id: str, years: int = 3) -> Dict:
    """
    分析特定合作伙伴的历史价值
    
    参数:
        partner_id: 合作伙伴ID
        years: 分析最近的年数
        
    返回:
        包含价值分析结果的字典
    """
    if partner_id not in partners:
        return {"status": "error", "message": f"合作伙伴ID {partner_id} 不存在"}
    
    partner = partners[partner_id]
    records = cooperation_records.get(partner_id, [])
    
    # 计算时间范围
    cutoff_date = (datetime.now() - timedelta(days=years*365)).strftime("%Y-%m-%d")
    
    # 筛选指定年份内的合作记录
    recent_records = [r for r in records if r["start_date"] >= cutoff_date]
    
    # 计算总合作价值
    total_value = sum(r["value"] or 0 for r in recent_records)
    
    # 计算合作项目数量
    project_count = len(recent_records)
    
    # 计算年均合作价值
    avg_annual_value = total_value / years if years > 0 else 0
    
    # 计算平均交付率和质量率
    avg_delivery_rate = sum(r["delivery_rate"] or 0 for r in recent_records) / project_count if project_count > 0 else 0
    avg_quality_rate = sum(r["quality_rate"] or 0 for r in recent_records) / project_count if project_count > 0 else 0
    
    # 确定合作频率
    frequency = "high" if project_count > years * 2 else "medium" if project_count > 0 else "low"
    
    return {
        "status": "success",
        "partner": {"id": partner_id, "name": partner["name"], "industry": partner["industry"]},
        "analysis_period": f"最近{years}年",
        "total_value": total_value,
        "project_count": project_count,
        "avg_annual_value": avg_annual_value,
        "avg_delivery_rate": avg_delivery_rate,
        "avg_quality_rate": avg_quality_rate,
        "cooperation_frequency": frequency,
        "latest_cooperation": recent_records[-1] if recent_records else None
    }

# 工具：按行业分析合作伙伴
@mcp.tool()
def analyze_by_industry(industry: Optional[str] = None) -> Dict:
    """
    按行业分析合作伙伴分布和价值
    
    参数:
        industry: 特定行业，留空则分析所有行业
        
    返回:
        包含行业分析结果的字典
    """
    # 筛选行业内的合作伙伴
    if industry:
        industry_partners = [p for p in partners.values() if p["industry"] == industry]
    else:
        industry_partners = list(partners.values())
    
    # 按行业分组统计
    industry_stats = {}
    for partner in industry_partners:
        ind = partner["industry"]
        if ind not in industry_stats:
            industry_stats[ind] = {
                "partner_count": 0,
                "total_value": 0.0,
                "project_count": 0,
                "avg_rating": 0.0,
                "total_employees": 0,
                "avg_revenue": 0.0
            }
        
        industry_stats[ind]["partner_count"] += 1
        industry_stats[ind]["avg_rating"] += partner["rating"]
        industry_stats[ind]["total_employees"] += partner["employees"]
        industry_stats[ind]["avg_revenue"] += partner["revenue_billion"]
        
        # 累加该行业所有合作伙伴的合作价值
        for record in cooperation_records.get(partner["id"], []):
            industry_stats[ind]["total_value"] += record["value"] or 0
            industry_stats[ind]["project_count"] += 1
    
    # 计算平均值
    for ind in industry_stats:
        count = industry_stats[ind]["partner_count"]
        industry_stats[ind]["avg_rating"] /= count if count > 0 else 1
        industry_stats[ind]["avg_revenue"] /= count if count > 0 else 1
        industry_stats[ind]["avg_value_per_partner"] = industry_stats[ind]["total_value"] / count if count > 0 else 0
    
    return {
        "status": "success",
        "target_industry": industry,
        "industry_count": len(industry_stats),
        "total_partners": len(industry_partners),
        "industry_stats": industry_stats
    }

# 资源：获取合作伙伴详情
@mcp.resource("partner://{partner_id}")
def get_partner_details(partner_id: str) -> Dict:
    """
    获取特定合作伙伴的详细信息及合作历史
    
    参数:
        partner_id: 合作伙伴ID
        
    返回:
        包含合作伙伴详情和历史的字典
    """
    if partner_id not in partners:
        return {"status": "error", "message": f"合作伙伴ID {partner_id} 不存在"}
    
    return {
        "status": "success",
        "partner": partners[partner_id],
        "cooperation_history": cooperation_records.get(partner_id, []),
        "total_cooperations": len(cooperation_records.get(partner_id, [])),
        "total_cooperation_value": sum(r["value"] or 0 for r in cooperation_records.get(partner_id, []))
    }

# 提示：生成合作伙伴分析报告
@mcp.prompt()
def generate_analysis_report(period: str = "current_year", focus: str = "all") -> str:
    """
    生成手机厂商合作伙伴分析报告的提示词
    
    参数:
        period: 分析周期（current_year-本年度, last_year-去年, last_3_years-近3年）
        focus: 分析重点（all-全部, value-价值, industry-行业分布, tier-合作级别）
        
    返回:
        生成的分析报告提示词
    """
    return f"""
    请生成手机厂商的合作伙伴分析报告，具体要求如下：
    
    分析周期：{period}
    分析重点：{focus}
    
    报告应包含以下内容：
    1. 合作伙伴总体概况（数量、行业分布、合作级别分布）
    2. 各行业合作伙伴的价值贡献分析
    3. 关键合作伙伴的表现评估（交付率、质量率、合作价值）
    4. 合作趋势与模式分析
    5. 潜在的风险与机遇
    6. 合作策略建议（包括新合作领域和优化现有合作）
    
    请以专业、简洁的商业分析风格撰写，使用数据支持结论，
    突出关键发现，并提供可操作的建议。
    """


def main() -> None:
    mcp.run(transport='stdio')

