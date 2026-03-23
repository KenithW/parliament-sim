"""
A* Search Algorithm - A* 搜索算法
用于寻找最优辩论路径和发言顺序
"""

import heapq
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field


@dataclass
class Node:
    """搜索节点"""
    state_id: str                # 状态标识
    speaker: str                 # 当前发言人
    argument_strength: float     # 论点强度 (0~1)
    public_approval_change: float # 对公众支持的改变
    emotional_impact: float      # 情绪影响
    
    def __hash__(self):
        return hash(self.state_id)
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.state_id == other.state_id


@dataclass 
class PathNode(Node):
    """路径节点（包含 A* 信息）"""
    g_score: float = 0.0         # 从起点到当前点的代价
    f_score: float = 0.0         # g_score + h_score (总估计代价)
    parent: Optional['PathNode'] = None
    
    def __lt__(self, other):
        return self.f_score < other.f_score


class ASTarSearch:
    """
    A* 搜索算法实现
    
    应用场景：
    - 找到最优的发言顺序组合
    - 选择最佳的论证策略
    - 规划最有效的辩论路径
    """
    
    def __init__(self):
        self.open_set: List[PathNode] = []
        self.came_from: Dict[Node, Optional[PathNode]] = {}
        self.g_score_map: Dict[Node, float] = {}
        self.f_score_map: Dict[Node, float] = {}
        self.closed_set: Set[Node] = set()
        
        self.all_nodes: Dict[str, Node] = {}
        
    def add_state(
        self, 
        state_id: str,
        speaker: str,
        argument_strength: float,
        public_approval_change: float,
        emotional_impact: float
    ):
        """添加一个可能的状态节点"""
        node = Node(
            state_id=state_id,
            speaker=speaker,
            argument_strength=argument_strength,
            public_approval_change=public_approval_change,
            emotional_impact=emotional_impact
        )
        self.all_nodes[state_id] = node
        
    def heuristic(self, current: Node, goal: str) -> float:
        """
        启发函数：估计从当前节点到目标的最小代价
        
        Args:
            current: 当前节点
            goal: 目标状态 ID
        
        Returns:
            估计代价
        """
        # 简单启发式：基于剩余需要获得的公众支持度
        remaining_approval = 1.0 - self._get_total_approval(goal)
        return max(0, remaining_approval * 2)  # 放大权重
    
    def _get_total_approval(self, goal_id: str) -> float:
        """计算到达某个状态的累积公众支持变化"""
        total = 0.0
        current = goal_id
        
        while current in self.all_nodes:
            node = self.all_nodes[current]
            total += node.public_approval_change
            
            # 简化逻辑，实际应该追踪完整路径
            break
        
        return total
    
    def reconstruct_path(self, current: PathNode) -> List[PathNode]:
        """重构从起点到终点的路径"""
        total_path = [current]
        while current.parent is not None:
            current = current.parent
            total_path.append(current)
        total_path.reverse()
        return total_path
    
    def astar_search(
        self,
        start_id: str,
        goal_ids: List[str],
        max_turns: int = 10
    ) -> Optional[List[Node]]:
        """
        A* 搜索最优路径
        
        Args:
            start_id: 起始状态 ID
            goal_ids: 可选的目标状态列表
            max_turns: 最大轮数限制
        
        Returns:
            最佳路径或 None
        """
        # 初始化
        start_node = self.all_nodes[start_id]
        start_path = PathNode(
            state_id=start_node.state_id,
            speaker=start_node.speaker,
            argument_strength=start_node.argument_strength,
            public_approval_change=start_node.public_approval_change,
            emotional_impact=start_node.emotional_impact
        )
        
        start_path.g_score = 0
        start_path.f_score = self.heuristic(start_node, goal_ids[0])
        
        heapq.heappush(self.open_set, start_path)
        self.g_score_map[start_node] = 0
        self.f_score_map[start_node] = start_path.f_score
        
        print(f"[A*] 开始搜索，起点={start_id}")
        print(f"[A*] 目标状态：{len(goal_ids)}个候选")
        
        iteration = 0
        
        while self.open_set:
            iteration += 1
            
            # 取出 f_score 最小的节点
            current_path = heapq.heappop(self.open_set)
            current_node = self.all_nodes[current_path.state_id]
            
            # 检查是否达到目标
            if current_path.state_id in goal_ids:
                path = self.reconstruct_path(current_path)
                nodes = [n for n in path]
                
                print(f"\n[A*] 找到最优路径！迭代次数={iteration}")
                print(f"[A*] 路径长度：{len(nodes)}步\n")
                
                for i, node in enumerate(nodes):
                    print(f"  [{i}] {node.speaker}: "
                          f"强度={node.argument_strength:.2f}, "
                          f"支持率变化={node.public_approval_change:+.3f}")
                
                return nodes
            
            # 检查是否超过最大轮数
            if len(self.reconstruct_path(current_path)) > max_turns:
                continue
            
            # 标记为已访问
            self.closed_set.add(current_node)
            
            # 生成后继节点
            successors = self._get_successors(current_node)
            
            for successor in successors:
                if successor in self.closed_set:
                    continue
                
                # 计算临时 g 分数
                tentative_g = self.g_score_map.get(current_node, float('inf')) + \
                             abs(successor.public_approval_change)
                
                # 如果找到更好路径或首次访问
                if successor not in [n for n in self.g_score_map.keys()]:
                    self.g_score_map[successor] = float('inf')
                
                if tentative_g < self.g_score_map[successor]:
                    # 更新距离
                    self.g_score_map[successor] = tentative_g
                    self.f_score_map[successor] = tentative_g + \
                                                  self.heuristic(successor, goal_ids[0])
                    
                    # 添加到优先队列
                    successor_path = PathNode(
                        state_id=successor.state_id,
                        speaker=successor.speaker,
                        argument_strength=successor.argument_strength,
                        public_approval_change=successor.public_approval_change,
                        emotional_impact=successor.emotional_impact,
                        parent=current_path
                    )
                    heapq.heappush(self.open_set, successor_path)
            
            if iteration % 5 == 0:
                print(f"[A*] 已处理 {iteration} 个节点，open_set 大小：{len(self.open_set)}")
        
        print("[A*] 未找到有效路径")
        return None
    
    def _get_successors(self, current: Node) -> List[Node]:
        """
        获取当前节点的后继状态
        
        这在实际应用中应该更智能
        这里我们随机生成一些可能的下一步
        """
        candidates = list(self.all_nodes.values())
        
        # 过滤掉已经访问过的
        available = [n for n in candidates if n != current]
        
        # 返回最多 3 个可能后继
        return random.sample(available, min(3, len(available)))


