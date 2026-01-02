# @self-expose: {"id": "agent_feedback_collector", "name": "Agent Feedback Collector", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Agent Feedback Collector功能"]}}
import json
import uuid
from datetime import datetime
import os
import logging

# 配置日志
logging.basicConfig(
    filename='logs/agent_feedback.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

class AgentFeedbackCollector:
    """
    智能体反馈收集器，用于收集智能体对工具的反馈和优化建议
    """
    
    def __init__(self, feedback_file="data/agent_feedback.json"):
        """
        初始化反馈收集器
        
        Args:
            feedback_file: 反馈数据保存的文件路径
        """
        self.feedback_file = feedback_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """
        确保反馈文件存在，不存在则创建
        """
        os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def collect_feedback(self, agent_id, agent_type, tool_name, feedback_type, content, priority="medium"):
        """
        收集智能体反馈
        
        Args:
            agent_id: 智能体ID
            agent_type: 智能体类型
            tool_name: 工具名称
            feedback_type: 反馈类型（使用体验、功能优化、新功能需求、问题报告）
            content: 反馈内容
            priority: 优先级（low, medium, high）
            
        Returns:
            dict: 包含反馈ID和状态的字典
        """
        # 验证反馈类型
        valid_feedback_types = ["使用体验", "功能优化", "新功能需求", "问题报告"]
        if feedback_type not in valid_feedback_types:
            logger.warning(f"无效的反馈类型: {feedback_type}")
            return {"status": "error", "message": f"无效的反馈类型，必须是: {', '.join(valid_feedback_types)}"}
        
        # 验证优先级
        valid_priorities = ["low", "medium", "high"]
        if priority not in valid_priorities:
            logger.warning(f"无效的优先级: {priority}")
            return {"status": "error", "message": f"无效的优先级，必须是: {', '.join(valid_priorities)}"}
        
        # 创建反馈记录
        feedback = {
            "id": f"feedback_{uuid.uuid4()}",
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "agent_type": agent_type,
            "tool_name": tool_name,
            "feedback_type": feedback_type,
            "content": content,
            "priority": priority,
            "status": "pending",
            "evaluation_result": None,
            "processed_by": None,
            "processed_at": None
        }
        
        # 保存反馈
        try:
            with open(self.feedback_file, 'r+', encoding='utf-8') as f:
                feedbacks = json.load(f)
                feedbacks.append(feedback)
                f.seek(0)
                json.dump(feedbacks, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功收集反馈: {feedback['id']}，工具: {tool_name}，类型: {feedback_type}")
            return {"status": "success", "feedback_id": feedback["id"]}
        except Exception as e:
            logger.error(f"保存反馈失败: {e}")
            return {"status": "error", "message": f"保存反馈失败: {str(e)}"}
    
    def get_feedback(self, feedback_id):
        """
        根据ID获取反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            dict: 反馈信息，不存在则返回None
        """
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
                for feedback in feedbacks:
                    if feedback["id"] == feedback_id:
                        return feedback
            return None
        except Exception as e:
            logger.error(f"获取反馈失败: {e}")
            return None
    
    def get_all_feedbacks(self, status=None, tool_name=None, feedback_type=None):
        """
        获取所有反馈，支持过滤
        
        Args:
            status: 反馈状态过滤
            tool_name: 工具名称过滤
            feedback_type: 反馈类型过滤
            
        Returns:
            list: 过滤后的反馈列表
        """
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
            
            # 应用过滤条件
            if status:
                feedbacks = [f for f in feedbacks if f["status"] == status]
            if tool_name:
                feedbacks = [f for f in feedbacks if f["tool_name"] == tool_name]
            if feedback_type:
                feedbacks = [f for f in feedbacks if f["feedback_type"] == feedback_type]
            
            return feedbacks
        except Exception as e:
            logger.error(f"获取反馈列表失败: {e}")
            return []
    
    def update_feedback_status(self, feedback_id, status, evaluation_result=None, processed_by=None):
        """
        更新反馈状态
        
        Args:
            feedback_id: 反馈ID
            status: 新状态
            evaluation_result: 评估结果
            processed_by: 处理者
            
        Returns:
            bool: 更新是否成功
        """
        try:
            with open(self.feedback_file, 'r+', encoding='utf-8') as f:
                feedbacks = json.load(f)
                updated = False
                for feedback in feedbacks:
                    if feedback["id"] == feedback_id:
                        feedback["status"] = status
                        if evaluation_result:
                            feedback["evaluation_result"] = evaluation_result
                        if processed_by:
                            feedback["processed_by"] = processed_by
                            feedback["processed_at"] = datetime.now().isoformat()
                        updated = True
                        break
                
                if updated:
                    f.seek(0)
                    f.truncate()
                    json.dump(feedbacks, f, ensure_ascii=False, indent=2)
                    logger.info(f"更新反馈状态: {feedback_id} -> {status}")
                    return True
                else:
                    logger.warning(f"未找到反馈: {feedback_id}")
                    return False
        except Exception as e:
            logger.error(f"更新反馈状态失败: {e}")
            return False
    
    def delete_feedback(self, feedback_id):
        """
        删除反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            with open(self.feedback_file, 'r+', encoding='utf-8') as f:
                feedbacks = json.load(f)
                original_length = len(feedbacks)
                feedbacks = [f for f in feedbacks if f["id"] != feedback_id]
                
                if len(feedbacks) < original_length:
                    f.seek(0)
                    f.truncate()
                    json.dump(feedbacks, f, ensure_ascii=False, indent=2)
                    logger.info(f"删除反馈: {feedback_id}")
                    return True
                else:
                    logger.warning(f"未找到反馈: {feedback_id}")
                    return False
        except Exception as e:
            logger.error(f"删除反馈失败: {e}")
            return False

# 命令行测试支持
if __name__ == "__main__":
    import sys
    
    # 简单的命令行测试
    collector = AgentFeedbackCollector()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python agent_feedback_collector.py collect <agent_id> <agent_type> <tool_name> <feedback_type> <content> [priority]")
        print("  python agent_feedback_collector.py list [status] [tool_name] [feedback_type]")
        print("  python agent_feedback_collector.py get <feedback_id>")
        print("  python agent_feedback_collector.py update <feedback_id> <status> [evaluation_result] [processed_by]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "collect":
        if len(sys.argv) < 7:
            print("参数不足: python agent_feedback_collector.py collect <agent_id> <agent_type> <tool_name> <feedback_type> <content> [priority]")
            sys.exit(1)
        
        agent_id = sys.argv[2]
        agent_type = sys.argv[3]
        tool_name = sys.argv[4]
        feedback_type = sys.argv[5]
        content = sys.argv[6]
        priority = sys.argv[7] if len(sys.argv) > 7 else "medium"
        
        result = collector.collect_feedback(agent_id, agent_type, tool_name, feedback_type, content, priority)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "list":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        tool_name = sys.argv[3] if len(sys.argv) > 3 else None
        feedback_type = sys.argv[4] if len(sys.argv) > 4 else None
        
        feedbacks = collector.get_all_feedbacks(status, tool_name, feedback_type)
        print(json.dumps(feedbacks, ensure_ascii=False, indent=2))
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("参数不足: python agent_feedback_collector.py get <feedback_id>")
            sys.exit(1)
        
        feedback_id = sys.argv[2]
        feedback = collector.get_feedback(feedback_id)
        if feedback:
            print(json.dumps(feedback, ensure_ascii=False, indent=2))
        else:
            print(f"未找到反馈: {feedback_id}")
    
    elif command == "update":
        if len(sys.argv) < 4:
            print("参数不足: python agent_feedback_collector.py update <feedback_id> <status> [evaluation_result] [processed_by]")
            sys.exit(1)
        
        feedback_id = sys.argv[2]
        status = sys.argv[3]
        evaluation_result = sys.argv[4] if len(sys.argv) > 4 else None
        processed_by = sys.argv[5] if len(sys.argv) > 5 else None
        
        result = collector.update_feedback_status(feedback_id, status, evaluation_result, processed_by)
        print(f"更新结果: {'成功' if result else '失败'}")
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
