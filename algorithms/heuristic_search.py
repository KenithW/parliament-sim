"""
Heuristic Search - 启发式搜索
用于实时决策和快速策略选择
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import heapq


@dataclass
class DecisionNode:
    """决策树节点"""
    strategy: str                       # 策略名称
    estimated_success: float           # 预估成功率 (0~1)
    resource_cost: float               # 资源消耗
    time_cost: int                     # 时间成本
    children: List['DecisionNode'] = None
    
    def __lt__(self, other):
        return self.estimated_success < other.estimated_success


class HeuristicSearchEngine:
    """
    启发式搜索引擎
    
    应用场景：
    - 实时辩论应对
    - 快速策略评估
    - 动态调整发言内容
    
    核心思想：使用启发式函数快速评估和剪枝
    """
    
    def __init__(self):
        self.search_tree: Optional[DecisionNode] = None
        
        # 启发式函数权重
        self.weights = {
            'success': 0.4,      # 成功率权重
            'efficiency': 0.3,   # 效率权重
            'impact': 0.2,       # 影响力权重
            'risk': 0.1          # 风险惩罚
        }
    
    def build_decision_tree(
        self,
        current_context: Dict,
        max_depth: int = 5
    ) -> DecisionNode:
        """
        构建决策树
        
        Args:
            current_context: 当前辩论上下文
            max_depth: 最大搜索深度
        
        Returns:
            根节点
        """
        print(f"[HS] Building decision tree, depth={max_depth}")
        
        # 定义可用策略库
        strategies = self._get_available_strategies(current_context)
        
        # 创建根节点（代表"什么都不做"）
        root = DecisionNode(
            strategy="observe",
            estimated_success=0.5,
            resource_cost=0,
            time_cost=0,
            children=strategies
        )
        
        # 扩展子节点（如果还有深度）
        if max_depth > 1 and root.children:
            for child in root.children:
                child.children = self._expand_node(child, max_depth - 1)
        
        self.search_tree = root
        return root
    
    def _get_available_strategies(self, context: Dict) -> List[DecisionNode]:
        """根据当前上下文获取可用策略"""
        my_role = context.get('my_role', 'PM')
        opponent_strength = context.get('opponent_strength', 0.5)
        public_approval = context.get('public_approval', 50)
        
        # 根据情况过滤策略
        strategies = []
        
        if opponent_strength < 0.4:
            strategies.append(DecisionNode(
                strategy="aggressive_attack",
                estimated_success=0.7,
                resource_cost=0.2,
                time_cost=1
            ))
        
        if opponent_strength > 0.6:
            strategies.append(DecisionNode(
                strategy="defensive_counter",
                estimated_success=0.6,
                resource_cost=0.1,
                time_cost=1
            ))
        
        # 始终可用的策略
        strategies.extend([
            DecisionNode(
                strategy="moderate_response",
                estimated_success=0.55,
                resource_cost=0.1,
                time_cost=1
            ),
            DecisionNode(
                strategy="redirect_focus",
                estimated_success=0.5,
                resource_cost=0.15,
                time_cost=2
            ),
            DecisionNode(
                strategy="appeal_to_emotion",
                estimated_success=0.45,
                resource_cost=0.25,
                time_cost=1
            ),
        ])
        
        return strategies
    
    def _expand_node(self, node: DecisionNode, remaining_depth: int) -> List[DecisionNode]:
        """扩展一个节点"""
        if remaining_depth <= 0 or node.strategy == "end":
            return [DecisionNode(
                strategy="end",
                estimated_success=0,
                resource_cost=0,
                time_cost=0
            )]
        
        # 生成可能的下一步
        next_actions = ["attack", "defend", "question", "concede"]
        children = []
        
        for action in next_actions:
            success_prob = self._estimate_success(node, action)
            
            children.append(DecisionNode(
                strategy=f"{node.strategy}_{action}",
                estimated_success=success_prob,
                resource_cost=node.resource_cost + 0.1,
                time_cost=node.time_cost + 1
            ))
        
        return children
    
    def _estimate_success(self, parent: DecisionNode, action: str) -> float:
        """估算某个行动的成功率"""
        base_rate = 0.5
        
        if action == "attack" and parent.strategy.startswith("aggressive"):
            return base_rate + 0.2
        elif action == "defend" and parent.strategy.startswith("defensive"):
            return base_rate + 0.15
        elif action == "concede" and parent.estimated_success < 0.4:
            return base_rate - 0.1
        else:
            return base_rate + random.uniform(-0.1, 0.1)
    
    def evaluate_strategy(self, node: DecisionNode) -> float:
        """
        使用启发式函数评估策略
        
        H(s) = w1*success + w2*efficiency - w3*risk
        """
        # 成功率得分
        success_score = node.estimated_success * 100
        
        # 效率得分（成本越低越好）
        efficiency_score = (1 - node.resource_cost) * 50
        
        # 影响力得分（基于角色和时机）
        impact_score = 30 if node.time_cost < 2 else 20
        
        # 风险评估（简单处理）
        risk_penalty = node.resource_cost * 20
        
        # 综合评分
        score = (
            self.weights['success'] * success_score +
            self.weights['efficiency'] * efficiency_score +
            self.weights['impact'] * impact_score -
            risk_penalty
        )
        
        return score
    
    def find_best_strategy(
        self,
        root: DecisionNode,
        method: str = "beam_search"
    ) -> Tuple[str, float]:
        """
        找到最佳策略
        
        Args:
            root: 决策树根节点
            method: 搜索方法 ("beam_search", "dfs", "greedy")
        
        Returns:
            (最佳策略名称，评分)
        """
        print(f"\n[HS] Finding best strategy using {method}...")
        
        if method == "greedy":
            return self._greedy_search(root)
        elif method == "beam_search":
            return self._beam_search(root, beam_width=3)
        elif method == "dfs":
            return self._dfs_search(root)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _greedy_search(self, root: DecisionNode) -> Tuple[str, float]:
        """贪婪搜索 - 每一步选局部最优"""
        current = root
        path = [current.strategy]
        
        while current.children:
            # 选择子节点中评估最高的
            best_child = max(
                current.children,
                key=lambda c: self.evaluate_strategy(c)
            )
            path.append(best_child.strategy)
            current = best_child
        
        final_score = self.evaluate_strategy(current)
        
        print(f"[HS] Greedy path: {' -> '.join(path)}")
        print(f"[HS] Final score: {final_score:.2f}")
        
        return current.strategy, final_score
    
    def _beam_search(
        self,
        root: DecisionNode,
        beam_width: int = 3
    ) -> Tuple[str, float]:
        """束搜索 - 保留多个候选路径"""
        # 初始化：每个子节点作为一个独立路径
        beams = [(child, [root.strategy, child.strategy]) 
                for child in root.children[:beam_width]]
        
        for depth in range(2, 5):  # 最多搜索到第 4 层
            new_beams = []
            
            for path_node, path in beams:
                if path_node.children:
                    for child in path_node.children:
                        score = self.evaluate_strategy(child)
                        new_beams.append((child, path + [child.strategy]))
            
            # 按分数排序并保留前 beam_width 个
            new_beams.sort(key=lambda x: self.evaluate_strategy(x[0]), reverse=True)
            beams = new_beams[:beam_width]
            
            if not beams:
                break
        
        # 选择最终最佳
        best_beam = max(beams, key=lambda x: self.evaluate_strategy(x[0]))
        
        print(f"[HS] Beam search complete. Top paths:")
        for i, (node, path) in enumerate(beams[:3]):
            score = self.evaluate_strategy(node)
            print(f"  {i+1}. {' -> '.join(path)} (score: {score:.2f})")
        
        return best_beam[0].strategy, self.evaluate_strategy(best_beam[0])
    
    def _dfs_search(self, root: DecisionNode) -> Tuple[str, float]:
        """深度优先搜索 - 探索所有路径"""
        best_score = -float('inf')
        best_strategy = root.strategy
        best_path = [root.strategy]
        
        def dfs(node: DecisionNode, path: List[str]):
            nonlocal best_score, best_strategy
            
            score = self.evaluate_strategy(node)
            
            if score > best_score:
                best_score = score
                best_strategy = node.strategy
                best_path = path.copy()
            
            if node.children:
                for child in node.children:
                    dfs(child, path + [child.strategy])
        
        dfs(root, [root.strategy])
        
        print(f"[HS] DFS explored all paths. Best: {' -> '.join(best_path)}")
        print(f"[HS] Score: {best_score:.2f}")
        
        return best_strategy, best_score
    
    def real_time_recommendation(
        self,
        opponent_move: str,
        context: Dict
    ) -> Dict:
        """
        实时推荐建议
        
        Args:
            opponent_move: 对手的最新动作
            context: 当前辩论上下文
        
        Returns:
            推荐结果字典
        """
        print("\n" + "=" * 60)
        print("REAL-TIME RECOMMENDATION ENGINE")
        print("=" * 60)
        
        # 更新上下文
        context['opponent_last_move'] = opponent_move
        
        # 构建决策树
        root = self.build_decision_tree(context, max_depth=3)
        
        # 找到最佳策略
        best_strategy, score = self.find_best_strategy(root, method="beam_search")
        
        # 生成建议
        recommendation = {
            "recommended_strategy": best_strategy,
            "confidence_score": score,
            "reasoning": self._generate_reasoning(best_strategy, context),
            "estimated_impact": self._estimate_impact(best_strategy)
        }
        
        print("\n🎯 RECOMMENDATION:")
        for key, value in recommendation.items():
            print(f"  {key}: {value}")
        
        return recommendation
    
    def _generate_reasoning(self, strategy: str, context: Dict) -> str:
        """为推荐生成理由"""
        reasoning_parts = []
        
        if "attack" in strategy:
            reasoning_parts.append("Your opponent has shown vulnerability")
        if "defend" in strategy:
            reasoning_parts.append("Opponent's previous attack was strong")
        if "redirect" in strategy:
            reasoning_parts.append("Current topic is unfavorable")
        if "emotional" in strategy:
            reasoning_parts.append("Appeal to emotion could sway undecided voters")
        
        return "; ".join(reasoning_parts) if reasoning_parts else "Balanced approach recommended"
    
    def _estimate_impact(self, strategy: str) -> str:
        """估计策略影响"""
        impacts = {
            "attack": "High risk, high reward",
            "defend": "Stabilizes position",
            "redirect": "Changes debate focus",
            "emotional": "Increases engagement but may seem manipulative",
            "default": "Safe incremental gain"
        }
        
        for key, value in impacts.items():
            if key in strategy.lower():
                return value
        
        return impacts["default"]


# ======================
# 测试
# ======================
if __name__ == "__main__":
    from random import uniform
    
    print("=" * 60)
    print("HEURISTIC SEARCH TEST")
    print("=" * 60)
    
    engine = HeuristicSearchEngine()
    
    # 模拟几个场景
    scenarios = [
        {
            "role": "PM",
            "opponent_strength": 0.6,
            "public_approval": 48,
            "opponent_move": "attack_economy"
        },
        {
            "role": "LO",
            "opponent_strength": 0.4,
            "public_approval": 52,
            "opponent_move": "defend_healthcare"
        }
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\n{'='*60}")
        print(f"SCENARIO {i+1}: {scenario['role']} vs opponent strength={scenario['opponent_strength']}")
        print('='*60)
        
        result = engine.real_time_recommendation(scenario['opponent_move'], scenario)