def generate_debate_states(num_speakers: int = 6, num_options_per_speaker: int = 3) -> ASTarSearch:
    """
    生成辩论状态空间示例
    
    Args:
        num_speakers: 演讲者数量
        num_options_per_speaker: 每个演讲者的策略选项数
    
    Returns:
        填充好状态空间的搜索器
    """
    search = ASTarSearch()
    
    speakers = ["PM", "LO", "Chancellor", "Shadow Chancellor", "Backbencher1", "Backbencher2"]
    
    # 生成所有可能的状态组合
    import itertools
    from random import uniform, randint
    
    state_counter = 0
    
    for speaker_idx in range(num_speakers):
        speaker = speakers[speaker_idx]
        
        for option_idx in range(num_options_per_speaker):
            state_id = f"{speaker}_opt{option_idx}"
            
            # 模拟不同策略的效果
            arg_strength = uniform(0.5, 1.0)
            approval_change = uniform(-0.1, 0.2)
            emotional_impact = uniform(0.3, 0.9)
            
            search.add_state(
                state_id=state_id,
                speaker=speaker,
                argument_strength=arg_strength,
                public_approval_change=approval_change,
                emotional_impact=emotional_impact
            )
            state_counter += 1
    
    # 定义起始和目标状态
    start_state = f"{speakers[0]}_opt0"
    goal_states = [f"{speakers[-1]}_opt{i}" for i in range(num_options_per_speaker)]
    
    print(f"[A*] 生成了 {state_counter} 个状态节点")
    print(f"[A*] 起始状态：{start_state}")
    print(f"[A*] 目标状态范围：{len(goal_states)}个")
    
    return search, start_state, goal_states


if __name__ == "__main__":
    import random
    
    print("=" * 60)
    print("A* SEARCH TEST - Optimal Debate Path Finding")
    print("=" * 60)
    
    # 生成状态空间
    search, start, goals = generate_debate_states(num_speakers=5, num_options_per_speaker=3)
    
    # 运行 A* 搜索
    best_path = search.astar_search(start, goals, max_turns=8)
    
    if best_path:
        print("\n" + "=" * 60)
        print("🎯 OPTIMAL DEBATE STRATEGY:")
        print("=" * 60)
        
        total_approval = sum(n.public_approval_change for n in best_path)
        avg_strength = sum(n.argument_strength for n in best_path) / len(best_path)
        
        print(f"  Total Public Approval Change: {total_approval:+.3f}")
        print(f"  Average Argument Strength: {avg_strength:.3f}")
        print(f"  Recommended Strategy:")
        print(f"  1. Follow this exact speaking order")
        print(f"  2. Each speaker should choose the indicated option")
    
    print("=" * 60)
