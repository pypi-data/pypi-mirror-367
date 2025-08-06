#!/usr/bin/env python3
"""
CodeCrew Agent Communication System
Handles inter-agent communication and coordination
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages agents can send"""
    STATUS_UPDATE = "status_update"
    TASK_REQUEST = "task_request"
    TASK_COMPLETION = "task_completion"
    BLOCKER_REPORT = "blocker_report"
    COORDINATION_REQUEST = "coordination_request"
    INFORMATION_SHARE = "information_share"

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Message:
    """Inter-agent message"""
    id: str
    from_agent: str
    to_agent: Optional[str]  # None for broadcast messages
    message_type: MessageType
    priority: MessagePriority
    subject: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    read: bool = False
    responded: bool = False

    def __post_init__(self):
        if isinstance(self.message_type, str):
            self.message_type = MessageType(self.message_type)
        if isinstance(self.priority, str):
            self.priority = MessagePriority(self.priority)

class AgentCommunicationHub:
    """Central communication hub for all agents"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.messages_dir = project_path / ".codecrew" / "messages"
        self.messages_dir.mkdir(parents=True, exist_ok=True)
        self.messages_file = self.messages_dir / "messages.json"
        self.messages: Dict[str, Message] = {}
        self._load_messages()
    
    def send_message(self, from_agent: str, to_agent: Optional[str], 
                    message_type: MessageType, priority: MessagePriority,
                    subject: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """Send a message from one agent to another (or broadcast)"""
        
        message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        message = Message(
            id=message_id,
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            priority=priority,
            subject=subject,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now()
        )
        
        self.messages[message_id] = message
        self._save_messages()
        
        logger.info(f"Message sent from {from_agent} to {to_agent or 'ALL'}: {subject}")
        return message_id
    
    def get_messages_for_agent(self, agent_id: str, unread_only: bool = False) -> List[Message]:
        """Get messages for a specific agent"""
        messages = []
        
        for message in self.messages.values():
            # Check if message is for this agent (direct or broadcast)
            if message.to_agent == agent_id or message.to_agent is None:
                if not unread_only or not message.read:
                    messages.append(message)
        
        # Sort by priority and timestamp
        messages.sort(key=lambda m: (m.priority.value, m.timestamp), reverse=True)
        return messages
    
    def mark_message_read(self, message_id: str, agent_id: str) -> bool:
        """Mark a message as read by an agent"""
        if message_id in self.messages:
            message = self.messages[message_id]
            if message.to_agent == agent_id or message.to_agent is None:
                message.read = True
                self._save_messages()
                return True
        return False
    
    def respond_to_message(self, original_message_id: str, from_agent: str,
                          response_content: str, metadata: Dict[str, Any] = None) -> str:
        """Respond to a message"""
        if original_message_id not in self.messages:
            raise ValueError(f"Original message {original_message_id} not found")
        
        original = self.messages[original_message_id]
        
        # Send response back to original sender
        response_id = self.send_message(
            from_agent=from_agent,
            to_agent=original.from_agent,
            message_type=MessageType.INFORMATION_SHARE,
            priority=original.priority,
            subject=f"Re: {original.subject}",
            content=response_content,
            metadata={
                "response_to": original_message_id,
                **(metadata or {})
            }
        )
        
        # Mark original as responded
        original.responded = True
        self._save_messages()
        
        return response_id
    
    def broadcast_status_update(self, from_agent: str, status: str, 
                               current_task: str, progress: float) -> str:
        """Broadcast a status update to all agents"""
        return self.send_message(
            from_agent=from_agent,
            to_agent=None,  # Broadcast
            message_type=MessageType.STATUS_UPDATE,
            priority=MessagePriority.LOW,
            subject=f"Status Update from {from_agent}",
            content=f"Status: {status}\nCurrent Task: {current_task}\nProgress: {progress:.1%}",
            metadata={
                "status": status,
                "current_task": current_task,
                "progress": progress
            }
        )
    
    def report_blocker(self, from_agent: str, blocker_description: str, 
                      severity: str = "medium") -> str:
        """Report a blocker that needs attention"""
        return self.send_message(
            from_agent=from_agent,
            to_agent=None,  # Broadcast to all agents
            message_type=MessageType.BLOCKER_REPORT,
            priority=MessagePriority.HIGH if severity == "high" else MessagePriority.MEDIUM,
            subject=f"Blocker Report from {from_agent}",
            content=f"Blocker: {blocker_description}\nSeverity: {severity}",
            metadata={
                "blocker_description": blocker_description,
                "severity": severity
            }
        )
    
    def request_coordination(self, from_agent: str, coordination_type: str,
                           details: str, target_agents: List[str] = None) -> List[str]:
        """Request coordination with other agents"""
        message_ids = []
        
        if target_agents:
            # Send to specific agents
            for target_agent in target_agents:
                msg_id = self.send_message(
                    from_agent=from_agent,
                    to_agent=target_agent,
                    message_type=MessageType.COORDINATION_REQUEST,
                    priority=MessagePriority.MEDIUM,
                    subject=f"Coordination Request: {coordination_type}",
                    content=details,
                    metadata={
                        "coordination_type": coordination_type,
                        "target_agents": target_agents
                    }
                )
                message_ids.append(msg_id)
        else:
            # Broadcast to all
            msg_id = self.send_message(
                from_agent=from_agent,
                to_agent=None,
                message_type=MessageType.COORDINATION_REQUEST,
                priority=MessagePriority.MEDIUM,
                subject=f"Coordination Request: {coordination_type}",
                content=details,
                metadata={
                    "coordination_type": coordination_type
                }
            )
            message_ids.append(msg_id)
        
        return message_ids
    
    def get_communication_summary(self) -> Dict[str, Any]:
        """Get a summary of communication activity"""
        total_messages = len(self.messages)
        unread_messages = sum(1 for m in self.messages.values() if not m.read)
        
        # Count by type
        type_counts = {}
        for msg_type in MessageType:
            type_counts[msg_type.value] = sum(
                1 for m in self.messages.values() 
                if m.message_type == msg_type
            )
        
        # Count by priority
        priority_counts = {}
        for priority in MessagePriority:
            priority_counts[priority.value] = sum(
                1 for m in self.messages.values() 
                if m.priority == priority
            )
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now().timestamp() - (24 * 60 * 60)
        recent_messages = sum(
            1 for m in self.messages.values() 
            if m.timestamp.timestamp() > recent_cutoff
        )
        
        return {
            "total_messages": total_messages,
            "unread_messages": unread_messages,
            "recent_messages_24h": recent_messages,
            "messages_by_type": type_counts,
            "messages_by_priority": priority_counts
        }
    
    def _load_messages(self):
        """Load messages from file"""
        if not self.messages_file.exists():
            return
        
        try:
            with open(self.messages_file, 'r') as f:
                data = json.load(f)
                for msg_id, msg_data in data.items():
                    msg_data['timestamp'] = datetime.fromisoformat(msg_data['timestamp'])
                    self.messages[msg_id] = Message(**msg_data)
        except Exception as e:
            logger.warning(f"Error loading messages: {e}")
    
    def _save_messages(self):
        """Save messages to file"""
        data = {}
        for msg_id, message in self.messages.items():
            msg_dict = asdict(message)
            msg_dict['message_type'] = msg_dict['message_type'].value
            msg_dict['priority'] = msg_dict['priority'].value
            msg_dict['timestamp'] = msg_dict['timestamp'].isoformat()
            data[msg_id] = msg_dict
        
        with open(self.messages_file, 'w') as f:
            json.dump(data, f, indent=2)

class AgentCommunicator:
    """Communication interface for individual agents"""
    
    def __init__(self, agent_id: str, communication_hub: AgentCommunicationHub):
        self.agent_id = agent_id
        self.hub = communication_hub
    
    def send_status_update(self, status: str, current_task: str, progress: float):
        """Send a status update"""
        return self.hub.broadcast_status_update(
            self.agent_id, status, current_task, progress
        )
    
    def report_blocker(self, description: str, severity: str = "medium"):
        """Report a blocker"""
        return self.hub.report_blocker(self.agent_id, description, severity)
    
    def request_help(self, help_type: str, details: str, target_agents: List[str] = None):
        """Request help from other agents"""
        return self.hub.request_coordination(
            self.agent_id, help_type, details, target_agents
        )
    
    def get_my_messages(self, unread_only: bool = False) -> List[Message]:
        """Get messages for this agent"""
        return self.hub.get_messages_for_agent(self.agent_id, unread_only)
    
    def read_message(self, message_id: str):
        """Mark a message as read"""
        return self.hub.mark_message_read(message_id, self.agent_id)
    
    def respond_to_message(self, message_id: str, response: str, metadata: Dict[str, Any] = None):
        """Respond to a message"""
        return self.hub.respond_to_message(message_id, self.agent_id, response, metadata)
