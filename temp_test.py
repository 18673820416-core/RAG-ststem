# @self-expose: {"id": "temp_test", "name": "Temp Test", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Temp Test功能"]}}
from src.system_maintenance_agent import get_system_maintenance
agent = get_system_maintenance()
print('✅ 系统维护师智能体加载成功')
health = agent.monitor_system_health()
print(f'健康巡检: {health["overall_status"]}')