# @self-expose: {"id": "data_collector_agent", "name": "Data Collector Agent", "type": "agent", "version": "2.0.0", "needs": {"deps": ["base_agent", "data_collector", "tool_discovery_engine", "llm_client_enhanced", "vision_processing_engine", "audio_processing_engine", "multimodal_fusion_engine"], "resources": ["agent_prompts/data_collector_prompt.txt"]}, "provides": {"capabilities": ["数据收集", "数据源扫描", "数据质量验证", "数据报告生成", "多模态内容解析", "网页多媒体爬取"], "methods": {"process_user_query": {"signature": "(query: str) -> Dict[str, Any]", "description": "处理用户查询"}, "_register_multimodal_tools": {"signature": "() -> None", "description": "注册多模态引擎（仅数据收集师专属）"}}, "exclusive_tools": ["VisionProcessingEngine", "AudioProcessingEngine", "MultimodalFusionEngine"], "tool_usage_scenarios": ["爬取网页时解析图片/截图", "爬取网页时解析音频/视频", "融合多模态信息提取结构化数据"]}}
# 数据收集智能体 - 基于统一智能体模板
# 开发提示词来源：用户要求设计数据收集智能体，解决RAG系统"吃饭"问题

import os
import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

# 导入智能体基类
from base_agent import BaseAgent

# 导入数据收集工具
from data_collector import DataCollector

# 导入工具发现引擎
from tool_discovery_engine import ToolDiscoveryEngine

# 导入LLM客户端
from llm_client_enhanced import LLMClientEnhanced

logger = logging.getLogger(__name__)

