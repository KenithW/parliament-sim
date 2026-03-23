"""
UK Parliament Simulation - Main Entry Point (Enhanced)
英国议会模拟系统 - 主入口（增强版）

使用方法:
    python main.py                      # 运行示例辩论
    python main.py --mode pmqs          # 首相问答环节
    python main.py --mode debate        # 正式辩论
    python main.py --mode full          # 完整议程
    python main.py --topic "你的议题"    # 指定议题
    python main.py --turns 10           # 指定回合数
    python main.py --with-vote          # 启用投票
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from workflow import run_debate_mode, run_pmq_mode, run_full_session
from state import create_initial_state
from config import PARTIES, DEBATE_CONFIG


def save_debate_record(state: dict, output_dir: str = "debates"):
    """
    保存辩论记录到文件
    
    Args:
        state: 最终状态
        output_dir: 输出目录
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debate_{timestamp}.md"
    filepath = output_path / filename
    
    # 写入 Markdown 文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# 🏛️ UK Parliament Debate Record\n\n")
        f.write(f"**Mode:** {state.get('mode', 'debate')}\n\n")
        f.write(f"**Topic:** {state['topic']}\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Turns:** {state['turn_count']}\n\n")
        f.write("---\n\n")
        
        for record in state["debate_records"]:
            f.write(f"## {record.speaker.upper()} (Turn {record.turn})\n\n")
            f.write(f"{record.content}\n\n")
            f.write("---\n\n")
        
        if state.get("votes"):
            f.write(f"## 📊 投票结果\n\n")
            f.write(f"- 赞成：{state['votes'].get('ayes', 0)}\n")
            f.write(f"- 反对：{state['votes'].get('nos', 0)}\n")
            f.write(f"- 弃权：{state['votes'].get('abstentions', 0)}\n")
            f.write(f"- 结果：{state['votes'].get('result', 'unknown')}\n\n")
    
    print(f"📄 辩论记录已保存：{filepath}")
    return filepath


def save_pmq_record(records: list, output_dir: str = "debates"):
    """
    保存 PMQ 记录到文件
    
    Args:
        records: PMQ 记录列表
        output_dir: 输出目录
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pmq_{timestamp}.md"
    filepath = output_path / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# 🎯 Prime Minister's Questions (PMQs)\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        for rec in records:
            f.write(f"## Question {rec['turn'] + 1}\n\n")
            f.write(f"**Questioner:** {rec['questioner_role']} ({rec['questioner_party']})\n\n")
            f.write(f"### Question\n\n{rec['question']}\n\n")
            f.write(f"### Prime Minister's Response\n\n{rec['response']}\n\n")
            f.write("---\n\n")
    
    print(f"📄 PMQ 记录已保存：{filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="🏛️ UK Parliament Simulation - 英国议会模拟系统（增强版）"
    )
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["debate", "pmqs", "full"],
        default="debate",
        help="运行模式：debate=辩论，pmqs=首相问答，full=完整议程"
    )
    parser.add_argument(
        "--topic", "-t",
        type=str,
        default="是否应该增加 NHS（国家医疗服务）的预算？",
        help="辩论议题"
    )
    parser.add_argument(
        "--turns", "-n",
        type=int,
        default=8,
        help="最大回合数 (默认：8)"
    )
    parser.add_argument(
        "--with-vote", "-v",
        action="store_true",
        help="启用投票系统"
    )
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="保存记录到文件"
    )
    parser.add_argument(
        "--list-parties",
        action="store_true",
        help="列出可用政党"
    )
    parser.add_argument(
        "--list-roles",
        action="store_true",
        help="列出可用角色"
    )
    
    args = parser.parse_args()
    
    # 列出政党
    if args.list_parties:
        print("\n📋 可用政党:\n")
        for key, party in PARTIES.items():
            print(f"  {party.name} ({key})")
            print(f"    政纲：{party.manifesto}\n")
        return
    
    # 列出角色
    if args.list_roles:
        print("\n📋 可用角色:\n")
        roles = [
            ("Speaker", "议长 - 中立主持"),
            ("PM", "首相 - 执政党领袖"),
            ("LO", "反对党领袖"),
            ("Chancellor", "财政大臣"),
            ("Shadow Chancellor", "影子财政大臣"),
            ("Backbencher", "后座议员"),
        ]
        for role, desc in roles:
            print(f"  {role}: {desc}")
        return
    
    # 运行不同模式
    print("\n" + "="*60)
    print("🏛️  UK Parliament Simulation")
    print("    英国议会模拟系统")
    print("="*60)
    print(f"\n📌 模式：{args.mode}")
    print(f"📌 议题：{args.topic}")
    print(f"📊 回合数：{args.turns}")
    print(f"🤖 模型：{__import__('config').LLM_CONFIG['model']}")
    print("\n开始...\n")
    
    if args.mode == "pmqs":
        # PMQ 模式
        records = run_pmq_mode(args.topic)
        if args.save:
            save_pmq_record(records)
    
    elif args.mode == "debate":
        # 辩论模式
        final_state = run_debate_mode(args.topic, args.turns, with_vote=args.with_vote)
        if args.save:
            save_debate_record(final_state)
    
    elif args.mode == "full":
        # 完整模式
        result = run_full_session(args.topic, args.turns)
        if args.save:
            save_pmq_record(result["pmq"])
            save_debate_record(result["debate"])
    
    print("\n✅ 完成!\n")


if __name__ == "__main__":
    main()
