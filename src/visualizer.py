"""
Visualizer: Tkinter-based graphical playback of the Fly-in drone simulation.

Consumes the same `paths` dictionary produced by Scheduler and the same
DroneMap produced by Parsing/main.py — it does not touch or influence the
pathfinding/scheduling algorithm in any way. Drop this file into src/ as
visualizer.py.
"""
from __future__ import annotations

import tkinter as tk
from typing import Dict, List, Optional, Tuple

from src.parsing import DroneMap
from src.simulator import DroneStatus

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
CANVAS_WIDTH = 900
CANVAS_HEIGHT = 680
SIDEBAR_WIDTH = 280
PADDING = 60
ZONE_RADIUS = 20
DRONE_RADIUS = 9
TRAIL_LENGTH = 6

TWEEN_STEPS = 12
DEFAULT_DELAY_MS = 650  # total ms per simulated turn (before speed slider)

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
BG_DARK = "#11121a"
PANEL_BG = "#181a26"
PANEL_BORDER = "#2b2e40"
TEXT_LIGHT = "#eef0fb"
TEXT_MUTED = "#8b8fa8"
ACCENT = "#7c9eff"
LINE_COLOR = "#2e3145"

ZONE_MODE_COLORS = {
    "normal": "#454863",
    "priority": "#f4b942",
    "restricted": "#e4572e",
    "blocked": "#2a2c38",
}
ZONE_BORDER = "#f4f5fb"
START_GLOW = "#4caf50"
END_GLOW = "#ffd166"

