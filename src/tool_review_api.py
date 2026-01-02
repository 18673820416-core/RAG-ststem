#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具审核API接口 - 提供工具审核相关的Web API
开发提示词来源：用户要求发现的工具需上报用户审核后才能关联到注册表
"""

# @self-expose: {"id": "tool_review_api", "name": "Tool Review Api", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Tool Review Api功能"]}}

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

tool_review_bp = Blueprint('tool_review', __name__)

@tool_review_bp.route('/api/tool_review/pending', methods=['GET'])
def get_pending_tools():
    """获取所有待审核工具"""
    try:
        from tool_review_manager import get_tool_review_manager
        
        review_manager = get_tool_review_manager()
        pending_tools = review_manager.get_pending_tools()
        
        return jsonify({
            'success': True,
            'pending_tools': pending_tools,
            'count': len(pending_tools)
        })
        
    except Exception as e:
        logger.error(f"获取待审核工具失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tool_review_bp.route('/api/tool_review/pending/<tool_id>', methods=['GET'])
def get_pending_tool_detail(tool_id: str):
    """获取指定待审核工具的详细信息"""
    try:
        from tool_review_manager import get_tool_review_manager
        
        review_manager = get_tool_review_manager()
        tool_info = review_manager.get_tool_for_review(tool_id)
        
        if not tool_info:
            return jsonify({
                'success': False,
                'error': f'工具 {tool_id} 不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'tool_info': tool_info
        })
        
    except Exception as e:
        logger.error(f"获取工具详情失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tool_review_bp.route('/api/tool_review/approve/<tool_id>', methods=['POST'])
def approve_tool(tool_id: str):
    """审核通过工具"""
    try:
        data = request.get_json() or {}
        reviewer = data.get('reviewer', 'user')
        review_notes = data.get('review_notes', '审核通过')
        
        from tool_review_manager import get_tool_review_manager
        
        review_manager = get_tool_review_manager()
        success = review_manager.approve_tool(tool_id, reviewer, review_notes)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'工具 {tool_id} 审核通过'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'审核工具 {tool_id} 失败'
            }), 400
        
    except Exception as e:
        logger.error(f"审核通过工具失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tool_review_bp.route('/api/tool_review/reject/<tool_id>', methods=['POST'])
def reject_tool(tool_id: str):
    """审核拒绝工具"""
    try:
        data = request.get_json() or {}
        reviewer = data.get('reviewer', 'user')
        review_notes = data.get('review_notes', '审核未通过')
        
        from tool_review_manager import get_tool_review_manager
        
        review_manager = get_tool_review_manager()
        success = review_manager.reject_tool(tool_id, reviewer, review_notes)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'工具 {tool_id} 审核拒绝'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'审核拒绝工具 {tool_id} 失败'
            }), 400
        
    except Exception as e:
        logger.error(f"审核拒绝工具失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tool_review_bp.route('/api/tool_review/statistics', methods=['GET'])
def get_review_statistics():
    """获取审核统计信息"""
    try:
        from tool_review_manager import get_tool_review_manager
        
        review_manager = get_tool_review_manager()
        statistics = review_manager.get_review_statistics()
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
    except Exception as e:
        logger.error(f"获取审核统计信息失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tool_review_bp.route('/api/tool_review/discover', methods=['POST'])
def trigger_tool_discovery():
    """触发工具发现流程"""
    try:
        from agent_discovery_engine import get_agent_discovery_engine
        
        discovery_engine = get_agent_discovery_engine()
        
        # 触发工具发现
        discovered_tools = discovery_engine.discover_tools()
        
        # 检查是否返回了错误信息（功能未实现）
        if "error" in discovered_tools:
            logger.warning(f"工具发现功能未实现: {discovered_tools['message']}")
            return jsonify({
                'success': False,
                'error': discovered_tools['message'],
                'message': '工具发现功能当前未实现，请等待后续开发'
            }), 501  # 501表示未实现
        
        return jsonify({
            'success': True,
            'message': f'发现 {len(discovered_tools)} 个工具',
            'discovered_tools': discovered_tools
        })
        
    except Exception as e:
        logger.error(f"触发工具发现失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tool_review_bp.route('/api/tool_review/status', methods=['GET'])
def get_review_system_status():
    """获取审核系统状态"""
    try:
        from tool_review_manager import get_tool_review_manager
        from tool_registry_manager import get_tool_registry_manager
        
        review_manager = get_tool_review_manager()
        registry_manager = get_tool_registry_manager()
        
        review_stats = review_manager.get_review_statistics()
        registry_stats = registry_manager.get_registry_statistics()
        
        return jsonify({
            'success': True,
            'system_status': {
                'review_system': 'active',
                'registry_system': 'active',
                'pending_tools': review_stats['pending_tools_count'],
                'total_registered_tools': registry_stats['total_tools'],
                'approval_rate': review_stats['approval_rate']
            }
        })
        
    except Exception as e:
        logger.error(f"获取审核系统状态失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500