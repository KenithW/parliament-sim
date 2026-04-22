"""CSV and transcript output for strategy comparison experiments."""

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class ExperimentResults:
    topic: str
    rows: List[Dict] = field(default_factory=list)
    experiment_id: str = field(default_factory=lambda: datetime.now().strftime("exp_%Y%m%d_%H%M%S"))

    @property
    def results(self) -> List[Dict]:
        return self.rows

    def add(self, row: Dict) -> None:
        self.rows.append(row)

    def add_result(self, row: Dict) -> None:
        self.add(row)

    def save(self, output_dir: str) -> Path:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        self._write_runs(output / "runs.csv")
        self._write_summary(output / "summary.csv")
        (output / "metadata.json").write_text(
            json.dumps(
                {
                    "experiment_id": self.experiment_id,
                    "topic": self.topic,
                    "runs": len(self.rows),
                    "strategies": sorted({r["strategy"] for r in self.rows}),
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return output

    def to_csv(self, output_dir: str) -> Path:
        return self.save(output_dir)

    def save_transcript(
        self,
        records: List,
        strategy: str,
        run_number: int,
        output_dir: str,
        evaluation: Dict = None,
        vote: Dict = None,
    ) -> str:
        folder = Path(output_dir) / "transcripts"
        folder.mkdir(parents=True, exist_ok=True)
        filename = f"{strategy}_run{run_number}.md"
        path = folder / filename
        with path.open("w", encoding="utf-8") as f:
            f.write(f"# Debate Transcript\n\n")
            f.write(f"Topic: {self.topic}\n\n")
            f.write(f"Strategy: {strategy}\n\n")
            for record in records:
                f.write(f"## Turn {record.turn}: {record.role} ({record.side})\n\n")
                f.write(f"Strategy move: {record.strategy}\n\n")
                f.write(record.content.strip() + "\n\n")
            if evaluation:
                f.write("## Evaluation\n\n")
                f.write(f"- Government score: {evaluation['government']['overall']:.2f}\n")
                f.write(f"- Opposition score: {evaluation['opposition']['overall']:.2f}\n")
                f.write(f"- Score winner: {evaluation['comparison']['winner']}\n\n")
            if vote:
                f.write("## Final Vote\n\n")
                f.write(
                    f"Government {vote['government_votes']} | "
                    f"Opposition {vote['opposition_votes']} | "
                    f"Abstain {vote['abstentions']}\n\n"
                )
                f.write(f"Winner: {vote['winner']}\n\n")
                for ballot in vote["ballots"]:
                    f.write(
                        f"- {ballot['voter']}: {ballot['vote']} "
                        f"({ballot['reason']})\n"
                    )
        return str(path)

    def save_debate_record(self, debate_records: List, strategy: str, run_number: int, output_dir: str) -> str:
        return self.save_transcript(debate_records, strategy, run_number, output_dir)

    def summary(self) -> str:
        grouped = self._grouped()
        lines = ["Strategy comparison summary", ""]
        for strategy, rows in sorted(grouped.items()):
            avg_quality = _avg(rows, "total_quality")
            avg_margin = _avg(rows, "government_margin")
            gov_wins = sum(1 for row in rows if row["winner"] == "government")
            lines.append(
                f"- {strategy}: quality={avg_quality:.2f}, "
                f"government_margin={avg_margin:+.2f}, government_wins={gov_wins}/{len(rows)}"
            )
        return "\n".join(lines)

    def _write_runs(self, path: Path) -> None:
        fields = [
            "experiment_id",
            "strategy",
            "run",
            "topic",
            "winner",
            "score_winner",
            "government_score",
            "opposition_score",
            "government_margin",
            "total_quality",
            "government_votes",
            "opposition_votes",
            "abstentions",
            "vote_margin",
            "duration_s",
            "turns",
            "transcript",
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in self.rows:
                writer.writerow({field: row.get(field, "") for field in fields})

    def _write_summary(self, path: Path) -> None:
        fields = [
            "strategy",
            "runs",
            "avg_total_quality",
            "avg_government_score",
            "avg_opposition_score",
            "avg_government_margin",
            "government_win_rate",
            "avg_government_votes",
            "avg_opposition_votes",
            "avg_duration_s",
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for strategy, rows in sorted(self._grouped().items()):
                writer.writerow(
                    {
                        "strategy": strategy,
                        "runs": len(rows),
                        "avg_total_quality": f"{_avg(rows, 'total_quality'):.3f}",
                        "avg_government_score": f"{_avg(rows, 'government_score'):.3f}",
                        "avg_opposition_score": f"{_avg(rows, 'opposition_score'):.3f}",
                        "avg_government_margin": f"{_avg(rows, 'government_margin'):.3f}",
                        "government_win_rate": f"{_rate(rows, 'winner', 'government'):.1f}%",
                        "avg_government_votes": f"{_avg(rows, 'government_votes'):.2f}",
                        "avg_opposition_votes": f"{_avg(rows, 'opposition_votes'):.2f}",
                        "avg_duration_s": f"{_avg(rows, 'duration_s'):.3f}",
                    }
                )

    def _grouped(self) -> Dict[str, List[Dict]]:
        grouped = {}
        for row in self.rows:
            grouped.setdefault(row["strategy"], []).append(row)
        return grouped


def _avg(rows: List[Dict], key: str) -> float:
    return sum(float(row.get(key, 0.0)) for row in rows) / max(1, len(rows))


def _rate(rows: List[Dict], key: str, value: str) -> float:
    return sum(1 for row in rows if row.get(key) == value) / max(1, len(rows)) * 100