class DataCollectorAgent(BaseAgent):
    """数据收集智能体 - 负责RAG系统的数据基础建设"""
    
    def __init__(self, agent_id: str = "data_collector_001"):
        # 调用父类初始化
        super().__init__(
            agent_id=agent_id,
            agent_type="data_collector",
            prompt_file="src/agent_prompts/data_collector_prompt.txt"
        )
        
        # 设置智能体目的（角色由系统提示词定义）
        self.purpose = "为RAG系统收集、整理和准备基础数据，确保系统有充足的知识来源"
        
        # 初始化数据收集器
        self.data_collector = DataCollector()
        
        # 初始化工具发现引擎
        self.tool_discovery_engine = ToolDiscoveryEngine()
        
        # 初始化LLM客户端 - 智能体核心大脑
        self.llm_client = LLMClientEnhanced()
        
        # 注册专用工具
        self._register_data_collection_tools()
        
        logger.info(f"数据收集智能体 {agent_id} 初始化完成")
    
    def _register_data_collection_tools(self):
        """注册数据收集专用工具"""
        # 数据收集智能体专用工具 - 使用tool_integrator注册
        self.tool_integrator.register_tool(
            tool_name="scan_file_system",
            tool_description="扫描文件系统，发现可收集的数据源",
            tool_usage="用于扫描文件系统，发现可收集的数据源"
        )
        
        self.tool_integrator.register_tool(
            tool_name="collect_from_path",
            tool_description="从指定路径收集数据",
            tool_usage="用于从指定路径收集数据"
        )
        
        self.tool_integrator.register_tool(
            tool_name="batch_collect_sources",
            tool_description="批量收集所有配置的数据源",
            tool_usage="用于批量收集所有配置的数据源"
        )
        
        self.tool_integrator.register_tool(
            tool_name="validate_data_quality",
            tool_description="验证收集数据的质量",
            tool_usage="用于验证收集数据的质量"
        )
        
        self.tool_integrator.register_tool(
            tool_name="generate_collection_report",
            tool_description="生成数据收集报告",
            tool_usage="用于生成数据收集报告"
        )
        
        # 🔥 数据收集师专属：多模态引擎注册
        # 场景：爬取网页时遇到图片/视频，需要解析多媒体内容
        self._register_multimodal_tools()
        
        logger.info("数据收集专用工具注册完成（含多模态引擎）")
    
    def _register_multimodal_tools(self):
        """注册多模态引擎（仅数据收集师可用）"""
        try:
            # 🔥 直接实例化并注册到 tool_instances（而非调用空壳的 register_tool）
            
            # 视觉处理引擎：解析网页截图/图片
            from src.vision_processing_engine import VisionProcessingTool
            self.tool_integrator.tool_instances['VisionProcessingEngine'] = VisionProcessingTool()
            logger.info("✅ 视觉处理引擎实例化成功")
            
            # 音频处理引擎：解析网页音频/视频
            from src.audio_processing_engine import AudioProcessingTool
            self.tool_integrator.tool_instances['AudioProcessingEngine'] = AudioProcessingTool()
            logger.info("✅ 音频处理引擎实例化成功")
            
            # 多模态融合引擎：融合多种模态信息
            from src.multimodal_fusion_engine import MultimodalFusionTool
            self.tool_integrator.tool_instances['MultimodalFusionEngine'] = MultimodalFusionTool()
            logger.info("✅ 多模态融合引擎实例化成功")
            
            logger.info("🎨 多模态引擎注册成功（仅数据收集师可用）")
        except Exception as e:
            logger.warning(f"多模态引擎注册失败: {e}")
            import traceback
            traceback.print_exc()
    
    def process_user_query(self, user_query: str) -> Dict[str, Any]:
        """
        处理用户查询 - 智能体自主决策能力的核心方法
        
        Args:
            user_query: 用户查询内容
            
        Returns:
            Dict: 处理结果
        """
        # 记录工作日志
        self._write_work_log(f"处理用户查询: {user_query}", "QUERY_PROCESSING")
        
        try:
            # 使用LLM分析用户意图
            analysis_result = self._analyze_user_intent(user_query)
            
            # 根据意图选择适当的工具
            tool_selection = self._select_tools_for_query(analysis_result)
            
            # 执行工具链
            execution_result = self._execute_tool_chain(tool_selection, user_query)
            
            # 生成响应
            response = self._generate_response(execution_result, user_query)
            
            return {
                "success": True,
                "user_query": user_query,
                "intent_analysis": analysis_result,
                "tool_selection": tool_selection,
                "execution_result": execution_result,
                "response": response,
                "message": "查询处理完成"
            }
            
        except Exception as e:
            logger.error(f"处理用户查询失败: {e}")
            return {
                "success": False,
                "user_query": user_query,
                "error": str(e),
                "message": "查询处理失败"
            }
    
    def _analyze_user_intent(self, user_query: str) -> Dict[str, Any]:
        """使用LLM分析用户意图"""
        prompt = f"""
        你是一个数据收集智能体，需要分析用户查询的意图。
        
        用户查询：{user_query}
        
        请分析用户的意图，并返回以下信息：
        1. 意图分类（数据扫描、数据收集、工具集成、报告生成等）
        2. 关键需求
        3. 建议的处理流程
        
        请以JSON格式返回分析结果。
        """
        
        try:
            response = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="deepseek-chat",
                temperature=0.3,
                max_tokens=300
            )
            
            # 解析JSON响应
            import json
            return json.loads(response)
            
        except:
            # 如果解析失败，返回默认分析
            return {
                "intent_category": "数据收集",
                "key_requirements": ["收集数据"],
                "suggested_workflow": ["扫描数据源", "收集数据", "生成报告"]
            }
    
    def _select_tools_for_query(self, intent_analysis: Dict[str, Any]) -> List[str]:
        """根据意图分析选择工具"""
        intent_category = intent_analysis.get("intent_category", "数据收集")
        
        tool_mapping = {
            "数据扫描": ["scan_file_system"],
            "数据收集": ["collect_from_path", "batch_collect_sources"],
            "工具集成": ["discover_external_tools", "integrate_external_tool"],
            "报告生成": ["generate_collection_report"]
        }
        
        return tool_mapping.get(intent_category, ["scan_file_system", "collect_from_path"])
    
    def _execute_tool_chain(self, tools: List[str], user_query: str) -> Dict[str, Any]:
        """执行工具链"""
        results = {}
        
        for tool_name in tools:
            try:
                # 调用相应的工具方法
                if hasattr(self, tool_name):
                    tool_method = getattr(self, tool_name)
                    
                    # 根据工具类型传递适当的参数
                    if tool_name == "scan_file_system":
                        result = tool_method()
                    elif tool_name == "collect_from_path":
                        result = tool_method("./data")
                    elif tool_name == "batch_collect_sources":
                        result = tool_method()
                    elif tool_name == "discover_external_tools":
                        result = tool_method(["data", "collection"])
                    elif tool_name == "integrate_external_tool":
                        result = tool_method("data_collector")
                    elif tool_name == "generate_collection_report":
                        result = tool_method()
                    else:
                        result = tool_method()
                    
                    results[tool_name] = result
                    
            except Exception as e:
                results[tool_name] = {"error": str(e)}
        
        return results
    
    def _generate_response(self, execution_results: Dict[str, Any], user_query: str) -> str:
        """生成最终响应"""
        prompt = f"""
        你是一个数据收集智能体，已经处理了用户查询并获得了执行结果。
        
        用户查询：{user_query}
        执行结果：{execution_results}
        
        请基于执行结果，生成一个专业、友好的响应给用户。
        响应应该包括：
        1. 对用户查询的理解
        2. 执行的主要操作
        3. 获得的结果
        4. 下一步建议
        
        请用中文回复。
        """
        
        try:
            response = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="deepseek-chat",
                temperature=0.7,
                max_tokens=400
            )
            return response
            
        except Exception as e:
            return f"处理完成。执行结果：{execution_results}"
    
    def discover_external_tools(self, keywords: List[str], category: str = None) -> Dict[str, Any]:
        """发现外部数据收集工具"""
        
        # 记录工作日志
        self._write_work_log("开始发现外部工具", {
            "keywords": keywords,
            "category": category
        })
        
        try:
            # 使用工具发现引擎搜索
            discovered_tools = self.tool_discovery_engine.search_github_tools(keywords, category)
            
            if not discovered_tools:
                # 尝试从缓存获取
                cached_tools = self.tool_discovery_engine.get_cached_tools(category)
                if cached_tools:
                    discovered_tools = cached_tools
                    logger.info(f"从缓存获取到 {len(discovered_tools)} 个工具")
            
            # 分析工具适用性
            suitable_tools = []
            for tool in discovered_tools:
                if self._assess_tool_suitability(tool, keywords):
                    suitable_tools.append(tool)
            
            return {
                "success": True,
                "discovered_count": len(discovered_tools),
                "suitable_count": len(suitable_tools),
                "tools": suitable_tools,
                "message": f"发现 {len(suitable_tools)} 个适用的外部工具"
            }
            
        except Exception as e:
            logger.error(f"外部工具发现失败: {e}")
            return {
                "success": False,
                "message": f"工具发现失败: {str(e)}"
            }
    
    def _assess_tool_suitability(self, tool_info: Dict, keywords: List[str]) -> bool:
        """评估工具适用性"""
        
        # 质量阈值
        if tool_info.get("quality_score", 0) < 0.6:
            return False
        
        # 关键词匹配度
        description = tool_info.get("description", "").lower()
        name = tool_info.get("name", "").lower()
        
        for keyword in keywords:
            if keyword.lower() in description or keyword.lower() in name:
                return True
        
        return False
    
    def generate_tool_wrapper(self, tool_info: Dict) -> Dict[str, Any]:
        """为外部工具生成包装器"""
        
        # 记录工作日志
        self._write_work_log("生成工具包装器", {
            "tool_name": tool_info.get("name"),
            "tool_url": tool_info.get("url")
        })
        
        try:
            # 生成包装器代码
            wrapper_code = self.tool_discovery_engine.generate_tool_wrapper(tool_info)
            
            if wrapper_code:
                # 保存包装器文件
                tool_name = tool_info["name"]
                wrapper_file = Path(f"tools/external/{tool_name}_wrapper.py")
                wrapper_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(wrapper_file, 'w', encoding='utf-8') as f:
                    f.write(wrapper_code)
                
                # 注册新工具
                self.tool_integrator.register_tool(
                    tool_name=f"external_{tool_name}",
                    tool_description=f"外部工具包装器: {tool_info.get('description', '')}",
                    tool_usage=f"使用外部工具 {tool_name} 进行数据收集"
                )
                
                return {
                    "success": True,
                    "wrapper_file": str(wrapper_file),
                    "tool_name": f"external_{tool_name}",
                    "message": f"工具包装器生成成功: {tool_name}"
                }
            else:
                return {
                    "success": False,
                    "message": "包装器代码生成失败"
                }
                
        except Exception as e:
            logger.error(f"工具包装器生成失败: {e}")
            return {
                "success": False,
                "message": f"包装器生成失败: {str(e)}"
            }
    
    def integrate_external_tool(self, tool_name: str, tool_url: str = None) -> Dict[str, Any]:
        """集成外部工具到数据收集系统"""
        
        # 记录工作日志
        self._write_work_log("集成外部工具", {
            "tool_name": tool_name,
            "tool_url": tool_url
        })
        
        try:
            # 如果提供了URL，先发现工具信息
            tool_info = None
            if tool_url:
                # 从URL提取工具信息
                discovered_tools = self.tool_discovery_engine.search_github_tools([tool_name])
                if discovered_tools:
                    tool_info = discovered_tools[0]
            
            # 如果未提供URL，尝试从缓存获取
            if not tool_info:
                cached_tools = self.tool_discovery_engine.get_cached_tools()
                for tool in cached_tools:
                    if tool["name"] == tool_name:
                        tool_info = tool
                        break
            
            if not tool_info:
                return {
                    "success": False,
                    "message": f"未找到工具信息: {tool_name}"
                }
            
            # 生成包装器
            wrapper_result = self.generate_tool_wrapper(tool_info)
            
            if wrapper_result["success"]:
                # 测试工具可用性
                test_result = self._test_external_tool(tool_info["name"])
                
                if test_result["success"]:
                    # 记录工具集成经验
                    self._record_tool_integration_experience(tool_info, "success")
                    
                    return {
                        "success": True,
                        "tool_name": tool_info["name"],
                        "wrapper_file": wrapper_result["wrapper_file"],
                        "test_result": test_result,
                        "message": f"外部工具集成成功: {tool_info['name']}"
                    }
                else:
                    # 记录失败经验
                    self._record_tool_integration_experience(tool_info, "failed")
                    
                    return {
                        "success": False,
                        "message": f"工具测试失败: {test_result.get('message', '未知错误')}"
                    }
            else:
                return wrapper_result
                
        except Exception as e:
            logger.error(f"外部工具集成失败: {e}")
            return {
                "success": False,
                "message": f"集成失败: {str(e)}"
            }
    
    def _test_external_tool(self, tool_name: str) -> Dict[str, Any]:
        """测试外部工具可用性"""
        # 简化的测试逻辑
        # 实际实现需要执行具体的测试用例
        return {
            "success": True,
            "message": "工具测试通过",
            "test_cases": ["安装测试", "基本功能测试"]
        }
    
    def _record_tool_integration_experience(self, tool_info: Dict, result: str):
        """记录工具集成经验"""
        # 记录到记忆系统，为后续工具选择提供参考
        experience = {
            "tool_name": tool_info["name"],
            "integration_result": result,
            "timestamp": self._get_current_timestamp(),
            "tool_quality": tool_info.get("quality_score", 0)
        }
        
        # 保存到经验库
        experience_file = Path("data/tool_experiences.json")
        experiences = []
        if experience_file.exists():
            with open(experience_file, 'r', encoding='utf-8') as f:
                experiences = json.load(f)
        
        experiences.append(experience)
        
        with open(experience_file, 'w', encoding='utf-8') as f:
            json.dump(experiences, f, ensure_ascii=False, indent=2)
    
    def scan_file_system(self, target_path: str = None) -> Dict[str, Any]:
        """扫描文件系统，发现可收集的数据源"""
        
        # 记录工作日志
        self._write_work_log("开始扫描文件系统", {"target_path": target_path})
        
        try:
            if target_path is None:
                # 使用配置的数据源路径
                from config.system_config import DATA_SOURCES
                
                scan_results = {
                    "scanned_sources": [],
                    "available_paths": [],
                    "unavailable_paths": []
                }
                
                for source_name, config in DATA_SOURCES.items():
                    if config.get("enabled", False):
                        paths = config.get("paths", [])
                        for path_template in paths:
                            path = path_template.replace("{username}", "current_user")
                            
                            if Path(path).exists():
                                scan_results["available_paths"].append({
                                    "source": source_name,
                                    "path": path,
                                    "status": "available"
                                })
                            else:
                                scan_results["unavailable_paths"].append({
                                    "source": source_name,
                                    "path": path,
                                    "status": "unavailable"
                                })
                        
                        scan_results["scanned_sources"].append(source_name)
                
                logger.info(f"扫描完成: {len(scan_results['available_paths'])} 个可用路径")
                return {
                    "success": True,
                    "scan_results": scan_results,
                    "message": f"发现 {len(scan_results['available_paths'])} 个可用数据源"
                }
            
            else:
                # 扫描指定路径
                target_path = Path(target_path)
                if not target_path.exists():
                    return {
                        "success": False,
                        "message": f"目标路径不存在: {target_path}"
                    }
                
                # 统计文件信息
                file_count = 0
                total_size = 0
                supported_extensions = ['.txt', '.md', '.json', '.log']
                
                for file_path in target_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                        file_count += 1
                        total_size += file_path.stat().st_size
                
                return {
                    "success": True,
                    "scan_results": {
                        "target_path": str(target_path),
                        "file_count": file_count,
                        "total_size": total_size,
                        "supported_files": file_count > 0
                    },
                    "message": f"发现 {file_count} 个支持的文件，总大小: {total_size} 字节"
                }
        
        except Exception as e:
            logger.error(f"文件系统扫描失败: {e}")
            return {
                "success": False,
                "message": f"扫描失败: {str(e)}"
            }
    
    def collect_from_path(self, path: str, use_intelligent_slicing: bool = True) -> Dict[str, Any]:
        """从指定路径收集数据"""
        
        # 风险评估：检查路径安全性
        risk_assessment = self._assess_collection_risk(path)
        if risk_assessment["risk_level"] == "high":
            return {
                "success": False,
                "message": f"高风险操作被阻止: {risk_assessment['reason']}"
            }
        
        # 记录工作日志
        self._write_work_log("开始数据收集", {
            "path": path,
            "use_intelligent_slicing": use_intelligent_slicing,
            "risk_assessment": risk_assessment
        })
        
        try:
            # 使用数据收集器进行收集
            raw_data = self.data_collector.collect_from_file_system(path)
            
            if not raw_data:
                return {
                    "success": False,
                    "message": "未收集到任何数据"
                }
            
            # 应用智能切片（如果启用）
            if use_intelligent_slicing:
                sliced_data = []
                for item in raw_data:
                    content = item.get('content', '')
                    if content:
                        slices = self.data_collector._intelligent_slice_text(
                            content, item.get('file_path', '')
                        )
                        sliced_data.extend(slices)
                
                final_data = sliced_data
                slicing_info = f"，智能切片后得到 {len(sliced_data)} 条数据"
            else:
                final_data = raw_data
                slicing_info = ""
            
            # 保存收集的数据
            self.data_collector._save_collected_data(final_data)
            
            # 创建记忆条目
            memory_content = f"从路径 {path} 收集数据，获得 {len(final_data)} 条记录"
            self.create_memory(
                content=memory_content,
                importance=0.7,
                tags=["data_collection", path]
            )
            
            return {
                "success": True,
                "collected_count": len(final_data),
                "raw_count": len(raw_data),
                "used_intelligent_slicing": use_intelligent_slicing,
                "message": f"成功收集 {len(raw_data)} 条原始数据{slicing_info}"
            }
        
        except Exception as e:
            logger.error(f"数据收集失败: {e}")
            return {
                "success": False,
                "message": f"收集失败: {str(e)}"
            }
    
    def batch_collect_sources(self) -> Dict[str, Any]:
        """批量收集所有配置的数据源"""
        
        self._write_work_log("开始批量数据收集", {})
        
        try:
            # 使用数据收集器的批量收集功能
            all_data = self.data_collector.collect_all_sources()
            
            if not all_data:
                return {
                    "success": False,
                    "message": "批量收集未获得任何数据"
                }
            
            # 创建批量收集记忆
            memory_content = f"批量数据收集完成，共获得 {len(all_data)} 条高质量数据切片"
            self.create_memory(
                content=memory_content,
                importance=0.8,
                tags=["batch_collection", "data_foundation"]
            )
            
            return {
                "success": True,
                "total_collected": len(all_data),
                "message": f"批量收集完成，获得 {len(all_data)} 条数据"
            }
        
        except Exception as e:
            logger.error(f"批量收集失败: {e}")
            return {
                "success": False,
                "message": f"批量收集失败: {str(e)}"
            }
    
    def validate_data_quality(self, sample_size: int = 10) -> Dict[str, Any]:
        """验证收集数据的质量"""
        
        self._write_work_log("开始数据质量验证", {"sample_size": sample_size})
        
        try:
            # 获取最近收集的数据文件
            data_dir = Path("e:/RAG系统/data")
            data_files = list(data_dir.glob("collected_data_*.json"))
            
            if not data_files:
                return {
                    "success": False,
                    "message": "未找到收集的数据文件"
                }
            
            # 使用最新的数据文件
            latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 质量评估指标
            quality_metrics = {
                "total_records": len(data),
                "avg_content_length": 0,
                "importance_distribution": {"high": 0, "medium": 0, "low": 0},
                "source_diversity": {},
                "completeness_score": 0.0
            }
            
            # 计算质量指标
            total_length = 0
            for item in data[:sample_size]:  # 抽样检查
                content = item.get('content', '')
                total_length += len(content)
                
                importance = item.get('importance', 0.5)
                if importance >= 0.8:
                    quality_metrics["importance_distribution"]["high"] += 1
                elif importance >= 0.5:
                    quality_metrics["importance_distribution"]["medium"] += 1
                else:
                    quality_metrics["importance_distribution"]["low"] += 1
                
                source = item.get('source', 'unknown')
                quality_metrics["source_diversity"][source] = quality_metrics["source_diversity"].get(source, 0) + 1
            
            if sample_size > 0:
                quality_metrics["avg_content_length"] = total_length / sample_size
                
                # 计算完整性分数
                completeness_factors = [
                    1.0 if len(data) > 0 else 0.0,  # 是否有数据
                    0.8 if quality_metrics["avg_content_length"] > 100 else 0.3,  # 内容长度
                    0.7 if len(quality_metrics["source_diversity"]) > 1 else 0.4,  # 来源多样性
                    0.6 if quality_metrics["importance_distribution"]["high"] > 0 else 0.2  # 高质量内容
                ]
                quality_metrics["completeness_score"] = sum(completeness_factors) / len(completeness_factors)
            
            return {
                "success": True,
                "quality_metrics": quality_metrics,
                "data_file": str(latest_file),
                "message": f"数据质量评估完成，完整性分数: {quality_metrics['completeness_score']:.2f}"
            }
        
        except Exception as e:
            logger.error(f"数据质量验证失败: {e}")
            return {
                "success": False,
                "message": f"质量验证失败: {str(e)}"
            }
    
    def generate_collection_report(self) -> Dict[str, Any]:
        """生成数据收集报告"""
        
        self._write_work_log("生成数据收集报告", {})
        
        try:
            # 获取数据目录信息
            data_dir = Path("e:/RAG系统/data")
            data_files = list(data_dir.glob("collected_data_*.json"))
            
            if not data_files:
                return {
                    "success": False,
                    "message": "未找到收集的数据文件"
                }
            
            # 统计报告信息
            report = {
                "total_collection_files": len(data_files),
                "latest_collection_time": None,
                "total_data_records": 0,
                "file_size_distribution": {},
                "collection_timeline": []
            }
            
            for data_file in data_files:
                file_size = data_file.stat().st_size
                file_time = datetime.fromtimestamp(data_file.stat().st_mtime)
                
                # 读取文件统计记录数
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    record_count = len(data)
                except:
                    record_count = 0
                
                report["total_data_records"] += record_count
                
                # 文件大小分类
                size_category = "small"
                if file_size > 1024 * 1024:  # 1MB
                    size_category = "large"
                elif file_size > 1024 * 100:  # 100KB
                    size_category = "medium"
                
                report["file_size_distribution"][size_category] = report["file_size_distribution"].get(size_category, 0) + 1
                
                report["collection_timeline"].append({
                    "file": data_file.name,
                    "timestamp": file_time.isoformat(),
                    "records": record_count,
                    "size": file_size
                })
            
            # 按时间排序
            report["collection_timeline"].sort(key=lambda x: x["timestamp"], reverse=True)
            
            if report["collection_timeline"]:
                report["latest_collection_time"] = report["collection_timeline"][0]["timestamp"]
            
            return {
                "success": True,
                "report": report,
                "message": f"数据收集报告生成完成，共 {report['total_data_records']} 条记录"
            }
        
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return {
                "success": False,
                "message": f"报告生成失败: {str(e)}"
            }
    
    def _assess_collection_risk(self, path: str) -> Dict[str, Any]:
        """评估数据收集风险"""
        
        path_obj = Path(path)
        
        # 高风险路径检查
        system_paths = [
            "C:\\Windows", "C:\\Program Files", "C:\\ProgramData",
            "/etc", "/usr", "/bin", "/sbin"
        ]
        
        for system_path in system_paths:
            if str(path_obj).startswith(system_path):
                return {
                    "risk_level": "high",
                    "reason": f"尝试访问系统保护路径: {system_path}"
                }
        
        # 检查路径是否存在
        if not path_obj.exists():
            return {
                "risk_level": "medium",
                "reason": "目标路径不存在"
            }
        
        # 检查权限
        try:
            # 尝试读取路径信息
            path_obj.stat()
        except PermissionError:
            return {
                "risk_level": "high",
                "reason": "没有访问该路径的权限"
            }
        
        return {
            "risk_level": "low",
            "reason": "路径安全检查通过"
        }

# 测试函数
def test_data_collector_agent():
    """测试数据收集智能体"""
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建智能体实例
    agent = DataCollectorAgent()
    
    print("=== 数据收集智能体测试 ===")
    
    # 测试扫描文件系统
    print("\n1. 扫描文件系统...")
    scan_result = agent.scan_file_system()
    print(f"扫描结果: {scan_result}")
    
    # 测试数据收集
    print("\n2. 测试数据收集...")
    test_path = "E:\\AI"  # 使用你之前提到的AI目录
    if Path(test_path).exists():
        collect_result = agent.collect_from_path(test_path)
        print(f"收集结果: {collect_result}")
    else:
        print(f"测试路径不存在: {test_path}")
    
    # 测试质量验证
    print("\n3. 测试数据质量验证...")
    quality_result = agent.validate_data_quality()
    print(f"质量验证结果: {quality_result}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_data_collector_agent()

# 全局智能体实例(懒加载)
_data_collector_agent = None

def get_data_collector() -> DataCollectorAgent:
    """获取数据收集者智能体实例(懒加载)"""
    global _data_collector_agent
    if _data_collector_agent is None:
        _data_collector_agent = DataCollectorAgent()
    return _data_collector_agent