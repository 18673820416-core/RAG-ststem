# @self-expose: {"id": "mention_parser", "name": "Mention Parser", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Mention Parser功能"]}}
"""
@机制解析器 - 支持智能体名称自动补全和选择
开发提示词来源：用户要求实现微信式@智能体选择功能，支持智能体自定义名称
"""

import re
from typing import List, Dict, Optional, Tuple
from enum import Enum

class MentionType(Enum):
    """@类型枚举"""
    AGENT_MENTION = "agent"  # @智能体
    TOPIC_MENTION = "topic"  # @话题
    ACTION_MENTION = "action"  # @动作

class MentionParser:
    """@机制解析器"""
    
    def __init__(self):
        # 智能体配置 - 支持自定义名称
        self.agents_config = {
            "architect": {
                "id": "architect",
                "name": "系统管家",
                "nicknames": ["系统管家", "管家", "系统", "管理"],
                "role": "负责RAG系统的整体管理、技术决策和系统规划",
                "color": "#FF6B6B",
                "icon": "🏗️"
            },
            "evaluator": {
                "id": "evaluator", 
                "name": "方案评估师",
                "nicknames": ["评估师", "方案评估", "评估", "风险分析"],
                "role": "负责方案可行性评估、风险分析和成本效益评估",
                "color": "#4ECDC4",
                "icon": "📊"
            },
            "implementer": {
                "id": "implementer",
                "name": "文本实现师", 
                "nicknames": ["实现师", "文本实现", "开发", "实现"],
                "role": "负责文本实现、内容编写和系统部署",
                "color": "#45B7D1",
                "icon": "💻"
            },
            "collector": {
                "id": "collector",
                "name": "数据收集师",
                "nicknames": ["收集师", "数据收集", "爬虫", "数据采集"],
                "role": "负责数据收集、信息爬取和知识库构建",
                "color": "#96CEB4",
                "icon": "📚"
            }
        }
        
        # 用户自定义名称存储
        self.custom_names = {}
        
        # 加载保存的自定义名称
        self._load_custom_names()
    
    def _load_custom_names(self):
        """加载用户自定义名称"""
        try:
            import json
            import os
            
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "agent_custom_names.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.custom_names = json.load(f)
        except Exception as e:
            print(f"加载自定义名称失败: {e}")
    
    def _save_custom_names(self):
        """保存用户自定义名称"""
        try:
            import json
            import os
            
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "agent_custom_names.json")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.custom_names, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自定义名称失败: {e}")
    
    def set_custom_name(self, agent_id: str, custom_name: str):
        """设置智能体自定义名称"""
        if agent_id in self.agents_config:
            self.custom_names[agent_id] = custom_name
            self._save_custom_names()
            return True
        return False
    
    def get_agent_display_name(self, agent_id: str) -> str:
        """获取智能体显示名称（优先使用自定义名称）"""
        if agent_id in self.custom_names:
            return self.custom_names[agent_id]
        return self.agents_config[agent_id]["name"]
    
    def get_all_agents(self) -> List[Dict]:
        """获取所有智能体信息（包含自定义名称）"""
        agents = []
        for agent_id, config in self.agents_config.items():
            agent_info = config.copy()
            agent_info["display_name"] = self.get_agent_display_name(agent_id)
            agents.append(agent_info)
        return agents
    
    def parse_mentions(self, text: str) -> List[Dict]:
        """解析文本中的@提及"""
        mentions = []
        
        # 匹配@智能体模式 - 修复：只匹配单个@符号后面的智能体名称，避免@@情况
        agent_pattern = r'@([^\s@]+)'
        matches = re.finditer(agent_pattern, text)
        
        for match in matches:
            mention_text = match.group(1)
            start_pos = match.start()
            end_pos = match.end()
            
            # 查找匹配的智能体
            matched_agent = self._find_matching_agent(mention_text)
            
            if matched_agent:
                mentions.append({
                    "type": MentionType.AGENT_MENTION.value,
                    "agent_id": matched_agent["id"],
                    "display_name": matched_agent["display_name"],
                    "original_text": f"@{mention_text}",
                    "start_pos": start_pos,
                    "end_pos": end_pos,
                    "matched_text": mention_text
                })
        
        return mentions
    
    def _find_matching_agent(self, text: str) -> Optional[Dict]:
        """查找匹配的智能体"""
        text_lower = text.lower()
        
        # 首先检查自定义名称
        for agent_id, custom_name in self.custom_names.items():
            if text_lower in custom_name.lower():
                agent_info = self.agents_config[agent_id].copy()
                agent_info["display_name"] = custom_name
                return agent_info
        
        # 检查标准名称和昵称
        for agent_id, config in self.agents_config.items():
            # 检查标准名称
            if text_lower in config["name"].lower():
                agent_info = config.copy()
                agent_info["display_name"] = self.get_agent_display_name(agent_id)
                return agent_info
            
            # 检查昵称
            for nickname in config["nicknames"]:
                if text_lower in nickname.lower():
                    agent_info = config.copy()
                    agent_info["display_name"] = self.get_agent_display_name(agent_id)
                    return agent_info
        
        return None
    
    def find_agent_suggestions(self, partial_text: str) -> List[Dict]:
        """根据部分文本查找智能体建议"""
        suggestions = []
        partial_lower = partial_text.lower()
        
        # 检查所有智能体的名称和昵称
        for agent_id, config in self.agents_config.items():
            display_name = self.get_agent_display_name(agent_id)
            
            # 检查显示名称
            if partial_lower in display_name.lower():
                suggestions.append({
                    "agent_id": agent_id,
                    "display_name": display_name,
                    "role": config["role"],
                    "color": config["color"],
                    "icon": config["icon"],
                    "match_type": "display_name"
                })
                continue
            
            # 检查标准名称
            if partial_lower in config["name"].lower():
                suggestions.append({
                    "agent_id": agent_id,
                    "display_name": display_name,
                    "role": config["role"],
                    "color": config["color"],
                    "icon": config["icon"],
                    "match_type": "standard_name"
                })
                continue
            
            # 检查昵称
            for nickname in config["nicknames"]:
                if partial_lower in nickname.lower():
                    suggestions.append({
                        "agent_id": agent_id,
                        "display_name": display_name,
                        "role": config["role"],
                        "color": config["color"],
                        "icon": config["icon"],
                        "match_type": "nickname"
                    })
                    break
        
        # 按匹配质量排序（显示名称 > 标准名称 > 昵称）
        suggestions.sort(key=lambda x: {"display_name": 0, "standard_name": 1, "nickname": 2}[x["match_type"]])
        
        return suggestions
    
    def process_message_with_mentions(self, original_message: str) -> Tuple[str, List[Dict]]:
        """处理包含@提及的消息，返回处理后的消息和提及列表"""
        mentions = self.parse_mentions(original_message)
        processed_message = original_message
        
        # 从后往前替换，避免位置偏移问题
        for mention in sorted(mentions, key=lambda x: x["start_pos"], reverse=True):
            # 创建HTML格式的@标签
            mention_tag = f'<span class="mention-tag" data-agent-id="{mention["agent_id"]}" style="color: {self.agents_config[mention["agent_id"]]["color"]}; background-color: {self.agents_config[mention["agent_id"]]["color"]}22; padding: 2px 6px; border-radius: 4px; font-weight: 500;">@{mention["display_name"]}</span>'
            
            # 替换原始文本
            processed_message = (
                processed_message[:mention["start_pos"]] + 
                mention_tag + 
                processed_message[mention["end_pos"]:]
            )
        
        return processed_message, mentions
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Dict]:
        """根据ID获取智能体信息"""
        if agent_id in self.agents_config:
            agent_info = self.agents_config[agent_id].copy()
            agent_info["display_name"] = self.get_agent_display_name(agent_id)
            return agent_info
        return None
    
    def validate_mention(self, agent_id: str) -> bool:
        """验证@提及是否有效"""
        return agent_id in self.agents_config

# 全局实例
mention_parser = MentionParser()

def test_mention_parser():
    """测试@机制解析器"""
    parser = MentionParser()
    
    # 测试自定义名称
    parser.set_custom_name("architect", "架构大师")
    parser.set_custom_name("implementer", "代码高手")
    
    # 测试消息解析
    test_messages = [
        "@架构师 你好，请帮我设计系统架构",
        "@架构大师 这个方案怎么样？",
        "@评估 风险评估如何？",
        "@代码 实现这个功能需要多久？",
        "@数据 收集相关数据"
    ]
    
    for message in test_messages:
        print(f"\n原始消息: {message}")
        processed, mentions = parser.process_message_with_mentions(message)
        print(f"处理后的消息: {processed}")
        print(f"发现的提及: {mentions}")
        
        # 测试建议功能
        if "@" in message:
            partial = message.split("@")[1].split()[0] if " " in message.split("@")[1] else message.split("@")[1]
            suggestions = parser.find_agent_suggestions(partial)
            print(f"建议的智能体: {[s['display_name'] for s in suggestions]}")

if __name__ == "__main__":
    test_mention_parser()