"""
Genetic Algorithm - 遗传算法
用于进化政策立场和辩论策略
"""

import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Chromosome:
    """染色体 - 代表一个策略组合"""
    policy_values: List[float]       # 政策立场值 (0~1)
    rhetorical_style: int            # 修辞风格编码
    emotional_intensity: float       # 情绪强度
    fitness_score: float = 0.0       # 适应度得分
    
    def encode(self) -> str:
        """编码为字符串"""
        return f"{self.policy_values}_{self.rhetorical_style}_{self.emotional_intensity}"


class GeneticAlgorithm:
    """
    遗传算法引擎
    
    应用场景：
    - 进化执政党的政策立场
    - 优化辩论策略组合
    - 发现最优的演讲模式
    """
    
    def __init__(
        self,
        population_size: int = 50,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        generations: int = 20
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generations = generations
        
        self.population: List[Chromosome] = []
        self.best_solution: Optional[Chromosome] = None
        
    def initialize_population(self) -> List[Chromosome]:
        """初始化种群"""
        print(f"[GA] 初始化种群，大小={self.population_size}")
        
        self.population = [
            Chromosome(
                policy_values=[random.random() for _ in range(5)],  # 5 个政策维度
                rhetorical_style=random.randint(0, 2),               # 3 种风格
                emotional_intensity=random.uniform(0, 1)             # 情绪强度
            )
            for _ in range(self.population_size)
        ]
        
        return self.population
    
    def calculate_fitness(self, chromosome: Chromette) -> float:
        """
        计算适应度
        
        评估标准：
        - 政策吸引力（公众支持）
        - 政治可行性（通过可能性）
        - 一致性（与政党立场匹配）
        - 创新度（避免陈旧）
        """
        # 模拟评估函数
        base_score = sum(chromosome.policy_values) / len(chromosome.policy_values)
        
        style_bonus = {
            0: "conservative",   # 保守
            1: "progressive",    # 进步
            2: "compromise"      # 妥协
        }.get(chromosome.rhetorical_style, 0.5)
        
        emotion_penalty = abs(chromosome.emotional_intensity - 0.6) * 0.2
        
        fitness = base_score * 0.4 + style_bonus * 0.3 + (1 - emotion_penalty) * 0.3
        
        chromosome.fitness_score = fitness
        return fitness
    
    def calculate_all_fitness(self):
        """计算整个种群的适应度"""
        for chrom in self.population:
            self.calculate_fitness(chrom)
    
    def select_parents(self, k: int = 3) -> List[Chromosome]:
        """
        锦标赛选择
        
        Args:
            k: 参赛个体数
    
        Returns:
            选中的父代
        """
        tournament = random.sample(self.population, k)
        return max(tournament, key=lambda c: c.fitness_score)
    
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Chromosome:
        """
        单点交叉
        
        Args:
            parent1, parent2: 两个父代
        
        Returns:
            子代染色体
        """
        # 随机交叉点
        point = random.randint(1, len(parent1.policy_values) - 1)
        
        # 交叉政策值
        child_policy = (
            parent1.policy_values[:point] + 
            parent2.policy_values[point:]
        )
        
        # 混合其他特征
        child_rhetorical = random.choice([parent1.rhetorical_style, 
                                           parent2.rhetorical_style])
        child_emotion = (parent1.emotional_intensity + 
                        parent2.emotional_intensity) / 2
        
        return Chromosome(
            policy_values=child_policy,
            rhetorical_style=child_rhetorical,
            emotional_intensity=child_emotion
        )
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        变异操作
        
        - 政策值微调
        - 修辞风格突变
        - 情绪强度调整
        """
        # 复制染色体
        child = Chromosome(
            policy_values=chromosome.policy_values.copy(),
            rhetorical_style=chromosome.rhetorical_style,
            emotional_intensity=chromosome.emotional_intensity
        )
        
        # 政策值变异 (高斯噪声)
        for i in range(len(child.policy_values)):
            if random.random() < self.mutation_rate:
                child.policy_values[i] += random.gauss(0, 0.1)
                child.policy_values[i] = max(0, min(1, child.policy_values[i]))
        
        # 修辞风格突变
        if random.random() < self.mutation_rate:
            child.rhetorical_style = random.randint(0, 2)
        
        # 情绪强度变异
        if random.random() < self.mutation_rate:
            child.emotional_intensity += random.uniform(-0.2, 0.2)
            child.emotional_intensity = max(0, min(1, child.emotional_intensity))
        
        return child
    
    def evolve(self) -> Chromosome:
        """
        执行一次完整演化
        
        Returns:
            最佳解决方案
        """
        print(f"\n[GA] 开始演化，代数={self.generations}")
        
        # 初始化
        self.initialize_population()
        self.calculate_all_fitness()
        
        best_chromosome = max(self.population, key=lambda c: c.fitness_score)
        self.best_solution = best_chromosome
        
        history = []
        
        for generation in range(self.generations):
            print(f"\n  【第{generation+1}代】")
            
            # 创建新一代
            new_population = []
            
            # 精英保留（前 2 名直接晋级）
            elite = sorted(self.population, key=lambda c: c.fitness_score)[:2]
            new_population.extend(elite)
            
            # 繁殖
            while len(new_population) < self.population_size:
                # 选择父代
                parent1 = self.select_parents()
                parent2 = self.select_parents()
                
                # 交叉
                if random.random() < self.crossover_rate:
                    child = self.crossover(parent1, parent2)
                else:
                    child = Chromosome(
                        policy_values=parent1.policy_values.copy(),
                        rhetorical_style=parent1.rhetorical_style,
                        emotional_intensity=parent1.emotional_intensity
                    )
                
                # 变异
                child = self.mutate(child)
                
                # 评估
                self.calculate_fitness(child)
                new_population.append(child)
            
            # 替换旧种群
            self.population = new_population
            
            # 找到当前代最佳
            current_best = max(self.population, key=lambda c: c.fitness_score)
            history.append({
                "generation": generation + 1,
                "best_fitness": current_best.fitness_score,
                "average_fitness": sum(c.fitness_score for c in self.population) / len(self.population)
            })
            
            if current_best.fitness_score > best_chromosome.fitness_score:
                best_chromosome = current_best
                self.best_solution = best_chromosome
            
            print(f"    最佳适应度：{current_best.fitness_score:.4f}")
            print(f"    平均适应度：{history[-1]['average_fitness']:.4f}")
        
        print("\n[GA] 演化完成!")
        return best_chromosome
    
    def get_policy_analysis(self) -> Dict:
        """分析最佳政策的含义"""
        if not self.best_solution:
            return {}
        
        policy_names = [
            "经济自由化",
            "社会福利投入",
            "环境保护力度",
            "移民政策严格度",
            "公共教育投资"
        ]
        
        analysis = {
            name: value 
            for name, value in zip(policy_names, self.best_solution.policy_values)
        }
        
        style_mapping = {
            0: "传统保守主义",
            1: "激进进步主义", 
            2: "温和中间派"
        }
        
        analysis["rhetorical_style"] = style_mapping.get(
            self.best_solution.rhetorical_style, "未知"
        )
        analysis["emotional_intensity"] = self.best_solution.emotional_intensity
        
        return analysis


# ======================
# 使用示例
# ======================
if __name__ == "__main__":
    print("=" * 60)
    print("GENETIC ALGORITHM TEST - Policy Evolution")
    print("=" * 60)
    
    # 创建 GA 实例
    ga = GeneticAlgorithm(
        population_size=30,
        mutation_rate=0.15,
        crossover_rate=0.8,
        generations=10
    )
    
    # 运行演化
    best = ga.evolve()
    
    # 分析结果
    print("\n" + "=" * 60)
    print("🏆 BEST POLICY FOUND:")
    print("=" * 60)
    
    analysis = ga.get_policy_analysis()
    for key, value in analysis.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")
    
    print("=" * 60)
    print("\n💡 建议政府采用以下政策组合:")
    policy = ga.get_policy_analysis()
    for name, score in policy.items():
        if isinstance(score, float) and name != "emotional_intensity":
            direction = "增加" if score > 0.6 else ("减少" if score < 0.4 else "维持")
            print(f"  → {direction} {name}")
