"""
FNX Taxonomy Loader v2.1
Hybrid Architecture: ASK (Primary) × Katz (Career Path)

Loads competency_taxonomy.yaml into typed dataclasses.
Provides singleton access via get_taxonomy().
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from functools import lru_cache


# ── Dataclasses ──

@dataclass
class LevelDefinition:
    """Thang đo 1 cấp độ theo Bloom's Taxonomy."""
    level: int
    name: str
    vi: str
    bloom: str
    abb_role: str
    experience: str
    description: str
    assessment_method: str


@dataclass
class Competency:
    """1 năng lực cụ thể, có 5 level descriptions + Katz zone mapping."""
    id: str
    name: str
    en: str
    description: str
    source: str
    katz_zone: str  # TECHNICAL | INTERPERSONAL | CONCEPTUAL
    levels: Dict[int, str] = field(default_factory=dict)


@dataclass
class AskGroup:
    """ASK primary group: Knowledge (K), Skill (S), or Attitude (A)."""
    id: str
    name: str
    vi: str
    description: str
    training_method: str
    color: str
    competencies: List[Competency] = field(default_factory=list)


@dataclass
class KatzZone:
    """Katz secondary zone: Technical, Interpersonal, or Conceptual."""
    id: str
    name: str
    vi: str
    description: str
    color: str
    competency_ids: List[str] = field(default_factory=list)


@dataclass
class RoleProfile:
    """Dual-weighted role profile — ASK weights for training, Katz weights for career path."""
    id: str
    name: str
    en: str
    description: str
    expected_level: str
    ask_weights: Dict[str, int] = field(default_factory=dict)
    katz_weights: Dict[str, int] = field(default_factory=dict)


@dataclass
class Taxonomy:
    """FNX Competency Taxonomy v2.1 — Hybrid ASK × Katz."""
    version: str
    status: str
    backbone: str
    sources: List[str]
    target_audience: List[str]
    context: str
    levels: Dict[int, LevelDefinition] = field(default_factory=dict)
    ask_groups: List[AskGroup] = field(default_factory=list)
    katz_zones: Dict[str, KatzZone] = field(default_factory=dict)
    role_profiles: Dict[str, RoleProfile] = field(default_factory=dict)

    # ── Backward-compatible aliases ──
    @property
    def groups(self) -> List[AskGroup]:
        """Alias for ask_groups — backward compatible."""
        return self.ask_groups

    @property
    def dimensions(self) -> List[AskGroup]:
        """Alias for ask_groups — backward compatible with v2.0."""
        return self.ask_groups

    @property
    def competency_ids(self) -> List[str]:
        """Ordered list: K1, K2, S1, S2, S3, S4, S5, A1, A2, A3."""
        ids = []
        for grp in self.ask_groups:
            for comp in grp.competencies:
                ids.append(comp.id)
        return ids

    def get_competency(self, comp_id: str) -> Optional[Competency]:
        """Look up a competency by ID (e.g. 'K1', 'S3', 'A2')."""
        for grp in self.ask_groups:
            for comp in grp.competencies:
                if comp.id == comp_id:
                    return comp
        return None

    def get_ask_group(self, group_id: str) -> Optional[AskGroup]:
        """Look up ASK group by ID: 'K', 'S', or 'A'."""
        for grp in self.ask_groups:
            if grp.id == group_id:
                return grp
        return None

    def get_katz_zone(self, comp_id: str) -> Optional[str]:
        """Get the Katz zone for a competency (e.g. 'K1' → 'TECHNICAL')."""
        comp = self.get_competency(comp_id)
        return comp.katz_zone if comp else None

    def get_katz_zone_info(self, zone_id: str) -> Optional[KatzZone]:
        """Get KatzZone by ID: 'TECHNICAL', 'INTERPERSONAL', 'CONCEPTUAL'."""
        return self.katz_zones.get(zone_id)

    def get_role_weights(self, role_id: str, layer: str = "ask") -> Optional[Dict[str, int]]:
        """Get weights for a role. layer='ask' or 'katz'."""
        profile = self.role_profiles.get(role_id)
        if not profile:
            return None
        return profile.ask_weights if layer == "ask" else profile.katz_weights

    def to_prompt_context(self) -> str:
        """Generate LLM system prompt context from taxonomy data.

        Uses ASK framing for clarity in LLM prompts.
        """
        lines = []
        lines.append(f"## Khung năng lực FNX v{self.version}")
        lines.append(f"Backbone: {self.backbone}")
        lines.append(f"Bối cảnh: {self.context}")
        lines.append("")

        # Level scale
        lines.append("### Cấp độ FNX (1–5)")
        lines.append("| Level | Tên | Bloom's | Mô tả |")
        lines.append("|---|---|---|---|")
        for lv_num in sorted(self.levels.keys()):
            lv = self.levels[lv_num]
            lines.append(f"| {lv.level} | {lv.vi} | {lv.bloom} | {lv.description} |")
        lines.append("")

        # ASK groups & competencies
        lines.append("### 3 ASK Groups")
        for grp in self.ask_groups:
            lines.append(f"\n#### {grp.id} — {grp.vi}")
            lines.append(f"_{grp.description}_")
            lines.append(f"Phương pháp đào tạo: {grp.training_method}\n")
            for comp in grp.competencies:
                lines.append(f"- **{comp.id}** — {comp.name}: {comp.description}")
        lines.append("")

        # Competency IDs summary
        ids = self.competency_ids
        lines.append(f"### Competency IDs: {', '.join(ids)}")
        lines.append(f"### ASK Types: K=Knowledge, S=Skill, A=Attitude")
        lines.append("")

        # Role profiles
        lines.append("### Đối tượng đánh giá")
        for pid, profile in self.role_profiles.items():
            w = profile.ask_weights
            lines.append(
                f"- **{profile.name}** ({profile.expected_level}): "
                f"K={w.get('K', 0)}% S={w.get('S', 0)}% A={w.get('A', 0)}%"
            )

        return "\n".join(lines)

    def __repr__(self) -> str:
        n_comps = sum(len(g.competencies) for g in self.ask_groups)
        n_levels = len(self.levels)
        n_desc = n_comps * n_levels
        return (
            f"<FNX Taxonomy v{self.version} | "
            f"ASK: {len(self.ask_groups)} groups, {n_comps} comps, {n_desc} descriptions | "
            f"Katz: {len(self.katz_zones)} zones | "
            f"{len(self.role_profiles)} role profiles>"
        )