DRONE_PALETTE = [
    "#00d4ff", "#ff6b6b", "#c77dff", "#06ffa5",
    "#ffd166", "#ef476f", "#4cc9f0", "#fb8500",
    "#80ffdb", "#f15bb5",
]


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class Visualizer:
    def __init__(
        self,
        paths: Dict[int, List[Tuple[str, int]]],
        dronemap: DroneMap,
    ) -> None:
        self.paths = paths
        self.dronemap = dronemap
        self.drones = [
            DroneStatus(drone_id, path) for drone_id, path in paths.items()
        ]
        self.total_turns = max(
            (path[-1][1] for path in paths.values() if path), default=0
        )

        self.current_turn = 0
        self.playing = False
        self.delay_ms = DEFAULT_DELAY_MS

        self.zone_pixel: Dict[str, Tuple[float, float]] = {}
        self.drone_items: Dict[int, int] = {}
        self.drone_glow_items: Dict[int, int] = {}
        self.drone_labels: Dict[int, int] = {}
        self.drone_pos: Dict[int, Tuple[float, float]] = {}
        self.drone_trail: Dict[int, List[Tuple[float, float]]] = {}
        self.trail_item_ids: List[int] = []

        self._tween_step = 0
        self._tween_start: Dict[int, Tuple[float, float]] = {}
        self._tween_target: Dict[int, Tuple[float, float]] = {}

        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self.turn_label: Optional[tk.Label] = None
        self.delivered_label: Optional[tk.Label] = None
        self.play_button: Optional[tk.Button] = None
        self.progress_bar_bg: Optional[int] = None
        self.progress_bar_fg: Optional[int] = None
        self._progress_canvas: Optional[tk.Canvas] = None

    # ------------------------------------------------------------------
    # Coordinate mapping
    # ------------------------------------------------------------------
    def _all_zones(self) -> dict:
        zones = dict(self.dronemap.zones)
        zones[self.dronemap.start_hub.name] = self.dronemap.start_hub
        zones[self.dronemap.end_hub.name] = self.dronemap.end_hub
        return zones

    def _compute_pixel_positions(self) -> None:
        zones = self._all_zones()
        xs = [z.coords[0] for z in zones.values()]
        ys = [z.coords[1] for z in zones.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(max_x - min_x, 1)
        span_y = max(max_y - min_y, 1)
        usable_w = CANVAS_WIDTH - 2 * PADDING
        usable_h = CANVAS_HEIGHT - 2 * PADDING

        for name, zone in zones.items():
            x, y = zone.coords
            px = PADDING + (x - min_x) / span_x * usable_w
            py = PADDING + (1 - (y - min_y) / span_y) * usable_h
            self.zone_pixel[name] = (px, py)

    # ------------------------------------------------------------------
    # Static drawing (drawn once)
    # ------------------------------------------------------------------
    def _draw_background(self) -> None:
        for i in range(0, CANVAS_HEIGHT, 40):
            shade = "#141520" if (i // 40) % 2 == 0 else BG_DARK
            self.canvas.create_rectangle(
                0, i, CANVAS_WIDTH, i + 40, fill=shade, outline="",
            )

    def _draw_connections(self) -> None:
        for conn in self.dronemap.connections:
            x1, y1 = self.zone_pixel[conn.zone_a]
            x2, y2 = self.zone_pixel[conn.zone_b]
            width = 1 + min(conn.max_link_capacity, 3)
            self.canvas.create_line(
                x1, y1, x2, y2, fill=LINE_COLOR, width=width,
                capstyle=tk.ROUND,
            )

    def _zone_fill(self, name: str, zone) -> str:
        if name == self.dronemap.start_hub.name:
            return START_GLOW
        if name == self.dronemap.end_hub.name:
            return END_GLOW
        return ZONE_MODE_COLORS.get(zone.mode, zone.color or "#666666")

    def _draw_zones(self) -> None:
        for name, zone in self._all_zones().items():
            x, y = self.zone_pixel[name]
            fill = self._zone_fill(name, zone)

            # soft drop shadow
            self.canvas.create_oval(
                x - ZONE_RADIUS + 3, y - ZONE_RADIUS + 4,
                x + ZONE_RADIUS + 3, y + ZONE_RADIUS + 4,
                fill="#000000", outline="",
            )
            # outer glow ring
            self.canvas.create_oval(
                x - ZONE_RADIUS - 4, y - ZONE_RADIUS - 4,
                x + ZONE_RADIUS + 4, y + ZONE_RADIUS + 4,
                fill="", outline=fill, width=1,
            )
            # main body
            self.canvas.create_oval(
                x - ZONE_RADIUS, y - ZONE_RADIUS,
                x + ZONE_RADIUS, y + ZONE_RADIUS,
                fill=fill, outline=ZONE_BORDER, width=2,
            )
            self.canvas.create_text(
                x, y + ZONE_RADIUS + 14,
                text=name, font=("Segoe UI", 8), fill=TEXT_MUTED,
            )
            if zone.max_drones > 1:
                self.canvas.create_text(
                    x, y, text=f"×{zone.max_drones}",
                    font=("Segoe UI", 8, "bold"), fill="#11121a",
                )

    # ------------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------------
    def _build_sidebar(self, parent: tk.Frame) -> None:
        parent.configure(bg=PANEL_BG, width=SIDEBAR_WIDTH)

        tk.Label(
            parent, text="FLY-IN", font=("Segoe UI", 20, "bold"),
            fg=ACCENT, bg=PANEL_BG,
        ).pack(anchor="w", padx=20, pady=(24, 0))
        tk.Label(
            parent, text="Drone Routing Simulation",
            font=("Segoe UI", 10), fg=TEXT_MUTED, bg=PANEL_BG,
        ).pack(anchor="w", padx=20, pady=(0, 20))

        self._divider(parent)

        self.turn_label = tk.Label(
            parent, text=f"Turn 0 / {self.total_turns}",
            font=("Segoe UI", 16, "bold"), fg=TEXT_LIGHT, bg=PANEL_BG,
        )
        self.turn_label.pack(anchor="w", padx=20, pady=(16, 4))

        progress_canvas = tk.Canvas(
            parent, width=SIDEBAR_WIDTH - 40, height=10,
            bg=PANEL_BG, highlightthickness=0,
        )
        progress_canvas.pack(padx=20, pady=(0, 16))
        self.progress_bar_bg = progress_canvas.create_rectangle(
            0, 0, SIDEBAR_WIDTH - 40, 10, fill="#262838", outline="",
        )
        self.progress_bar_fg = progress_canvas.create_rectangle(
            0, 0, 0, 10, fill=ACCENT, outline="",
        )
        self._progress_canvas = progress_canvas

        self.delivered_label = tk.Label(
            parent, text=f"Delivered: 0 / {len(self.drones)}",
            font=("Segoe UI", 11), fg=TEXT_MUTED, bg=PANEL_BG,
        )
        self.delivered_label.pack(anchor="w", padx=20, pady=(0, 16))

        self._divider(parent)

        controls = tk.Frame(parent, bg=PANEL_BG)
        controls.pack(pady=16)
        self._flat_button(controls, "⏮", self._step_back).pack(
            side="left", padx=4,
        )
        self.play_button = self._flat_button(
            controls, "▶ Play", self._toggle_play, accent=True,
        )
        self.play_button.pack(side="left", padx=4)
        self._flat_button(controls, "⏭", self._step_forward).pack(
            side="left", padx=4,
        )

        tk.Label(
            parent, text="Speed", font=("Segoe UI", 9),
            fg=TEXT_MUTED, bg=PANEL_BG,
        ).pack(anchor="w", padx=20, pady=(12, 0))
        speed_slider = tk.Scale(
            parent, from_=150, to=1200, orient="horizontal",
            length=SIDEBAR_WIDTH - 40, showvalue=False,
            bg=PANEL_BG, fg=TEXT_MUTED, troughcolor="#262838",
            highlightthickness=0, command=self._on_speed_change,
        )
        speed_slider.set(DEFAULT_DELAY_MS)
        speed_slider.pack(padx=20, pady=(0, 16))

        self._divider(parent)
        self._build_legend(parent)

    def _divider(self, parent: tk.Frame) -> None:
        tk.Frame(parent, bg=PANEL_BORDER, height=1).pack(
            fill="x", padx=20, pady=4,
        )

    def _flat_button(self, parent, text, command, accent=False) -> tk.Button:
        return tk.Button(
            parent, text=text, command=command,
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT if accent else "#232538",
            fg="#0d0e14" if accent else TEXT_LIGHT,
            activebackground="#9db4ff" if accent else "#31334a",
            relief="flat", padx=14, pady=6, bd=0, cursor="hand2",
        )

    def _build_legend(self, parent: tk.Frame) -> None:
        tk.Label(
            parent, text="ZONE TYPES", font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED, bg=PANEL_BG,
        ).pack(anchor="w", padx=20, pady=(16, 8))

        items = [
            ("Normal", ZONE_MODE_COLORS["normal"]),
            ("Priority", ZONE_MODE_COLORS["priority"]),
            ("Restricted (2 turns)", ZONE_MODE_COLORS["restricted"]),
            ("Blocked", ZONE_MODE_COLORS["blocked"]),
            ("Start", START_GLOW),
            ("End", END_GLOW),
        ]
        for label, color in items:
            row = tk.Frame(parent, bg=PANEL_BG)
            row.pack(anchor="w", padx=20, pady=2)
            swatch = tk.Canvas(
                row, width=14, height=14, bg=PANEL_BG, highlightthickness=0,
            )
            swatch.create_oval(1, 1, 13, 13, fill=color, outline="")
            swatch.pack(side="left", padx=(0, 8))
            tk.Label(
                row, text=label, font=("Segoe UI", 9),
                fg=TEXT_LIGHT, bg=PANEL_BG,
            ).pack(side="left")

    # ------------------------------------------------------------------
    # Drones
    # ------------------------------------------------------------------
    def _drone_color(self, drone_id: int) -> str:
        return DRONE_PALETTE[drone_id % len(DRONE_PALETTE)]

    def _initial_offset(self, index: int) -> Tuple[float, float]:
        return (index % 6) * 6 - 15, (index // 6) * 6 - 8

    def _place_drones_initial(self) -> None:
        start_x, start_y = self.zone_pixel[self.dronemap.start_hub.name]
        for i, drone in enumerate(self.drones):
            off_x, off_y = self._initial_offset(i)
            x, y = start_x + off_x, start_y + off_y
            color = self._drone_color(drone.id)

            glow = self.canvas.create_oval(
                x - DRONE_RADIUS - 4, y - DRONE_RADIUS - 4,
                x + DRONE_RADIUS + 4, y + DRONE_RADIUS + 4,
                fill="", outline=color, width=1,
            )
            body = self.canvas.create_oval(
                x - DRONE_RADIUS, y - DRONE_RADIUS,
                x + DRONE_RADIUS, y + DRONE_RADIUS,
                fill=color, outline="#0d0e14", width=1,
            )
            label = self.canvas.create_text(
                x, y, text=str(drone.id + 1),
                font=("Segoe UI", 7, "bold"), fill="#0d0e14",
            )
            self.drone_glow_items[drone.id] = glow
            self.drone_items[drone.id] = body
            self.drone_labels[drone.id] = label
            self.drone_pos[drone.id] = (x, y)
            self.drone_trail[drone.id] = [(x, y)]

    def _position_for_value(self, value: str) -> Tuple[float, float]:
        if value in self.zone_pixel:
            return self.zone_pixel[value]
        if "-" in value:
            zone_a, zone_b = value.split("-", 1)
            if zone_a in self.zone_pixel and zone_b in self.zone_pixel:
                x1, y1 = self.zone_pixel[zone_a]
                x2, y2 = self.zone_pixel[zone_b]
                return (x1 + x2) / 2, (y1 + y2) / 2
        return (CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2)

    def _move_drone(self, drone_id: int, x: float, y: float) -> None:
        body = self.drone_items[drone_id]
        glow = self.drone_glow_items[drone_id]
        label = self.drone_labels[drone_id]
        self.canvas.coords(
            body, x - DRONE_RADIUS, y - DRONE_RADIUS,
            x + DRONE_RADIUS, y + DRONE_RADIUS,
        )
        self.canvas.coords(
            glow, x - DRONE_RADIUS - 4, y - DRONE_RADIUS - 4,
            x + DRONE_RADIUS + 4, y + DRONE_RADIUS + 4,
        )
        self.canvas.coords(label, x, y)
        self.drone_pos[drone_id] = (x, y)

    def _redraw_trails(self) -> None:
        for item in self.trail_item_ids:
            self.canvas.delete(item)
        self.trail_item_ids.clear()

        for drone in self.drones:
            points = self.drone_trail[drone.id]
            if len(points) < 2:
                continue
            color = self._drone_color(drone.id)
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                item = self.canvas.create_line(
                    x1, y1, x2, y2, fill=color, width=2,
                    capstyle=tk.ROUND,
                )
                self.canvas.tag_lower(item)
                self.trail_item_ids.append(item)

    # ------------------------------------------------------------------
    # Playback / tweened animation
    # ------------------------------------------------------------------
    def _delivered_count(self) -> int:
        end_zone = self.dronemap.end_hub.name
        return sum(
            1 for d in self.drones
            if d.get_zone_at(self.current_turn) == end_zone
        )

    def _update_progress(self) -> None:
        ratio = self.current_turn / self.total_turns if self.total_turns else 0
        width = (SIDEBAR_WIDTH - 40) * ratio
        self._progress_canvas.coords(self.progress_bar_fg, 0, 0, width, 10)

    def _refresh_stats(self) -> None:
        self.turn_label.config(
            text=f"Turn {self.current_turn} / {self.total_turns}"
        )
        self.delivered_label.config(
            text=f"Delivered: {self._delivered_count()} / {len(self.drones)}"
        )
        self._update_progress()

    def _advance_turn(self) -> None:
        if self.current_turn >= self.total_turns:
            self.playing = False
            self.play_button.config(text="↻ Replay")
            return

        self.current_turn += 1
        self._tween_start = dict(self.drone_pos)
        self._tween_target = {}
        for drone in self.drones:
            value = drone.get_zone_at(self.current_turn)
            if value is None:
                self._tween_target[drone.id] = self.drone_pos[drone.id]
            else:
                self._tween_target[drone.id] = self._position_for_value(value)

        self._tween_step = 0
        self._do_tween()

    def _do_tween(self) -> None:
        t = self._tween_step / TWEEN_STEPS
        for drone_id, (sx, sy) in self._tween_start.items():
            tx, ty = self._tween_target[drone_id]
            self._move_drone(drone_id, lerp(sx, tx, t), lerp(sy, ty, t))

        self._tween_step += 1
        if self._tween_step <= TWEEN_STEPS:
            self.root.after(
                max(self.delay_ms // TWEEN_STEPS, 10), self._do_tween,
            )
            return

        for drone in self.drones:
            trail = self.drone_trail[drone.id]
            trail.append(self.drone_pos[drone.id])
            if len(trail) > TRAIL_LENGTH:
                trail.pop(0)
        self._redraw_trails()
        self._refresh_stats()

        if self.playing:
            self._advance_turn()

    def _toggle_play(self) -> None:
        if self.current_turn >= self.total_turns:
            self._reset()

        self.playing = not self.playing
        self.play_button.config(text="⏸ Pause" if self.playing else "▶ Play")
        if self.playing:
            self._advance_turn()

    def _reset(self) -> None:
        self.current_turn = 0
        start_x, start_y = self.zone_pixel[self.dronemap.start_hub.name]
        for i, drone in enumerate(self.drones):
            off_x, off_y = self._initial_offset(i)
            x, y = start_x + off_x, start_y + off_y
            self._move_drone(drone.id, x, y)
            self.drone_trail[drone.id] = [(x, y)]
        self._redraw_trails()
        self._refresh_stats()

    def _jump_to_turn(self, turn: int) -> None:
        self.current_turn = turn
        for drone in self.drones:
            value = drone.get_zone_at(self.current_turn)
            if value is not None:
                x, y = self._position_for_value(value)
                self._move_drone(drone.id, x, y)
                trail = self.drone_trail[drone.id]
                trail.append((x, y))
                if len(trail) > TRAIL_LENGTH:
                    trail.pop(0)
        self._redraw_trails()
        self._refresh_stats()

    def _step_forward(self) -> None:
        self.playing = False
        self.play_button.config(text="▶ Play")
        if self.current_turn < self.total_turns:
            self._jump_to_turn(self.current_turn + 1)

    def _step_back(self) -> None:
        self.playing = False
        self.play_button.config(text="▶ Play")
        if self.current_turn > 0:
            self._jump_to_turn(self.current_turn - 1)

    def _on_speed_change(self, value: str) -> None:
        self.delay_ms = int(value)

    # ------------------------------------------------------------------
    # Setup / entry point
    # ------------------------------------------------------------------
    def _setup_window(self) -> None:
        self.root = tk.Tk()
        self.root.title("Fly-in — Drone Routing Simulation")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        main = tk.Frame(self.root, bg=BG_DARK)
        main.pack()

        self.canvas = tk.Canvas(
            main, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
            bg=BG_DARK, highlightthickness=0,
        )
        self.canvas.pack(side="left")

        sidebar = tk.Frame(main, bg=PANEL_BG, width=SIDEBAR_WIDTH)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

    def run(self) -> None:
        self._compute_pixel_positions()
        self._setup_window()
        self._draw_background()
        self._draw_connections()
        self._draw_zones()
        self._place_drones_initial()
        self.root.mainloop()