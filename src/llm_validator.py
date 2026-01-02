# LLM切片质量验证器
# 技术来源：用户提出的"LLM仅作为切片检验员"概念
# 核心创新：将LLM从切片执行者降级为质量检验员，实现成本优化
# @self-expose: {"id": "llm_validator", "name": "Llm Validator", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Llm Validator功能"]}}

import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidatorConfig:
    """验证器配置"""
    quality_threshold: float = 0.7  # 质量阈值
    max_validation_batch: int = 10  # 最大验证批次大小
    enable_feedback: bool = True  # 是否启用改进建议

class LLMQualityValidator:
    """LLM切片质量验证器"""
    
    def __init__(self, llm_client=None, config: Optional[ValidatorConfig] = None):
        self.config = config or ValidatorConfig()
        self.llm_client = llm_client
        
    def validate_slice_quality(self, slices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        验证切片质量
        
        算法原理：
        1. 批量验证切片逻辑完整性
        2. 提供质量评分和改进建议
        3. 过滤低质量切片
        """
        if not slices:
            return []
            
        # 批量验证
        validated_slices = []
        batch_size = self.config.max_validation_batch
        
        for i in range(0, len(slices), batch_size):
            batch = slices[i:i + batch_size]
            batch_results = self._validate_batch(batch)
            validated_slices.extend(batch_results)
        
        # 过滤低质量切片
        filtered_slices = [
            slice_data for slice_data in validated_slices
            if slice_data.get('llm_quality_score', 0) >= self.config.quality_threshold
        ]
        
        logger.info(f"LLM验证完成：原始{len(slices)}个切片，验证后{len(filtered_slices)}个合格")
        
        return filtered_slices
    
    def _validate_batch(self, slices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量验证切片"""
        if not self.llm_client:
            # 如果没有LLM客户端，使用模拟验证
            return self._simulate_validation(slices)
        
        try:
            # 构建验证提示词
            prompt = self._build_validation_prompt(slices)
            
            # 调用LLM进行验证
            response = self.llm_client.generate_response(prompt)
            
            # 解析验证结果
            return self._parse_validation_response(response, slices)
            
        except Exception as e:
            logger.error(f"LLM验证失败: {e}，使用模拟验证")
            return self._simulate_validation(slices)
    
    def _build_validation_prompt(self, slices: List[Dict[str, Any]]) -> str:
        """构建验证提示词"""
        slices_info = []
        
        for i, slice_data in enumerate(slices):
            content = slice_data.get('content', '')[:500]  # 限制内容长度
            slice_id = slice_data.get('slice_id', f'slice_{i}')
            
            slices_info.append({
                "slice_id": slice_id,
                "content": content,
                "original_quality": slice_data.get('semantic_quality', 0.5)
            })
        
        prompt = f"""请评估以下文本切片的逻辑完整性质量。每个切片都应该是一个语义完整的逻辑单元。

切片列表：
{json.dumps(slices_info, ensure_ascii=False, indent=2)}

请按以下标准进行评估：
1. 逻辑完整性：切片是否包含完整的逻辑链（开头-发展-结尾）
2. 语义连贯性：内容是否语义连贯，没有突兀的断点
3. 信息密度：是否包含足够的信息量
4. 边界合理性：切片的边界是否在逻辑转折点

对于每个切片，请提供：
- 质量评分（0-1分，1为最佳）
- 逻辑完整性评估（完整/基本完整/不完整）
- 改进建议（如有需要）

请以JSON格式输出评估结果，格式如下：
{{
  "validation_results": [
    {{
      "slice_id": "slice_0",
      "llm_quality_score": 0.85,
      "logic_completeness": "完整",
      "improvement_suggestions": "无",
      "is_valid": true
    }}
  ]
}}

请确保输出为有效的JSON格式："""
        
        return prompt
    
    def _parse_validation_response(self, response: Dict[str, Any], 
                                 original_slices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析LLM验证结果"""
        try:
            content = response.get('content', '')
            
            # 提取JSON部分
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("未找到有效的JSON响应")
            
            json_str = content[json_start:json_end]
            validation_data = json.loads(json_str)
            
            results = validation_data.get('validation_results', [])
            
            # 更新原始切片数据
            validated_slices = []
            
            for result in results:
                slice_id = result.get('slice_id')
                
                # 找到对应的原始切片
                original_slice = None
                for slice_data in original_slices:
                    if slice_data.get('slice_id') == slice_id:
                        original_slice = slice_data
                        break
                
                if original_slice:
                    # 更新切片数据
                    updated_slice = original_slice.copy()
                    updated_slice['llm_quality_score'] = result.get('llm_quality_score', 0.5)
                    updated_slice['logic_completeness'] = result.get('logic_completeness', '未知')
                    updated_slice['improvement_suggestions'] = result.get('improvement_suggestions', '')
                    updated_slice['is_valid'] = result.get('is_valid', False)
                    updated_slice['validation_method'] = 'llm'
                    
                    # 更新综合质量评分
                    original_quality = updated_slice.get('semantic_quality', 0.5)
                    llm_quality = updated_slice['llm_quality_score']
                    updated_slice['semantic_quality'] = (original_quality * 0.4 + llm_quality * 0.6)
                    
                    validated_slices.append(updated_slice)
            
            return validated_slices
            
        except Exception as e:
            logger.error(f"解析验证结果失败: {e}")
            return self._simulate_validation(original_slices)
    
    def _simulate_validation(self, slices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """模拟验证（当LLM不可用时）"""
        validated_slices = []
        
        for slice_data in slices:
            updated_slice = slice_data.copy()
            
            # 基于现有质量评分进行模拟
            original_quality = slice_data.get('semantic_quality', 0.5)
            
            # 模拟LLM质量评分（基于现有质量的调整）
            if original_quality >= 0.8:
                llm_score = 0.85
                completeness = "完整"
            elif original_quality >= 0.6:
                llm_score = 0.7
                completeness = "基本完整"
            else:
                llm_score = 0.4
                completeness = "不完整"
            
            updated_slice['llm_quality_score'] = llm_score
            updated_slice['logic_completeness'] = completeness
            updated_slice['improvement_suggestions'] = "模拟验证 - 建议使用真实LLM验证"
            updated_slice['is_valid'] = llm_score >= self.config.quality_threshold
            updated_slice['validation_method'] = 'simulated'
            
            # 更新综合质量评分
            updated_slice['semantic_quality'] = (original_quality * 0.4 + llm_score * 0.6)
            
            validated_slices.append(updated_slice)
        
        return validated_slices
    
    def provide_feedback(self, slices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        提供分片质量反馈和改进建议
        
        返回整体质量分析和优化建议
        """
        if not slices:
            return {"error": "无切片数据"}
        
        # 统计质量分布
        quality_scores = [s.get('semantic_quality', 0) for s in slices]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # 合格率统计
        valid_count = sum(1 for s in slices if s.get('is_valid', False))
        valid_ratio = valid_count / len(slices) if slices else 0
        
        # 质量分布
        excellent = sum(1 for s in slices if s.get('semantic_quality', 0) >= 0.9)
        good = sum(1 for s in slices if 0.7 <= s.get('semantic_quality', 0) < 0.9)
        fair = sum(1 for s in slices if 0.5 <= s.get('semantic_quality', 0) < 0.7)
        poor = sum(1 for s in slices if s.get('semantic_quality', 0) < 0.5)
        
        feedback = {
            "total_slices": len(slices),
            "valid_slices": valid_count,
            "valid_ratio": valid_ratio,
            "average_quality": avg_quality,
            "quality_distribution": {
                "excellent": excellent,
                "good": good,
                "fair": fair,
                "poor": poor
            },
            "recommendations": []
        }
        
        # 生成改进建议
        if avg_quality < 0.7:
            feedback["recommendations"].append("建议调整信息熵阈值，优化逻辑边界检测")
        
        if valid_ratio < 0.8:
            feedback["recommendations"].append("建议优化切片大小配置，提高合格率")
        
        if poor > len(slices) * 0.3:
            feedback["recommendations"].append("大量切片质量较差，建议重新评估分片策略")
        
        # 添加具体改进建议
        for slice_data in slices:
            if slice_data.get('semantic_quality', 0) < 0.5:
                suggestions = slice_data.get('improvement_suggestions', '')
                if suggestions and suggestions not in feedback["recommendations"]:
                    feedback["recommendations"].append(f"低质量切片建议: {suggestions}")
        
        return feedback

def test_llm_validator():
    """测试LLM验证器"""
    # 创建测试切片数据
    test_slices = [
        {
            "slice_id": "test_slice_1",
            "content": "今天天气很好，阳光明媚。我决定去公园散步。公园里有很多人在锻炼身体。",
            "slice_size": 45,
            "semantic_quality": 0.8,
            "slice_method": "entropy_based"
        },
        {
            "slice_id": "test_slice_2", 
            "content": "突然，天空变暗，开始下起雨来。我赶紧找地方躲雨。",
            "slice_size": 25,
            "semantic_quality": 0.7,
            "slice_method": "entropy_based"
        },
        {
            "slice_id": "test_slice_3",
            "content": "雨停后，天空出现了一道美丽的彩虹。我感到非常开心。",
            "slice_size": 30,
            "semantic_quality": 0.9,
            "slice_method": "entropy_based"
        }
    ]
    
    # 使用模拟验证器
    validator = LLMQualityValidator()  # 不提供LLM客户端，使用模拟验证
    
    validated_slices = validator.validate_slice_quality(test_slices)
    
    print(f"验证结果：{len(validated_slices)} 个合格切片")
    for i, slice_data in enumerate(validated_slices):
        print(f"\n{i+1}. 切片ID: {slice_data['slice_id']}")
        print(f"   LLM质量评分: {slice_data.get('llm_quality_score', 0):.2f}")
        print(f"   逻辑完整性: {slice_data.get('logic_completeness', '未知')}")
        print(f"   综合质量: {slice_data.get('semantic_quality', 0):.2f}")
        print(f"   是否合格: {slice_data.get('is_valid', False)}")
    
    # 获取反馈
    feedback = validator.provide_feedback(validated_slices)
    print(f"\n质量反馈:")
    print(f"总切片数: {feedback['total_slices']}")
    print(f"合格率: {feedback['valid_ratio']:.2%}")
    print(f"平均质量: {feedback['average_quality']:.2f}")
    print(f"改进建议: {feedback['recommendations']}")

if __name__ == "__main__":
    test_llm_validator()