# ── YAML Loader ──

class TaxonomyLoader:
    """Parses competency_taxonomy.yaml into Taxonomy dataclass."""

    def __init__(self, yaml_path: Optional[str] = None):
        if yaml_path is None:
            yaml_path = os.path.join(os.path.dirname(__file__), "competency_taxonomy.yaml")
        self._path = yaml_path
        self._taxonomy: Optional[Taxonomy] = None

    def load(self) -> Taxonomy:
        if self._taxonomy is not None:
            return self._taxonomy

        with open(self._path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        meta = data.get("meta", {})

        # Levels
        levels = {}
        for lv_num, lv_data in data.get("levels", {}).items():
            levels[int(lv_num)] = LevelDefinition(
                level=int(lv_num),
                name=lv_data["name"],
                vi=lv_data["vi"],
                bloom=lv_data["bloom"],
                abb_role=lv_data["abb_role"],
                experience=lv_data["experience"],
                description=lv_data["description"],
                assessment_method=lv_data["assessment_method"],
            )

        # ASK Groups
        ask_groups = []
        for grp_data in data.get("ask_groups", []):
            comps = []
            for comp_data in grp_data.get("competencies", []):
                lv_descs = {}
                for lv_num, desc in comp_data.get("levels", {}).items():
                    lv_descs[int(lv_num)] = desc
                comps.append(Competency(
                    id=comp_data["id"],
                    name=comp_data["name"],
                    en=comp_data["en"],
                    description=comp_data["description"],
                    source=comp_data.get("source", ""),
                    katz_zone=comp_data.get("katz_zone", ""),
                    levels=lv_descs,
                ))
            ask_groups.append(AskGroup(
                id=grp_data["id"],
                name=grp_data["name"],
                vi=grp_data["vi"],
                description=grp_data["description"],
                training_method=grp_data.get("training_method", ""),
                color=grp_data.get("color", "#666"),
                competencies=comps,
            ))

        # Katz Zones
        katz_zones = {}
        for zone_id, zone_data in data.get("katz_zones", {}).items():
            katz_zones[zone_id] = KatzZone(
                id=zone_id,
                name=zone_data["name"],
                vi=zone_data["vi"],
                description=zone_data["description"],
                color=zone_data.get("color", "#666"),
                competency_ids=zone_data.get("competency_ids", []),
            )

        # Role Profiles
        role_profiles = {}
        for pid, pdata in data.get("role_profiles", {}).items():
            role_profiles[pid] = RoleProfile(
                id=pid,
                name=pdata["name"],
                en=pdata["en"],
                description=pdata["description"],
                expected_level=pdata["expected_level"],
                ask_weights=pdata.get("ask_weights", {}),
                katz_weights=pdata.get("katz_weights", {}),
            )

        self._taxonomy = Taxonomy(
            version=meta.get("version", "0.0.0"),
            status=meta.get("status", ""),
            backbone=meta.get("backbone", ""),
            sources=meta.get("sources", []),
            target_audience=meta.get("target_audience", []),
            context=meta.get("context", ""),
            levels=levels,
            ask_groups=ask_groups,
            katz_zones=katz_zones,
            role_profiles=role_profiles,
        )
        return self._taxonomy


# ── Singleton ──

_loader: Optional[TaxonomyLoader] = None


def get_taxonomy() -> Taxonomy:
    """Get the singleton Taxonomy instance.

    Usage:
        from core.taxonomy import get_taxonomy
        t = get_taxonomy()
        print(t.competency_ids)        # ['K1','K2','S1',...,'A3']
        print(t.get_katz_zone('K1'))   # 'TECHNICAL'
        print(t.to_prompt_context())   # LLM prompt context (ASK framing)
    """
    global _loader
    if _loader is None:
        _loader = TaxonomyLoader()
    return _loader.load()
