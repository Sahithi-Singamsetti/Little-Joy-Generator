import random
import html
import zlib
from datetime import datetime, timedelta
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

# =============================
# PAGE CONFIGURATION
# =============================
st.set_page_config(
    page_title="Little Joy ♡",
    page_icon="🐰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================
# SESSION STATE
# =============================
defaults = {
    "current_joy": None,
    "current_joy_mood": None,
    "current_affirmation": None,
    "favourites": [],
    "completed_adventures": [],
    "current_adventure": None,
    "celebrate": False,
    "breathing_active": False,
    "breathing_cycles": 4,
    "breath_sessions": 0,
    "mood_log": [],
    "diary_saved": False,
    "now_playing": None,
    "music_favs": [],
    "music_recent": [],
    "my_playlists": [],
    "music_added": False,
    # Gratitude jar
    "gratitude_jar": [],
    "jar_prompt": None,
    "jar_pulled": None,
    "jar_shaking": False,
    "jar_flash": False,
    "jar_just_added": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =============================
# CUSTOM STYLING
# =============================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;500;600;700;800;900&display=swap');

    :root {
        --ink: #624879;
        --muted: #88739e;
        --border: #e4d2f7;
        --accent: #9874c1;
        --font-display: 'Fredoka', 'Nunito', sans-serif;
    }

    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 8% 8%, rgba(255,255,255,.8), transparent 30%),
            radial-gradient(ellipse at 92% 15%, rgba(220,199,255,.7), transparent 32%),
            radial-gradient(ellipse at 80% 90%, rgba(255,220,240,.55), transparent 30%),
            linear-gradient(135deg, #eee4ff, #f8efff 48%, #f0e5ff);
        background-attachment: fixed;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    .block-container {
        max-width: 1320px !important;
        padding: 1.5rem clamp(1rem, 4vw, 3rem) 3rem !important;
    }

    /* ---------- ANIMATIONS ---------- */
    @keyframes bob {
        0%, 100% { transform: translateY(0) rotate(-3deg); }
        50%      { transform: translateY(-9px) rotate(3deg); }
    }

    @keyframes twinkle {
        0%, 100% { opacity: .2;  transform: scale(.75) rotate(0deg); }
        50%      { opacity: 1;   transform: scale(1.2) rotate(18deg); }
    }

    @keyframes noteIn {
        from {
            opacity: 0;
            transform: translateY(16px) rotate(var(--tilt, 0deg)) scale(.96);
        }
        to {
            opacity: 1;
            transform: translateY(0) rotate(var(--tilt, 0deg)) scale(1);
        }
    }

    /* ---------- HERO ---------- */
    .hero-card {
        --hero-a: rgba(255,211,235,.65);
        --hero-b: rgba(220,201,255,.65);
        --hero-c1: #fffafd;
        --hero-c2: #fbf5ff;
        --hero-c3: #fff5fa;
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(ellipse at 8% 10%, var(--hero-a), transparent 38%),
            radial-gradient(ellipse at 92% 90%, var(--hero-b), transparent 42%),
            linear-gradient(135deg, var(--hero-c1) 0%, var(--hero-c2) 52%, var(--hero-c3) 100%);
        border: 1px solid rgba(220,188,241,.8);
        border-radius: 32px;
        padding: clamp(1.7rem, 3vw, 2.5rem) 2rem;
        text-align: center;
        box-shadow: 0 12px 35px rgba(155,112,190,.12);
        margin: 0 0 1.5rem;
    }

    .sparkle {
        position: absolute;
        color: #c3a5e7;
        pointer-events: none;
        animation: twinkle 2.8s ease-in-out infinite;
    }

    .bunny-wrap {
        margin-bottom: .4rem;
    }

    .bunny {
        display: inline-block;
        font-size: clamp(3.5rem, 5vw, 4.5rem);
        line-height: 1.2;
        filter: drop-shadow(0 4px 5px rgba(184,126,202,.18));
        animation: bob 3.4s ease-in-out infinite;
    }

    .eyebrow {
        color: #b16b9e;
        font-size: .78rem;
        font-weight: 900;
        letter-spacing: .16em;
        margin-bottom: .5rem;
    }

    .hero-title {
        color: #8054a3;
        font-size: clamp(2.5rem, 4vw, 3.4rem);
        line-height: 1.15;
        font-weight: 900;
        margin: .3rem 0 .7rem;
        letter-spacing: -.03em;
        text-shadow: 0 2px 12px rgba(207,166,235,.16);
    }

    .hero-subtitle {
        color: #866d91;
        font-size: clamp(1.05rem, 1.5vw, 1.25rem);
        margin-bottom: .4rem;
    }

    .hero-greeting {
        font-family: var(--font-display);
        color: #b0689a;
        font-size: clamp(1.4rem, 2.4vw, 1.8rem);
        font-weight: 600;
        line-height: 1.25;
        margin: .3rem 0 .2rem;
    }

    .hero-note {
        color: #b078a5;
        font-size: 1rem;
        font-style: italic;
    }

    /* ---------- BUNNY LEVEL (in the hero) ---------- */
    .hero-level {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: .4rem .8rem;
        margin-top: 1.1rem;
    }

    .level-pill {
        padding: .28rem .9rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #f6ecff, #ffe9f3);
        border: 1px solid #e4cdf5;
        color: #7a559a;
        font-size: .9rem;
        font-weight: 900;
    }

    .level-points {
        color: #a07bb5;
        font-size: .85rem;
        font-weight: 800;
    }

    .level-bar {
        width: min(260px, 70%);
        height: 8px;
        margin: .6rem auto .3rem;
        border-radius: 999px;
        background: rgba(180,140,220,.18);
        overflow: hidden;
    }

    .level-bar span {
        display: block;
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #d9b9f6, #b58be8);
        transition: width .6s ease;
    }

    .level-next {
        color: #a58abb;
        font-size: .8rem;
        font-weight: 700;
    }

    /* ---------- SECTION HEADINGS ---------- */
    .section-title {
        color: #6f508d;
        font-size: clamp(1.7rem, 2.5vw, 2.15rem);
        font-weight: 900;
        line-height: 1.3;
        margin: .35rem 0 .4rem;
        letter-spacing: -.02em;
    }

    .tiny-note {
        color: #8c76a1;
        font-size: 1.02rem;
        line-height: 1.7;
        margin-bottom: 1.2rem;
    }

    /* ---------- STICKY-NOTE CARDS ---------- */
    .joy-card {
        position: relative;
        background:
            radial-gradient(circle at 1px 1px, var(--card-dot, rgba(152,106,184,.16)) 1px, transparent 0) 0 0 / 18px 18px,
            linear-gradient(145deg, var(--card-bg1, #ffffff), var(--card-bg2, #fff7fc));
        border: 1px solid var(--card-border, #ead9f7);
        border-radius: 22px;
        padding: clamp(1.3rem, 2.5vw, 1.9rem);
        margin: 1.7rem 0 1rem;
        box-shadow: 0 7px 22px rgba(150,112,184,.10);
        transform: rotate(var(--tilt, 0deg));
        transition: transform .2s ease, box-shadow .2s ease;
    }

    /* washi tape */
    .joy-card:before {
        content: "";
        position: absolute;
        top: -13px;
        left: 50%;
        width: 92px;
        height: 26px;
        background: repeating-linear-gradient(
            135deg,
            var(--card-tape, #e4d0f7) 0 7px,
            rgba(255,255,255,.45) 7px 14px
        );
        opacity: .92;
        border-radius: 3px;
        box-shadow: 0 1px 3px rgba(0,0,0,.07);
        transform: translateX(-50%) rotate(calc(var(--tilt, 0deg) * -1.5));
        pointer-events: none;
    }

    .joy-card:hover {
        transform: translateY(-3px) rotate(var(--tilt, 0deg));
        box-shadow: 0 12px 28px rgba(150,112,184,.16);
    }

    .joy-card.fade-in {
        animation: noteIn .7s ease backwards;
    }

    .joy-heading {
        font-family: var(--font-display);
        color: var(--card-accent, #986ab8);
        font-size: 1.35rem;
        font-weight: 600;
        line-height: 1.3;
        margin-bottom: .5rem;
    }

    .joy-text {
        color: #665472;
        font-family: 'Nunito', sans-serif;
        font-size: 1.1rem;
        font-weight: 500;
        line-height: 1.65;
    }

    .card-footer {
        color: var(--card-accent, #986ab8);
        font-size: .85rem;
        font-weight: 800;
        letter-spacing: .05em;
        margin-top: .9rem;
        opacity: .85;
    }

    /* ---------- SUPPORTING CARDS ---------- */
    .mini-card {
        --tilt: 0deg;
        position: relative;
        padding: 1.3rem;
        border: 1px solid #e4d4f4;
        border-radius: 22px;
        background: rgba(255,255,255,.78);
        margin: .7rem 0 .9rem;
        box-shadow: 0 7px 20px rgba(116,82,151,.06);
        transform: rotate(var(--tilt));
        transition: transform .2s ease, box-shadow .2s ease;
    }

    .mini-card:nth-of-type(odd)  { --tilt: .7deg; }
    .mini-card:nth-of-type(even) { --tilt: -.7deg; }

    .mini-card:before {
        content: "";
        position: absolute;
        top: -9px;
        right: 24px;
        width: 54px;
        height: 18px;
        background: repeating-linear-gradient(
            135deg,
            rgba(214,190,247,.85) 0 6px,
            rgba(255,255,255,.5) 6px 12px
        );
        border-radius: 3px;
        transform: rotate(5deg);
        pointer-events: none;
    }

    .mini-card:hover {
        transform: translateY(-2px) rotate(var(--tilt));
        box-shadow: 0 10px 25px rgba(116,82,151,.11);
    }

    .mini-card-title {
        color: #795b96;
        font-size: 1.05rem;
        font-weight: 900;
        margin-bottom: .4rem;
    }

    .mini-card-text {
        color: #88749a;
        font-size: .96rem;
        line-height: 1.7;
    }

    /* ---------- MOOD DIARY ---------- */
    .week-card {
        background: rgba(255,255,255,.62);
        border: 1px solid #e4d4f4;
        border-radius: 26px;
        padding: 1.2rem 1.2rem 1rem;
        margin: .4rem 0 1.4rem;
        box-shadow: 0 7px 22px rgba(116,82,151,.07);
    }

    .week-card-title {
        font-family: var(--font-display);
        color: #795b96;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: .8rem;
    }

    .week-strip {
        display: grid;
        grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: .6rem;
    }

    .week-day {
        text-align: center;
        border: 1px solid #e4d4f4;
        border-radius: 18px;
        padding: .7rem .2rem .6rem;
        background: rgba(255,255,255,.5);
        transition: transform .2s ease;
    }

    .week-day:hover {
        transform: translateY(-3px);
    }

    .week-day.empty {
        border-style: dashed;
        background: rgba(255,255,255,.35);
    }

    .week-day.is-today {
        outline: 3px solid rgba(181,139,232,.45);
        outline-offset: 2px;
    }

    .week-name {
        color: #8c76a1;
        font-size: .75rem;
        font-weight: 900;
        letter-spacing: .08em;
        text-transform: uppercase;
    }

    .week-emoji {
        font-size: 1.9rem;
        line-height: 1.5;
    }

    .week-day.empty .week-emoji {
        color: #cdbbe0;
        font-size: 1.5rem;
    }

    .week-date {
        color: #8c76a1;
        font-size: .85rem;
        font-weight: 800;
    }

    /* ---------- BREATHING BUDDY ---------- */
    /* One full breath = 14s: in 4s (0-28.57%), hold 4s (-57.14%), out 6s (-100%) */
    @keyframes breatheCircle {
        0%      { transform: scale(.7); }
        28.57%  { transform: scale(1.3); }
        57.14%  { transform: scale(1.3); }
        100%    { transform: scale(.7); }
    }

    @keyframes breatheHalo {
        0%      { transform: scale(.7);  opacity: .35; }
        28.57%  { transform: scale(1.22); opacity: .85; }
        57.14%  { transform: scale(1.22); opacity: .85; }
        100%    { transform: scale(.7);  opacity: .35; }
    }

    @keyframes breatheBunny {
        0%      { transform: scale(.9); }
        28.57%  { transform: scale(1.1); }
        57.14%  { transform: scale(1.1); }
        100%    { transform: scale(.9); }
    }

    @keyframes labelIn {
        0%            { opacity: 0; }
        4%, 26%       { opacity: 1; }
        28.57%, 100%  { opacity: 0; }
    }

    @keyframes labelHold {
        0%, 26%       { opacity: 0; }
        30%, 54%      { opacity: 1; }
        57.14%, 100%  { opacity: 0; }
    }

    @keyframes labelOut {
        0%, 55%       { opacity: 0; }
        61%, 94%      { opacity: 1; }
        100%          { opacity: 0; }
    }

    @keyframes labelDone {
        from { opacity: 0; }
        to   { opacity: 1; }
    }

    .breath-card {
        position: relative;
        background: linear-gradient(145deg, #f4fcf9, #e6f5ef 55%, #ede6fb);
        border: 1px solid #c9e6dc;
        border-radius: 28px;
        padding: 2.2rem 1rem 1.5rem;
        margin: 1.7rem 0 1rem;
        box-shadow: 0 8px 24px rgba(74,151,134,.12);
        text-align: center;
    }

    .breath-card:before {
        content: "";
        position: absolute;
        top: -13px;
        left: 50%;
        width: 92px;
        height: 26px;
        background: repeating-linear-gradient(
            135deg,
            #b9e3d5 0 7px,
            rgba(255,255,255,.5) 7px 14px
        );
        border-radius: 3px;
        box-shadow: 0 1px 3px rgba(0,0,0,.07);
        transform: translateX(-50%) rotate(-2deg);
        pointer-events: none;
    }

    .breath-stage {
        position: relative;
        width: min(300px, 78vw);
        aspect-ratio: 1 / 1;
        margin: 0 auto;
    }

    .breath-halo,
    .breath-ring {
        position: absolute;
        top: 0; right: 0; bottom: 0; left: 0;
        margin: auto;
        border-radius: 50%;
    }

    .breath-halo {
        width: 82%;
        height: 82%;
        background: radial-gradient(circle, rgba(181,226,212,.6), rgba(214,196,247,.3) 68%, transparent 72%);
        opacity: .5;
        transform: scale(.85);
    }

    .breath-ring {
        width: 62%;
        height: 62%;
        background: radial-gradient(circle at 35% 30%, #ffffff, #cdeee2 45%, #c9b8f2 100%);
        box-shadow: 0 0 40px rgba(150,205,190,.55), inset 0 0 22px rgba(255,255,255,.8);
        transform: scale(.85);
    }

    .breath-center {
        position: absolute;
        top: 0; right: 0; bottom: 0; left: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        pointer-events: none;
    }

    .breath-bunny {
        font-size: 3.2rem;
        line-height: 1.1;
        filter: drop-shadow(0 3px 4px rgba(74,151,134,.2));
    }

    .breath-labels {
        position: relative;
        width: 100%;
        height: 2.2rem;
        margin-top: .2rem;
    }

    .breath-label {
        position: absolute;
        top: 0; left: 0; right: 0;
        font-family: var(--font-display);
        font-size: 1.25rem;
        font-weight: 600;
        line-height: 1.3;
        color: #3f7d6d;
        opacity: 0;
    }

    .breath-stage.running .breath-label.ready { display: none; }
    .breath-stage:not(.running) .breath-label.ready { opacity: 1; }

    .breath-stage.running .breath-ring {
        animation: breatheCircle 14s ease-in-out var(--cycles) both;
    }

    .breath-stage.running .breath-halo {
        animation: breatheHalo 14s ease-in-out var(--cycles) both;
    }

    .breath-stage.running .breath-bunny {
        animation: breatheBunny 14s ease-in-out var(--cycles) both;
    }

    .breath-stage.running .breath-label.in {
        animation: labelIn 14s linear var(--cycles) both;
    }

    .breath-stage.running .breath-label.hold {
        animation: labelHold 14s linear var(--cycles) both;
    }

    .breath-stage.running .breath-label.out {
        animation: labelOut 14s linear var(--cycles) both;
    }

    .breath-stage.running .breath-label.done {
        animation: labelDone .8s ease var(--done-delay) both;
    }

    .breath-pattern {
        margin-top: 1.1rem;
        color: #4f8c7c;
        font-size: .95rem;
        font-weight: 800;
        letter-spacing: .04em;
    }

    /* ---------- GRATITUDE JAR ---------- */
    @keyframes slipDrop {
        from {
            opacity: 0;
            transform: translateY(-240px) rotate(0deg) scale(.6);
        }
        to {
            opacity: 1;
            transform: translateY(0) rotate(var(--rot, 0deg)) scale(1);
        }
    }

    @keyframes jarShake {
        0%, 100% { transform: rotate(0deg) translateX(0); }
        15%      { transform: rotate(-4deg) translateX(-5px); }
        30%      { transform: rotate(4deg) translateX(5px); }
        45%      { transform: rotate(-3deg) translateX(-4px); }
        60%      { transform: rotate(3deg) translateX(4px); }
        75%      { transform: rotate(-1.5deg) translateX(-2px); }
    }

    .jar-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: .8rem 0 1.2rem;
    }

    .jar-wrap.shake {
        animation: jarShake .8s ease both;
    }

    .jar-lid {
        position: relative;
        z-index: 3;
        width: 46%;
        max-width: 150px;
        height: 26px;
        border-radius: 12px 12px 5px 5px;
        background: repeating-linear-gradient(135deg, #d9bdf5 0 8px, #e9d6fb 8px 16px);
        border: 2px solid #cfb0ee;
        box-shadow: 0 3px 8px rgba(116,82,151,.15);
    }

    .jar-neck {
        width: 56%;
        max-width: 176px;
        height: 14px;
        margin-top: -2px;
        background: rgba(255,255,255,.7);
        border: 3px solid rgba(190,160,230,.7);
        border-bottom: none;
        border-radius: 10px 10px 0 0;
    }

    .jar {
        position: relative;
        box-sizing: border-box;
        width: min(310px, 86%);
        height: 340px;
        padding: 16px 16px 20px;
        border-radius: 36px 36px 54px 54px;
        border: 3px solid rgba(190,160,230,.75);
        background: linear-gradient(160deg, rgba(255,255,255,.8), rgba(236,224,253,.5));
        box-shadow: 0 14px 30px rgba(116,82,151,.14), inset 0 0 30px rgba(255,255,255,.7);
        overflow: hidden;
        display: flex;
        flex-wrap: wrap-reverse;
        align-content: flex-start;
        justify-content: center;
        gap: 4px;
    }

    .jar:after {
        content: "";
        position: absolute;
        top: 18px;
        left: 14px;
        width: 12px;
        height: 58%;
        border-radius: 10px;
        background: linear-gradient(rgba(255,255,255,.9), rgba(255,255,255,0));
        opacity: .7;
        pointer-events: none;
    }

    .slip {
        display: grid;
        place-items: center;
        flex: 0 0 auto;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--c1), var(--c2));
        color: rgba(255,255,255,.95);
        font-size: 1rem;
        line-height: 1;
        text-shadow: 0 1px 2px rgba(116,82,151,.25);
        box-shadow: 0 2px 5px rgba(116,82,151,.18);
        transform: rotate(var(--rot, 0deg));
    }

    .slip.slip-new {
        animation: slipDrop 1s cubic-bezier(.3, 1.35, .5, 1) both;
    }

    .jar-label {
        position: absolute;
        left: 50%;
        top: 42%;
        z-index: 2;
        padding: .45rem 1.1rem;
        border-radius: 12px;
        background: linear-gradient(145deg, #fffdf6, #fff1d9);
        border: 1px solid #f0dcb4;
        box-shadow: 0 3px 9px rgba(116,82,151,.14);
        transform: translate(-50%, -50%) rotate(-3deg);
        text-align: center;
        font-family: var(--font-display);
        font-size: 1.05rem;
        font-weight: 600;
        color: #a06f3b;
        white-space: nowrap;
    }

    .jar-label small {
        display: block;
        font-family: 'Nunito', sans-serif;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .08em;
        color: #c09a63;
    }

    .jar-empty {
        position: absolute;
        left: 0;
        right: 0;
        top: 64%;
        text-align: center;
        color: #b9a1cf;
        font-size: .95rem;
        font-weight: 700;
        line-height: 1.6;
    }

    /* ---------- MUSIC CORNER ---------- */
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    @keyframes eqBounce {
        0%, 100% { transform: scaleY(.25); }
        50%      { transform: scaleY(1); }
    }

    .track-card {
        position: relative;
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.1rem 1.1rem 1.1rem 1rem;
        margin: .5rem 0 .6rem;
        background:
            radial-gradient(circle at 1px 1px, rgba(152,106,184,.10) 1px, transparent 0) 0 0 / 16px 16px,
            linear-gradient(145deg, rgba(255,255,255,.95), rgba(255,255,255,.7));
        border: 1px solid rgba(220,198,243,.9);
        border-radius: 26px;
        box-shadow: 0 8px 22px rgba(116,82,151,.08);
        transform: rotate(var(--tilt, 0deg));
        transition: transform .25s ease, box-shadow .25s ease;
    }

    .track-card:hover {
        transform: translateY(-3px) rotate(var(--tilt, 0deg));
        box-shadow: 0 13px 28px rgba(116,82,151,.15);
    }

    .track-card.is-playing {
        border-color: #b58be8;
        box-shadow: 0 0 0 3px rgba(181,139,232,.25), 0 10px 26px rgba(116,82,151,.14);
    }

    .track-cover {
        position: relative;
        flex: 0 0 116px;
        height: 96px;
    }

    .cover-art {
        position: absolute;
        top: 0; left: 0;
        z-index: 2;
        display: grid;
        place-items: center;
        width: 92px;
        height: 92px;
        font-size: 2.6rem;
        border-radius: 22px;
        background: linear-gradient(135deg, var(--c1), var(--c2));
        box-shadow: 0 6px 14px rgba(116,82,151,.18), inset 0 0 0 3px rgba(255,255,255,.55);
    }

    .vinyl {
        position: absolute;
        top: 6px;
        right: 0;
        z-index: 1;
        width: 84px;
        height: 84px;
        border-radius: 50%;
        background: repeating-radial-gradient(circle at center, #43365a 0 2px, #54456f 2px 4px);
        box-shadow: 0 4px 10px rgba(60,40,90,.25);
        display: grid;
        place-items: center;
        transition: right .4s ease;
    }

    .track-card:hover .vinyl,
    .track-card.is-playing .vinyl {
        right: -12px;
    }

    .track-card.is-playing .vinyl {
        animation: spin 3s linear infinite;
    }

    .vinyl-label {
        position: relative;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--c1), var(--c2));
    }

    .vinyl-label:after {
        content: "";
        position: absolute;
        top: 50%; left: 50%;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #43365a;
        transform: translate(-50%, -50%);
    }

    .track-info {
        flex: 1;
        min-width: 0;
    }

    .track-title {
        font-family: var(--font-display);
        color: #6b4d8a;
        font-size: 1.2rem;
        font-weight: 600;
        line-height: 1.25;
    }

    .track-desc {
        color: #88749a;
        font-size: .92rem;
        line-height: 1.5;
        margin: .15rem 0 .5rem;
    }

    .chips {
        display: flex;
        flex-wrap: wrap;
        gap: .35rem;
    }

    .chip {
        padding: .18rem .6rem;
        border-radius: 999px;
        background: linear-gradient(135deg, var(--c1), var(--c2));
        color: #5d4678;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .02em;
    }

    .playing-badge {
        position: absolute;
        top: -11px;
        right: 18px;
        padding: .2rem .75rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #c9a7f5, #b58be8);
        color: #fff;
        font-size: .72rem;
        font-weight: 900;
        letter-spacing: .05em;
        box-shadow: 0 4px 10px rgba(153,112,202,.3);
    }

    .now-card {
        position: relative;
        text-align: center;
        padding: 1.6rem 1rem 1.3rem;
        margin: .4rem 0 .8rem;
        border-radius: 28px;
        border: 1px solid rgba(220,198,243,.9);
        background:
            radial-gradient(ellipse at 20% 0%, rgba(255,255,255,.7), transparent 60%),
            linear-gradient(145deg, var(--c1), var(--c2));
        box-shadow: 0 10px 26px rgba(116,82,151,.13);
    }

    .now-vinyl {
        width: 128px;
        height: 128px;
        margin: 0 auto .9rem;
        border-radius: 50%;
        display: grid;
        place-items: center;
        background: repeating-radial-gradient(circle at center, #43365a 0 2px, #54456f 2px 4px);
        box-shadow: 0 8px 18px rgba(60,40,90,.28);
        animation: spin 4s linear infinite;
    }

    .now-vinyl .vinyl-label {
        width: 46px;
        height: 46px;
    }

    .now-kicker {
        color: #7a5f99;
        font-size: .72rem;
        font-weight: 900;
        letter-spacing: .18em;
    }

    .now-title {
        font-family: var(--font-display);
        color: #5d4678;
        font-size: 1.45rem;
        font-weight: 600;
        line-height: 1.25;
        margin: .2rem 0;
    }

    .now-desc {
        color: #7a6590;
        font-size: .95rem;
        line-height: 1.5;
        margin-bottom: .8rem;
    }

    .eq {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 4px;
        height: 26px;
    }

    .eq span {
        width: 5px;
        height: 100%;
        border-radius: 3px;
        background: #9874c1;
        transform-origin: bottom;
        animation: eqBounce 1s ease-in-out infinite;
    }

    .eq span:nth-child(2) { animation-delay: .15s; }
    .eq span:nth-child(3) { animation-delay: .3s; }
    .eq span:nth-child(4) { animation-delay: .45s; }
    .eq span:nth-child(5) { animation-delay: .6s; }

    .recent-row {
        margin: .2rem 0 1rem;
        color: #8c76a1;
        font-size: .85rem;
        font-weight: 800;
    }

    .recent-row .chip {
        margin-left: .3rem;
    }

    @media (max-width: 768px) {
        .track-cover { flex-basis: 96px; height: 80px; }
        .cover-art   { width: 76px; height: 76px; font-size: 2.1rem; }
        .vinyl       { width: 70px; height: 70px; }
        .track-title { font-size: 1.05rem; }
    }

    @media (prefers-reduced-motion: reduce) {
        .track-card.is-playing .vinyl,
        .now-vinyl,
        .eq span {
            animation: none !important;
        }
    }

    /* ---------- INPUTS ---------- */
    [data-testid="stSelectbox"] label,
    [data-testid="stTextInput"] label,
    [data-testid="stRadio"] > label {
        color: #72568b;
        font-weight: 800;
        font-size: 1rem;
    }

    [data-baseweb="select"] > div {
        background: rgba(255,255,255,.9);
        border: 1px solid #dfcdf2;
        border-radius: 16px;
        min-height: 3.15rem;
    }

    [data-testid="stTextInput"] input {
        background: rgba(255,255,255,.9);
        border: 1px solid #dfcdf2;
        border-radius: 15px;
        min-height: 3rem;
    }

    /* ---------- BUTTONS ---------- */
    .stButton > button,
    .stLinkButton > a,
    .stDownloadButton > button,
    [data-testid="stFormSubmitButton"] button {
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,.75);
        background: linear-gradient(135deg, #c9a7f5 0%, #b58be8 50%, #d6b4f7 100%);
        color: #ffffff;
        font-family: 'Nunito', sans-serif;
        font-size: 1rem;
        font-weight: 900;
        padding: .72rem 1.3rem;
        min-height: 2.9rem;
        box-shadow: 0 5px 14px rgba(153,112,202,.20);
        transition: background .22s ease, border-color .22s ease,
                    box-shadow .22s ease, transform .22s ease;
    }

    .stButton > button:hover,
    .stLinkButton > a:hover,
    .stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #b58be8 0%, #a47bd8 100%);
        border-color: #d9c0f5;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(142,96,190,.28);
    }

    .stButton > button:active,
    .stLinkButton > a:active,
    .stDownloadButton > button:active,
    [data-testid="stFormSubmitButton"] button:active {
        transform: translateY(0);
        box-shadow: 0 3px 8px rgba(142,96,190,.18);
    }

    .stButton > button:focus-visible,
    .stLinkButton > a:focus-visible,
    .stDownloadButton > button:focus-visible,
    [data-testid="stFormSubmitButton"] button:focus-visible {
        outline: 3px solid rgba(181,139,232,.45);
        outline-offset: 3px;
    }

    /* ---------- TAB NAVIGATION ---------- */
    [data-testid="stTabs"] {
        margin-top: 1.4rem;
    }

    [data-testid="stTabs"] [role="tablist"] {
        display: flex;
        flex-wrap: wrap;
        gap: .65rem;
        padding: .65rem;
        margin: 0 0 2rem 0;
        background: rgba(255,255,255,.48);
        border: 1px solid rgba(218,198,241,.85);
        border-radius: 23px;
        box-shadow: 0 8px 25px rgba(112,78,147,.07);
    }

    [data-testid="stTabs"] [role="tab"] {
        flex: 1 1 140px;
        justify-content: center;
        gap: .45rem;
        padding: .95rem .85rem;
        min-height: 3.6rem;
        border: 1px solid transparent;
        border-radius: 17px;
        background: rgba(255,255,255,.30);
        color: #765d8e;
        font-family: 'Nunito', sans-serif;
        font-size: 1rem;
        font-weight: 900;
        white-space: nowrap;
        transition: background .2s ease, border-color .2s ease,
                    box-shadow .2s ease, transform .2s ease;
    }

    [data-testid="stTabs"] [role="tab"]:hover {
        background: rgba(255,255,255,.85);
        border-color: #e2d0f5;
        color: #62457f;
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #ffffff, #ecdefe);
        border: 1px solid #d8c0f1;
        color: #704c91;
        box-shadow: 0 5px 15px rgba(112,78,147,.13);
    }

    [data-testid="stTabs"] [role="tab"] p {
        font-size: 1rem;
        font-weight: 900;
    }

    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background-color: #b58bdf;
        height: 3px;
        border-radius: 999px;
    }

    /* ---------- FOOTER ---------- */
    .footer {
        text-align: center;
        color: #795b96;
        font-size: 1rem;
        line-height: 2;
        padding-top: 2.5rem;
        padding-bottom: 1rem;
        font-weight: 700;
    }

    .footer-support {
        max-width: 520px;
        margin: .4rem auto 0;
        color: #9a84ad;
        font-size: .88rem;
        line-height: 1.7;
        font-weight: 600;
    }

    /* ---------- MOBILE ---------- */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 1rem 2rem !important;
        }

        .hero-card {
            padding: 1.6rem 1rem;
            border-radius: 25px;
        }

        [data-testid="stTabs"] [role="tablist"] {
            gap: .4rem;
            padding: .45rem;
            border-radius: 19px;
        }

        [data-testid="stTabs"] [role="tab"] {
            flex: 1 1 115px;
            padding: .75rem .5rem;
            min-height: 3.1rem;
            font-size: .9rem;
        }

        [data-testid="stTabs"] [role="tab"] p {
            font-size: .9rem;
        }

        .joy-text {
            font-size: 1.05rem;
        }

        .jar {
            height: 300px;
        }

        .slip {
            width: 28px;
            height: 28px;
            font-size: .9rem;
        }

        .week-strip {
            gap: .3rem;
        }

        .week-day {
            border-radius: 13px;
            padding: .5rem .1rem .45rem;
        }

        .week-emoji {
            font-size: 1.4rem;
        }

        .week-name {
            font-size: .62rem;
            letter-spacing: .03em;
        }
    }

    /* ---------- RESPECT "REDUCE MOTION" ---------- */
    @media (prefers-reduced-motion: reduce) {
        .bunny, .sparkle, .joy-card.fade-in {
            animation: none !important;
        }

        .slip.slip-new,
        .jar-wrap.shake {
            animation: none !important;
        }

        .week-day:hover {
            transform: none;
        }

        .breath-stage.running .breath-ring,
        .breath-stage.running .breath-halo,
        .breath-stage.running .breath-bunny,
        .breath-stage.running .breath-label {
            animation: none !important;
        }

        .breath-stage.running .breath-label.in,
        .breath-stage.running .breath-label.hold,
        .breath-stage.running .breath-label.out,
        .breath-stage.running .breath-label.done {
            display: none;
        }

        .breath-stage.running .breath-label.static {
            opacity: 1;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================
# LITTLE JOY MESSAGES
# =============================
joy_messages = {
    "Happy ☀️": [
        "Let yourself enjoy this moment. You deserve the good things happening to you. ♡",
        "Your happiness doesn't need a reason. Let it bloom like a little flower. 🌷",
        "Notice how this feels in your body and soak it in. Good days deserve to be remembered. 🌼",
        "Share a little of this sunshine with someone today. Joy grows when it's passed along. ☀️",
        "Dance a tiny dance, even if it's just with your shoulders. You've earned it! 💃",
    ],
    "Tired ☁️": [
        "You don't have to earn your rest. You've done enough for today. 🧸",
        "It's okay to slow down. Even the moon takes its time to rise. 🌙",
        "Rest is productive too. Your body and mind do important work while you recharge. 🫖",
        "Ask yourself what the smallest comfort would be right now, then give it to yourself. ☁️",
        "You're allowed to do the bare minimum today and still be proud of yourself. 🧸",
    ],
    "A little sad 🌷": [
        "You don't have to feel okay all the time. Be gentle with yourself today. ♡",
        "This feeling is a moment in your story, not the whole story. 🌷",
        "If tears come, let them. They're just your heart making a little room. 🌧️",
        "Reach out to someone soft today, even with a tiny message. You don't have to carry this alone. ♡",
        "Be as kind to yourself as you would be to a good friend feeling this way. 🌷",
    ],
    "Excited ✨": [
        "AHH, let yourself be excited! You deserve to look forward to lovely things. ✨",
        "Keep that little spark alive. You deserve to feel excited about what's ahead. ♡",
        "Write down what you're looking forward to. Future you will love reading it. 📝",
        "That fizzy feeling is your heart saying yes. Follow it gently. 🎈",
        "Tell someone your good news. Excitement is even sweeter when it's shared. 💌",
    ],
    "Cozy 🧸": [
        "Imagine a warm blanket, a soft pillow, and absolutely nowhere you need to be. ☁️",
        "May your day be soft, your drink be warm, and your heart feel at home. 🧸",
        "Dim the lights, find your softest socks, and let the world wait for a little while. 🕯️",
        "Cozy is a perfectly good goal for today. Build your little nest and enjoy it. 🧣",
        "A good song, a warm drink, and a quiet corner. That's already a whole little holiday. ☕",
    ],
    "Anxious/Overwhelmed 🫧": [
        "One thing at a time. You only need to take the next small step. ♡",
        "Unclench your jaw, relax your shoulders, and take one slow breath. You can pause before you continue. 🫧",
        "Name five things you can see around you and let your eyes rest on each one. 🫧",
        "You don't have to solve it all right now. Just this breath, then the next one. ♡",
        "Feeling anxious doesn't mean something is wrong with you. Your mind is just trying to protect you. 🌿",
    ],
    "Bored 🍓": [
        "Your next little adventure might be something wonderfully ordinary. Try something just because it's fun. 🍓",
        "A tiny change of scenery, a favourite song, or a silly little doodle might be just what you need. 🌷",
        "Send a friend a silly photo or a song you like. Tiny connections brighten days. 💌",
        "Rearrange one little corner of your room and see how it feels. 🪴",
        "Learn one tiny new thing today, even just a single word in another language. ✨",
    ],
}

# =============================
# AFFIRMATIONS
# =============================
affirmations = [
    "I am allowed to grow at my own pace. 🌱",
    "I am proud of how far I've come. ♡",
    "I don't need to have everything figured out today. ☁️",
    "I deserve kindness, especially from myself. 🌷",
    "Small steps still move me forward. 🐾",
    "I can be a work in progress and still be wonderful. ✨",
    "I am capable of learning things that feel difficult right now. 🌱",
    "My worth is not measured by my productivity. 🧸",
    "Good things are allowed to happen to me. ☀️",
    "I can make room for both ambition and rest. ♡",
    "I am allowed to take up space and ask for what I need. 🌸",
    "I can start again as many times as I need to. 🌅",
    "I trust myself to figure things out one step at a time. 🐾",
    "My feelings are valid, even the messy ones. 🫧",
    "I am doing my best, and my best is enough. ♡",
    "I welcome small joys into my day. 🍓",
]

# =============================
# GRATITUDE JAR CONTENT
# =============================
GRATITUDE_PROMPTS = [
    "What's something small that made you smile today?",
    "Who is someone you're glad you know?",
    "What's a food or drink you really enjoyed recently?",
    "What's something your body did for you today?",
    "What's a place that makes you feel calm?",
    "What's something you're looking forward to?",
    "What's a song, show, or book you're thankful for?",
    "What's a lesson you're grateful you learned?",
    "What's something comfortable you're thankful for right now?",
    "What's a kind thing someone did for you lately?",
    "What's something in nature you noticed today?",
    "What's something about yourself you're thankful for?",
]

JAR_MILESTONES = {
    1: "Your very first slip! The jar has begun ♡",
    5: "5 slips! Your jar is getting cosy 🫙",
    10: "10 slips! Look at all that gratitude ✨",
    25: "25 slips! Your jar is glowing 🌟",
    50: "50 slips! What a beautiful habit 🌸",
    100: "100 slips! Your jar is a treasure ♡",
}

JAR_COLORS = [
    ("#ffd3eb", "#ffb3d6"),
    ("#e4d0f7", "#c9a7f5"),
    ("#d6ebff", "#a9d0f7"),
    ("#fff0b3", "#ffdf7a"),
    ("#d2f2e3", "#a5e0c4"),
    ("#ffe3cf", "#ffc59f"),
]
JAR_GLYPHS = ["♡", "✦", "★", "❀", "✿", "☁"]
JAR_MAX_VISIBLE = 60

# =============================
# DAILY INTENTIONS
# =============================
DAILY_INTENTIONS = [
    "Today I will notice one small thing that feels good.",
    "Today I will drink a glass of water and say thank you to my body.",
    "Today I will take one slow breath before I reply to anything.",
    "Today I will do one thing just because it's fun.",
    "Today I will speak to myself like I'd speak to a friend.",
    "Today I will step outside for a little fresh air.",
    "Today I will let one small thing be good enough.",
    "Today I will send one kind message to someone.",
    "Today I will take a break before I need one.",
    "Today I will celebrate one tiny win.",
    "Today I will listen to a song that makes me smile.",
    "Today I will tidy one small corner and enjoy the calm.",
    "Today I will pay attention to the colours around me.",
    "Today I will go at my own pace.",
]

# =============================
# BUNNY LEVELS (grow as you use the app)
# =============================
BUNNY_LEVELS = [
    (0, "Sleepy bunny", "😴"),
    (6, "Curious bunny", "🌱"),
    (16, "Hoppy bunny", "🥕"),
    (31, "Joyful bunny", "🌸"),
    (51, "Sparkly bunny", "✨"),
    (81, "Moonlit bunny", "🌙"),
]

# =============================
# NOTE CARD THEMES (mood colours)
# =============================
CARD_THEMES = {
    "default": dict(
        bg1="#ffffff", bg2="#fff7fc", border="#ead9f7",
        accent="#986ab8", tape="#e4d0f7", dot="rgba(152,106,184,.16)",
    ),
    "affirmation": dict(
        bg1="#fffafe", bg2="#f6e9fd", border="#e6cdf5",
        accent="#a05fbd", tape="#e8c9f6", dot="rgba(160,95,189,.16)",
    ),
    "adventure": dict(
        bg1="#fbfff2", bg2="#edf7d5", border="#d9e8a8",
        accent="#6f923a", tape="#d6e8a0", dot="rgba(111,146,58,.18)",
    ),
    "gratitude": dict(
        bg1="#fffcf2", bg2="#ffeccf", border="#f3d9a8",
        accent="#b27a2e", tape="#f6d9a0", dot="rgba(178,122,46,.18)",
    ),
}

# One palette per mood, in the SAME ORDER as joy_messages above:
# Happy, Tired, A little sad, Excited, Cozy, Anxious/Overwhelmed, Bored
mood_palettes = [
    dict(bg1="#fffdea", bg2="#fff1c2", border="#f4df9a",
         accent="#b98a10", tape="#f7e08a", dot="rgba(185,138,16,.18)"),   # Happy: butter yellow
    dict(bg1="#f4f9ff", bg2="#e0edfc", border="#c3d9f2",
         accent="#5a80b3", tape="#bad3f1", dot="rgba(90,128,179,.18)"),   # Tired: soft blue
    dict(bg1="#f7f4ff", bg2="#e9e2fa", border="#d4caef",
         accent="#7863a8", tape="#cdc1ec", dot="rgba(120,99,168,.18)"),   # A little sad: lavender
    dict(bg1="#fff6ee", bg2="#ffe1cc", border="#ffcaa9",
         accent="#d17a43", tape="#ffc9a3", dot="rgba(209,122,67,.18)"),   # Excited: peachy orange
    dict(bg1="#fffaf1", bg2="#f9e8d0", border="#eed3ae",
         accent="#a06f3b", tape="#efd0a2", dot="rgba(160,111,59,.18)"),   # Cozy: warm cream
    dict(bg1="#f2fcf9", bg2="#dcf4ed", border="#bce5da",
         accent="#4a9786", tape="#b2e2d4", dot="rgba(74,151,134,.18)"),   # Anxious: mint
    dict(bg1="#fff3f6", bg2="#ffdfe8", border="#f9c3d2",
         accent="#c75b7a", tape="#f8b7ca", dot="rgba(199,91,122,.18)"),   # Bored: strawberry pink
]

for _label, _palette in zip(joy_messages.keys(), mood_palettes):
    CARD_THEMES[_label] = _palette

TILTS = [-1.6, -1.0, -0.5, 0.5, 1.0, 1.6]


def tilt_for(seed_text):
    """A tilt that looks random but stays the same for the same text."""
    index = zlib.crc32(str(seed_text).encode("utf-8")) % len(TILTS)
    return f"{TILTS[index]}deg"


def card_style(theme, tilt):
    t = CARD_THEMES.get(theme, CARD_THEMES["default"])
    return (
        f"--tilt:{tilt};"
        f"--card-bg1:{t['bg1']};--card-bg2:{t['bg2']};"
        f"--card-border:{t['border']};--card-accent:{t['accent']};"
        f"--card-tape:{t['tape']};--card-dot:{t['dot']};"
    )


def note_card(heading, text, theme="default", tilt="0deg",
              animate=False, footer=None):
    """Build a sticky-note card (single line of HTML, no blank lines)."""
    classes = "joy-card fade-in" if animate else "joy-card"
    footer_html = (
        f'<div class="card-footer">{html.escape(footer)}</div>'
        if footer else ""
    )
    return (
        f'<div class="{classes}" style="{card_style(theme, tilt)}">'
        f'<div class="joy-heading">{html.escape(heading)}</div>'
        f'<div class="joy-text">{html.escape(text)}</div>'
        f"{footer_html}"
        f"</div>"
    )


# =============================
# TIME-OF-DAY HERO
# =============================
def get_local_now():
    """Use the visitor's timezone when Streamlit can tell us, else server time."""
    try:
        tz_name = st.context.timezone
        if tz_name:
            return datetime.now(ZoneInfo(tz_name))
    except Exception:
        pass
    return datetime.now()


def get_time_theme():
    hour = get_local_now().hour

    if 5 <= hour < 12:
        return dict(
            greeting="Good morning, sunshine ☀️",
            note="a gentle start to a lovely day ✧",
            a="rgba(255,233,170,.80)", b="rgba(255,205,222,.60)",
            c1="#fffdf4", c2="#fff8ec", c3="#fff4f7",
        )
    if 12 <= hour < 17:
        return dict(
            greeting="Hello, little ray of light 🌤️",
            note="you're doing better than you think ✧",
            a="rgba(190,230,255,.65)", b="rgba(255,225,200,.60)",
            c1="#fbfdff", c2="#f3faff", c3="#fff8f4",
        )
    if 17 <= hour < 21:
        return dict(
            greeting="Soft evening vibes 🌇",
            note="time to slow down and unwind ✧",
            a="rgba(255,196,170,.70)", b="rgba(214,190,255,.70)",
            c1="#fff8f5", c2="#fdf0fa", c3="#f5efff",
        )
    return dict(
        greeting="Cozy night, gentle heart 🌙",
        note="you made it through today ✧",
        a="rgba(170,178,255,.60)", b="rgba(218,182,255,.65)",
        c1="#f1efff", c2="#e9e6fb", c3="#f2eaff",
    )


def todays_intention():
    """One intention per day, the same all day long."""
    day_number = get_local_now().date().toordinal()
    return DAILY_INTENTIONS[day_number % len(DAILY_INTENTIONS)]


# =============================
# BUNNY LEVEL HELPERS
# =============================
def joy_points():
    """Points come from the little things you do in the app."""
    s = st.session_state
    return (
        len(s["favourites"])
        + 2 * len(s["mood_log"])
        + 2 * len(s["completed_adventures"])
        + 2 * len(s["gratitude_jar"])
        + 2 * s["breath_sessions"]
        + len(s["music_favs"])
    )


def bunny_level(points):
    level_index = 0
    for i, (threshold, _name, _emoji) in enumerate(BUNNY_LEVELS):
        if points >= threshold:
            level_index = i

    threshold, name, emoji = BUNNY_LEVELS[level_index]

    if level_index + 1 < len(BUNNY_LEVELS):
        next_threshold, next_name, next_emoji = BUNNY_LEVELS[level_index + 1]
        span = next_threshold - threshold
        percent = int(100 * (points - threshold) / span)
        note = (
            f"{next_threshold - points} more joy points until "
            f"{next_name.lower()} {next_emoji}"
        )
    else:
        percent = 100
        note = "your bunny is the happiest bunny in the meadow ♡"

    return dict(name=name, emoji=emoji, percent=percent, note=note)


def build_hero_html():
    """The hero card. Built last so the bunny level is always up to date."""
    time_theme = get_time_theme()
    hero_style = (
        f"--hero-a:{time_theme['a']};--hero-b:{time_theme['b']};"
        f"--hero-c1:{time_theme['c1']};--hero-c2:{time_theme['c2']};"
        f"--hero-c3:{time_theme['c3']};"
    )

    points = joy_points()
    level = bunny_level(points)

    sparkles_html = "".join(
        f'<span class="sparkle" style="top:{top};left:{left};'
        f'font-size:{size};animation-delay:{delay};">{char}</span>'
        for char, top, left, size, delay in SPARKLES
    )

    return (
        f'<div class="hero-card" style="{hero_style}">'
        f"{sparkles_html}"
        '<div class="bunny-wrap"><span class="bunny">🐰</span></div>'
        '<div class="eyebrow">YOUR LITTLE CORNER OF CALM</div>'
        '<div class="hero-title">Little Joy ♡</div>'
        '<div class="hero-subtitle">a tiny pocket of happiness, just for you</div>'
        f'<div class="hero-greeting">{time_theme["greeting"]}</div>'
        f'<div class="hero-note">{time_theme["note"]}</div>'
        '<div class="hero-level">'
        f'<span class="level-pill">{level["emoji"]} {html.escape(level["name"])}</span>'
        f'<span class="level-points">{points} joy points</span>'
        "</div>"
        f'<div class="level-bar"><span style="width:{level["percent"]}%;"></span></div>'
        f'<div class="level-next">{html.escape(level["note"])}</div>'
        "</div>"
    )


# =============================
# MOOD DIARY HELPERS
# =============================
# A rough "brightness" for each mood, only used to draw the little trend line.
# 5 = bright and energised, 1 = a tougher day.
MOOD_SCORES = {
    "Happy ☀️": 5,
    "Excited ✨": 5,
    "Cozy 🧸": 4,
    "Bored 🍓": 3,
    "Tired ☁️": 2,
    "A little sad 🌷": 2,
    "Anxious/Overwhelmed 🫧": 1,
}


def mood_emoji(label):
    """'Happy ☀️' -> '☀️'"""
    return label.rsplit(" ", 1)[-1]


def pretty_date(day):
    return f"{day.strftime('%a')} {day.day} {day.strftime('%b')}"


def pretty_iso(iso_text):
    """'2026-10-27' -> 'Tue 27 Oct'"""
    try:
        return pretty_date(datetime.strptime(iso_text, "%Y-%m-%d").date())
    except ValueError:
        return iso_text


def week_strip_html(week, by_date, today):
    """Seven little emoji tiles, one per day (single-line HTML pieces)."""
    cells = []

    for day in week:
        entry = by_date.get(day.isoformat())
        today_class = " is-today" if day == today else ""
        name = day.strftime("%a")
        number = str(day.day)

        if entry:
            theme = CARD_THEMES.get(entry["mood"], CARD_THEMES["default"])
            style = (
                f"background:linear-gradient(145deg,{theme['bg1']},{theme['bg2']});"
                f"border-color:{theme['border']};"
            )
            tip = entry["mood"]
            if entry.get("note"):
                tip += f" - {entry['note']}"
            cells.append(
                f'<div class="week-day{today_class}" style="{style}" '
                f'title="{html.escape(tip)}">'
                f'<div class="week-name">{name}</div>'
                f'<div class="week-emoji">{mood_emoji(entry["mood"])}</div>'
                f'<div class="week-date">{number}</div>'
                f"</div>"
            )
        else:
            cells.append(
                f'<div class="week-day empty{today_class}" '
                f'title="No check-in yet">'
                f'<div class="week-name">{name}</div>'
                f'<div class="week-emoji">·</div>'
                f'<div class="week-date">{number}</div>'
                f"</div>"
            )

    return (
        '<div class="week-card">'
        '<div class="week-card-title">Your week in moods 🌈</div>'
        f'<div class="week-strip">{"".join(cells)}</div>'
        "</div>"
    )


def current_streak(by_date, today):
    """Consecutive days checked in. Today not logged yet? Count from yesterday."""
    day = today if today.isoformat() in by_date else today - timedelta(days=1)
    streak = 0
    while day.isoformat() in by_date:
        streak += 1
        day -= timedelta(days=1)
    return streak


# =============================
# GRATITUDE JAR HELPERS
# =============================
def jar_html(entries, animate_last=False, shaking=False):
    """The glass jar, filled with little coloured slips (single-line HTML)."""
    shown = entries[-JAR_MAX_VISIBLE:]
    slips = []

    for i, entry in enumerate(shown):
        seed = zlib.crc32((entry["text"] + entry["date"]).encode("utf-8"))
        c1, c2 = JAR_COLORS[seed % len(JAR_COLORS)]
        glyph = JAR_GLYPHS[(seed >> 4) % len(JAR_GLYPHS)]
        rotation = (seed >> 8) % 50 - 25
        is_new = animate_last and i == len(shown) - 1
        slips.append(
            f'<span class="slip{" slip-new" if is_new else ""}" '
            f'style="--c1:{c1};--c2:{c2};--rot:{rotation}deg;">{glyph}</span>'
        )

    count = len(entries)
    count_text = f"{count} slip{'s' if count != 1 else ''}"
    empty_html = (
        ""
        if entries
        else '<div class="jar-empty">your jar is waiting<br>for its first little slip ♡</div>'
    )

    return (
        f'<div class="jar-wrap{" shake" if shaking else ""}">'
        '<div class="jar-lid"></div>'
        '<div class="jar-neck"></div>'
        '<div class="jar">'
        f"{empty_html}"
        f'<div class="jar-label">grateful ♡<small>{count_text}</small></div>'
        f'{"".join(slips)}'
        "</div></div>"
    )


def new_prompt():
    options = [p for p in GRATITUDE_PROMPTS if p != st.session_state["jar_prompt"]]
    st.session_state["jar_prompt"] = random.choice(options)


def shake_jar():
    jar = st.session_state["gratitude_jar"]
    if not jar:
        return
    pool = [e for e in jar if e != st.session_state["jar_pulled"]] or jar
    st.session_state["jar_pulled"] = random.choice(pool)
    st.session_state["jar_shaking"] = True


def remove_slip(index):
    jar = st.session_state["gratitude_jar"]
    if 0 <= index < len(jar):
        removed = jar.pop(index)
        if st.session_state["jar_pulled"] == removed:
            st.session_state["jar_pulled"] = None


def empty_jar():
    st.session_state["gratitude_jar"] = []
    st.session_state["jar_pulled"] = None


def jar_export_text(jar):
    lines = ["My Gratitude Jar ♡", ""]
    for entry in jar:
        lines.append(f"{entry['date']}  -  {entry['text']}")
    return "\n".join(lines)


# =============================
# BREATHING BUDDY HELPER
# =============================
# Pattern: in 4s + hold 4s + out 6s = 14s per breath.
# (If you change these, update the keyframe percentages in the CSS too.)
BREATH_CYCLE_SECONDS = 14

BREATHING_LENGTHS = {
    "About 1 minute": 4,
    "About 2 minutes": 9,
    "About 3 minutes": 13,
}


def breathing_stage(active, cycles):
    """Build the breathing circle (single-line HTML pieces, no blank lines)."""
    if active:
        state = "running"
        style = (
            f"--cycles:{int(cycles)};"
            f"--done-delay:{int(cycles) * BREATH_CYCLE_SECONDS}s;"
        )
    else:
        state = "idle"
        style = ""

    return (
        '<div class="breath-card">'
        f'<div class="breath-stage {state}" style="{style}">'
        '<div class="breath-halo"></div>'
        '<div class="breath-ring"></div>'
        '<div class="breath-center">'
        '<div class="breath-bunny">🐰</div>'
        '<div class="breath-labels">'
        '<span class="breath-label ready">Ready when you are</span>'
        '<span class="breath-label in">Breathe in</span>'
        '<span class="breath-label hold">Hold</span>'
        '<span class="breath-label out">Breathe out</span>'
        '<span class="breath-label done">All done ♡</span>'
        '<span class="breath-label static">Breathe slowly</span>'
        "</div></div></div>"
        '<div class="breath-pattern">in for 4 · hold for 4 · out for 6</div>'
        "</div>"
    )


# =============================
# MUSIC CORNER DATA & HELPERS
# =============================
MUSIC_MOODS = [
    "Calm & Cozy ☁️",
    "Happy & Uplifting ☀️",
    "Late-Night Feelings 🌙",
    "Focus & Study 📚",
]

# Cover colours for each mood (also used for playlists people add themselves).
MOOD_COVERS = {
    "Calm & Cozy ☁️":         ("#d6ebff", "#e8dcff"),
    "Happy & Uplifting ☀️":   ("#fff0b3", "#ffd8e6"),
    "Late-Night Feelings 🌙": ("#c8c5f4", "#ecc8f2"),
    "Focus & Study 📚":       ("#d2f2e3", "#e4f1c3"),
}

COVER_EMOJIS = ["🎧", "🎹", "🌙", "🌷", "🍓", "☁️", "✨", "🧸", "🐰", "🎸", "☀️", "📚"]

# To add a built-in playlist, copy one of these dicts. "id" must be unique.
BUILT_IN_TRACKS = [
    dict(
        id="peaceful-piano", title="Peaceful Piano", emoji="🎹",
        desc="Soft piano music for quiet moments.",
        vibes=["slow mornings", "deep breaths", "gentle resets"],
        moods=["Calm & Cozy ☁️", "Focus & Study 📚"],
        url="https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO",
        c1="#d6ebff", c2="#e8dcff", custom=False,
    ),
    dict(
        id="lofi-beats", title="Lo-Fi Beats", emoji="☕",
        desc="Relaxed beats for studying or unwinding.",
        vibes=["rainy windows", "warm drinks", "quiet focus"],
        moods=["Calm & Cozy ☁️", "Focus & Study 📚"],
        url="https://open.spotify.com/playlist/37i9dQZF1DWWQRwui0ExPn",
        c1="#ffe3cf", c2="#f4d9f5", custom=False,
    ),
    dict(
        id="mood-booster", title="Mood Booster", emoji="🌻",
        desc="An upbeat playlist to lift your mood.",
        vibes=["sunshine", "little wins", "main-character energy"],
        moods=["Happy & Uplifting ☀️"],
        url="https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0",
        c1="#fff0b3", c2="#ffd8e6", custom=False,
    ),
    dict(
        id="chill-hits", title="Chill Hits", emoji="🌙",
        desc="Chill music for a late-night atmosphere.",
        vibes=["city lights", "midnight thoughts", "soft feelings"],
        moods=["Late-Night Feelings 🌙"],
        url="https://open.spotify.com/playlist/37i9dQZF1DX0SM0LYsmbMT",
        c1="#c8c5f4", c2="#ecc8f2", custom=False,
    ),
]


def all_tracks():
    return BUILT_IN_TRACKS + st.session_state["my_playlists"]


def find_track(track_id):
    return next((t for t in all_tracks() if t["id"] == track_id), None)


def play_track(track_id):
    st.session_state["now_playing"] = track_id
    recent = [r for r in st.session_state["music_recent"] if r != track_id]
    st.session_state["music_recent"] = ([track_id] + recent)[:5]


def stop_track():
    st.session_state["now_playing"] = None


def toggle_fav(track_id):
    favs = st.session_state["music_favs"]
    if track_id in favs:
        favs.remove(track_id)
    else:
        favs.append(track_id)


def surprise_track():
    choice = random.choice(all_tracks())
    play_track(choice["id"])


def remove_playlist(track_id):
    st.session_state["my_playlists"] = [
        t for t in st.session_state["my_playlists"] if t["id"] != track_id
    ]
    st.session_state["music_favs"] = [
        f for f in st.session_state["music_favs"] if f != track_id
    ]
    st.session_state["music_recent"] = [
        r for r in st.session_state["music_recent"] if r != track_id
    ]
    if st.session_state["now_playing"] == track_id:
        st.session_state["now_playing"] = None


def music_card_html(track, playing):
    """A vinyl-record playlist card (single-line HTML pieces, no blank lines)."""
    chips = "".join(
        f'<span class="chip">{html.escape(v)}</span>' for v in track["vibes"]
    )
    badge = '<div class="playing-badge">♪ now playing</div>' if playing else ""
    return (
        f'<div class="track-card{" is-playing" if playing else ""}" '
        f'style="--c1:{track["c1"]};--c2:{track["c2"]};'
        f'--tilt:{tilt_for(track["id"])};">'
        f"{badge}"
        '<div class="track-cover">'
        '<div class="vinyl"><div class="vinyl-label"></div></div>'
        f'<div class="cover-art">{html.escape(track["emoji"])}</div>'
        "</div>"
        '<div class="track-info">'
        f'<div class="track-title">{html.escape(track["title"])}</div>'
        f'<div class="track-desc">{html.escape(track["desc"])}</div>'
        f'<div class="chips">{chips}</div>'
        "</div></div>"
    )


def now_playing_html(track):
    return (
        f'<div class="now-card" style="--c1:{track["c1"]};--c2:{track["c2"]};">'
        '<div class="now-vinyl"><div class="vinyl-label"></div></div>'
        '<div class="now-kicker">NOW PLAYING</div>'
        f'<div class="now-title">{html.escape(track["emoji"])} '
        f'{html.escape(track["title"])}</div>'
        f'<div class="now-desc">{html.escape(track["desc"])}</div>'
        '<div class="eq"><span></span><span></span><span></span>'
        "<span></span><span></span></div>"
        "</div>"
    )


# =============================
# SPOTIFY EMBED HELPER
# =============================
def get_spotify_embed_url(url):
    """Convert a Spotify content URL to a safe embed URL."""
    if not isinstance(url, str):
        return None

    parsed = urlparse(url.strip())

    # Only accept Spotify's official domain over https.
    if parsed.scheme != "https" or parsed.hostname not in {
        "open.spotify.com",
        "www.open.spotify.com",
    }:
        return None

    parts = [part for part in parsed.path.split("/") if part]

    # Allow an optional locale prefix such as /intl-fr/
    if parts and parts[0].startswith("intl-"):
        parts = parts[1:]

    supported_types = {
        "track", "album", "playlist",
        "artist", "show", "episode",
    }

    if len(parts) != 2:
        return None

    content_type, content_id = parts

    if content_type not in supported_types or not content_id:
        return None

    # Keep the ID restricted to ordinary Spotify ID characters.
    if not content_id.replace("-", "").replace("_", "").isalnum():
        return None

    return f"https://open.spotify.com/embed/{content_type}/{content_id}"


# =============================
# HERO SECTION
# =============================
SPARKLES = [
    ("✧", "18px", "6%", "2rem", "0s"),
    ("✦", "58%", "3%", "1.1rem", "0.8s"),
    ("⋆", "12%", "24%", "1.3rem", "1.4s"),
    ("✦", "16px", "82%", "1.2rem", "0.4s"),
    ("✧", "46%", "92%", "1.6rem", "1.1s"),
    ("♡", "80%", "88%", "1.6rem", "1.7s"),
    ("✧", "80%", "8%", "1.5rem", "2.0s"),
]

# The hero is filled in at the very bottom of the script, so the bunny level
# always reflects what you did during this run.
hero_slot = st.empty()

# =============================
# TABS
# =============================
(
    joy_tab,
    diary_tab,
    breathe_tab,
    affirmation_tab,
    jar_tab,
    music_tab,
    collection_tab,
    adventure_tab,
) = st.tabs(
    [
        "☀️ Little Joy",
        "📔 Mood Diary",
        "🫧 Breathing Buddy",
        "🌷 Affirmations",
        "🫙 Gratitude Jar",
        "🎧 Music Corner",
        "♡ My Collection",
        "🍓 Tiny Adventures",
    ]
)

# =============================
# TAB 1: LITTLE JOY
# =============================
with joy_tab:
    st.markdown(
        '<div class="section-title">How are you feeling? ♡</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tiny-note">Pick whatever feels closest to your heart.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.5, 1], gap="large")

    with left:
        mood = st.selectbox(
            "Choose your mood",
            list(joy_messages.keys()),
            label_visibility="collapsed",
            key="mood_picker",
        )

        just_generated = False

        if st.button(
            "Give me a little joy ✨",
            key="generate_joy",
            use_container_width=True,
        ):
            # Avoid showing the exact same note twice in a row.
            joy_options = [
                m for m in joy_messages[mood]
                if m != st.session_state["current_joy"]
            ] or joy_messages[mood]
            st.session_state["current_joy"] = random.choice(joy_options)
            st.session_state["current_joy_mood"] = mood
            just_generated = True

        if st.session_state["current_joy"]:
            joy_text = st.session_state["current_joy"]
            joy_mood = st.session_state["current_joy_mood"]

            st.markdown(
                note_card(
                    "A little note for you ♡",
                    joy_text,
                    theme=joy_mood,
                    tilt=tilt_for(joy_text),
                    animate=just_generated,
                    footer=joy_mood,
                ),
                unsafe_allow_html=True,
            )

            if st.button("♡ Save to My Collection", key="save_joy"):
                item = {
                    "type": "Little Joy",
                    "text": joy_text,
                    "mood": joy_mood,
                }

                if item not in st.session_state["favourites"]:
                    st.session_state["favourites"].append(item)
                    st.toast("Saved to your little collection! ♡")
                else:
                    st.toast("This little joy is already saved! ♡")
        else:
            # Empty card previews the colour of the mood you've selected.
            st.markdown(
                note_card(
                    "A little space just for you 🌷",
                    "Choose the feeling that fits today, then let a small "
                    "note find its way to you. There's no wrong way to feel. ♡",
                    theme=mood,
                    tilt="-1deg",
                ),
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            f"""
            <div class="mini-card">
                <div class="mini-card-title">🌞 Today's little intention</div>
                <div class="mini-card-text">{html.escape(todays_intention())}</div>
            </div>
            <div class="mini-card">
                <div class="mini-card-title">☁️ A soft reminder</div>
                <div class="mini-card-text">
                    Whatever you're feeling, you don't have to rush
                    through it. Give yourself a little room to be.
                </div>
            </div>
            <div class="mini-card">
                <div class="mini-card-title">🌷 A tiny pause</div>
                <div class="mini-card-text">
                    Relax your shoulders, take a slow breath,
                    and let this moment be enough.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Gentle nudge towards the Breathing Buddy for this mood.
        if mood == "Anxious/Overwhelmed 🫧":
            st.markdown(
                """
                <div class="mini-card">
                    <div class="mini-card-title">🫧 Try the Breathing Buddy</div>
                    <div class="mini-card-text">
                        Feeling overwhelmed? Open the Breathing Buddy tab
                        and breathe along with the little bunny. ♡
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# =============================
# TAB 2: MOOD DIARY
# =============================
with diary_tab:
    # Toast from the check-in that was just saved (shown after the rerun).
    if st.session_state["diary_saved"]:
        st.session_state["diary_saved"] = False
        st.toast("Check-in saved! Thank you for checking in with yourself ♡")

    today = get_local_now().date()
    mood_log = st.session_state["mood_log"]
    by_date = {entry["date"]: entry for entry in mood_log}
    week = [today - timedelta(days=offset) for offset in range(6, -1, -1)]

    st.markdown(
        '<div class="section-title">Mood diary 📔</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tiny-note">A tiny daily check-in. Log how you feel, '
        'add a line if you like, and watch your week take shape. ♡</div>',
        unsafe_allow_html=True,
    )

    # ----- Weekly mood strip -----
    st.markdown(
        week_strip_html(week, by_date, today),
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.5, 1], gap="large")

    # ----- Check-in -----
    with left:
        todays_entry = by_date.get(today.isoformat())

        if todays_entry:
            st.markdown(
                note_card(
                    "Today's check-in ♡",
                    todays_entry["note"]
                    or "No note today, and that's perfectly okay.",
                    theme=todays_entry["mood"],
                    tilt=tilt_for(todays_entry["mood"] + todays_entry["note"]),
                    footer=todays_entry["mood"],
                ),
                unsafe_allow_html=True,
            )
            st.caption("Checked in already? Saving again will update today's entry.")
        else:
            st.markdown(
                note_card(
                    "How's today going? 🌷",
                    "Pick the mood that fits best right now. You can add "
                    "a single line about your day if you'd like. ♡",
                    theme="default",
                    tilt="-1deg",
                ),
                unsafe_allow_html=True,
            )

        with st.form("mood_checkin_form", clear_on_submit=True):
            diary_mood = st.selectbox(
                "How are you feeling today?",
                list(joy_messages.keys()),
                key="diary_mood",
            )
            diary_note = st.text_input(
                "One line about today (optional)",
                max_chars=120,
                placeholder="e.g. a quiet walk made me smile",
                key="diary_note",
            )
            diary_submit = st.form_submit_button(
                "Save today's check-in ♡",
                use_container_width=True,
            )

        if diary_submit:
            today_iso = today.isoformat()
            new_entry = {
                "date": today_iso,
                "mood": diary_mood,
                "note": diary_note.strip(),
            }

            updated_log = [e for e in mood_log if e["date"] != today_iso]
            updated_log.append(new_entry)
            updated_log.sort(key=lambda e: e["date"])

            st.session_state["mood_log"] = updated_log
            st.session_state["diary_saved"] = True
            st.rerun()

    # ----- Stats and trend -----
    with right:
        logged_this_week = sum(1 for day in week if day.isoformat() in by_date)
        streak = current_streak(by_date, today)

        stat1, stat2 = st.columns(2)
        stat1.metric("This week", f"{logged_this_week} / 7")
        stat2.metric("Streak 🌱", f"{streak} day{'s' if streak != 1 else ''}")

        st.markdown(
            '<div class="mini-card">'
            '<div class="mini-card-title">📈 Your mood trend</div>'
            '<div class="mini-card-text">'
            "A rough picture of your week. Higher means a brighter day, "
            "lower means a tougher one. Both are completely okay. ♡"
            "</div></div>",
            unsafe_allow_html=True,
        )

        if logged_this_week >= 2:
            scores = [
                MOOD_SCORES[by_date[day.isoformat()]["mood"]]
                if day.isoformat() in by_date
                else None
                for day in week
            ]
            trend = pd.DataFrame(
                {"Mood level": scores},
                index=pd.to_datetime(week),
            )
            st.line_chart(trend, height=220, color="#b58be8")
        else:
            st.caption(
                "Check in on 2 or more days this week and your trend "
                "line will appear here. 🌱"
            )

    # ----- Recent check-ins -----
    st.markdown(
        '<div class="section-title" style="font-size:1.5rem;">'
        "Recent check-ins 🍓</div>",
        unsafe_allow_html=True,
    )

    if not mood_log:
        st.caption("Nothing here yet. Your check-ins will gather here. ♡")
    else:
        for entry in reversed(mood_log[-5:]):
            entry_day = datetime.strptime(entry["date"], "%Y-%m-%d").date()

            st.markdown(
                note_card(
                    entry["mood"],
                    entry["note"] or "No note for this day.",
                    theme=entry["mood"],
                    tilt=tilt_for(entry["date"]),
                    footer=pretty_date(entry_day),
                ),
                unsafe_allow_html=True,
            )

        diary_btn1, diary_btn2 = st.columns(2)

        with diary_btn1:
            st.download_button(
                "Download my diary 📥",
                data=pd.DataFrame(mood_log).to_csv(index=False),
                file_name="my_mood_diary.csv",
                mime="text/csv",
                key="download_diary",
                use_container_width=True,
            )

        with diary_btn2:
            if st.button("Clear my diary", key="clear_diary", use_container_width=True):
                st.session_state["mood_log"] = []
                st.rerun()

# =============================
# TAB 3: BREATHING BUDDY
# =============================
with breathe_tab:
    st.markdown(
        '<div class="section-title">Breathing buddy 🫧</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tiny-note">Breathe along with the little circle. '
        'It grows as you breathe in and softens as you breathe out. ♡</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.5, 1], gap="large")

    with left:
        breathing_active = st.session_state["breathing_active"]

        st.markdown(
            breathing_stage(
                breathing_active,
                st.session_state["breathing_cycles"],
            ),
            unsafe_allow_html=True,
        )

        breathing_length = st.radio(
            "How long would you like to breathe for?",
            list(BREATHING_LENGTHS.keys()),
            horizontal=True,
            key="breathing_length",
            disabled=breathing_active,
        )

        if not breathing_active:
            if st.button(
                "Start breathing 🫧",
                key="start_breathing",
                use_container_width=True,
            ):
                st.session_state["breathing_cycles"] = BREATHING_LENGTHS[
                    breathing_length
                ]
                st.session_state["breathing_active"] = True
                st.session_state["breath_sessions"] += 1
                st.rerun()
        else:
            if st.button(
                "Stop & reset ■",
                key="stop_breathing",
                use_container_width=True,
            ):
                st.session_state["breathing_active"] = False
                st.rerun()

    with right:
        st.markdown(
            note_card(
                "How it works 🌿",
                "Breathe in slowly for 4, hold gently for 4, then let it "
                "all out for 6. A longer breath out than in is a simple "
                "way to help your body slow down.",
                theme="Anxious/Overwhelmed 🫧",
                tilt="1deg",
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="mini-card">
                <div class="mini-card-title">☁️ Go at your own pace</div>
                <div class="mini-card-text">
                    There's no way to get this wrong. If the counts feel
                    too long, simply breathe a little shorter.
                </div>
            </div>
            <div class="mini-card">
                <div class="mini-card-title">🌷 Be gentle with yourself</div>
                <div class="mini-card-text">
                    If you ever feel dizzy, stop and go back to normal
                    breathing. If things feel like too much, talking to
                    someone you trust can really help. ♡
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# =============================
# TAB 4: AFFIRMATIONS
# =============================
with affirmation_tab:
    st.markdown(
        '<div class="section-title">A little reminder for you 🌷</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tiny-note">A few kind words to carry into your day. '
        'Take what you need and leave the rest. ♡</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.6, 1], gap="large")

    with left:
        st.markdown(
            note_card(
                "Your moment of kindness ✨",
                "You deserve encouragement, even on the ordinary days. "
                "Let's find a little reminder just for you. ♡",
                theme="affirmation",
                tilt="1deg",
            ),
            unsafe_allow_html=True,
        )

        affirmation_generated = False

        if st.button(
            "Find my affirmation ✨",
            key="generate_affirmation",
            use_container_width=True,
        ):
            # Avoid showing the exact same affirmation twice in a row.
            affirmation_options = [
                a for a in affirmations
                if a != st.session_state["current_affirmation"]
            ] or affirmations
            st.session_state["current_affirmation"] = random.choice(
                affirmation_options
            )
            affirmation_generated = True

        if st.session_state["current_affirmation"]:
            affirmation_text = st.session_state["current_affirmation"]

            st.markdown(
                note_card(
                    "A little note to keep ♡",
                    affirmation_text,
                    theme="affirmation",
                    tilt=tilt_for(affirmation_text),
                    animate=affirmation_generated,
                ),
                unsafe_allow_html=True,
            )

            if st.button(
                "♡ Save to My Collection",
                key="save_affirmation",
                use_container_width=True,
            ):
                item = {
                    "type": "Affirmation",
                    "text": affirmation_text,
                    "mood": None,
                }

                if item not in st.session_state["favourites"]:
                    st.session_state["favourites"].append(item)
                    st.toast("Affirmation saved! 🌷")
                else:
                    st.toast("This affirmation is already saved! ♡")
        else:
            st.markdown(
                note_card(
                    "Your next little reminder 🌱",
                    "Your affirmation will appear here when you're ready. "
                    "There's no rush. ♡",
                    theme="affirmation",
                    tilt="-1deg",
                ),
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            """
            <div class="mini-card">
                <div class="mini-card-title">🌷 A gentle reminder</div>
                <div class="mini-card-text">
                    You don't need to be productive every moment
                    to deserve a little kindness.
                </div>
            </div>
            <div class="mini-card">
                <div class="mini-card-title">☁️ A tiny ritual</div>
                <div class="mini-card-text">
                    Take one slow breath, relax your shoulders,
                    and choose one kind thought to carry with you.
                </div>
            </div>
            <div class="mini-card">
                <div class="mini-card-title">♡ Your little collection</div>
                <div class="mini-card-text">
                    Save the words that resonate with you.
                    You can revisit them in My Collection.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# =============================
# TAB 5: GRATITUDE JAR
# =============================
with jar_tab:
    # Toast / balloons from the slip that was just dropped in (after the rerun).
    if st.session_state["jar_just_added"]:
        st.session_state["jar_just_added"] = False
        jar_total = len(st.session_state["gratitude_jar"])

        if jar_total in JAR_MILESTONES:
            st.balloons()
            st.toast(JAR_MILESTONES[jar_total])
        else:
            st.toast("Dropped into the jar! 🫙♡")

    st.markdown(
        '<div class="section-title">Your gratitude jar 🫙</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tiny-note">Write down something you\'re thankful for and '
        'drop it in the jar. Shake it on a tough day to pull out a little '
        'reminder. ♡</div>',
        unsafe_allow_html=True,
    )

    jar = st.session_state["gratitude_jar"]

    # These flags are read once, so the animations only play when they should.
    animate_new_slip = st.session_state["jar_flash"]
    jar_is_shaking = st.session_state["jar_shaking"]
    st.session_state["jar_flash"] = False
    st.session_state["jar_shaking"] = False

    left, right = st.columns([1.3, 1], gap="large")

    with left:
        st.markdown(
            jar_html(jar, animate_last=animate_new_slip, shaking=jar_is_shaking),
            unsafe_allow_html=True,
        )

        # ----- Shake the jar -----
        if jar:
            st.button(
                "Shake the jar & pull out a slip 🎲",
                key="shake_jar",
                on_click=shake_jar,
                use_container_width=True,
            )
        else:
            st.caption("Add your first slip below, then you can shake the jar. 🌱")

        pulled = st.session_state["jar_pulled"]

        if pulled and pulled in jar:
            st.markdown(
                note_card(
                    "A slip from your jar ♡",
                    pulled["text"],
                    theme="gratitude",
                    tilt=tilt_for(pulled["text"] + pulled["date"]),
                    animate=jar_is_shaking,
                    footer=f"written on {pretty_iso(pulled['date'])}",
                ),
                unsafe_allow_html=True,
            )

            if st.button(
                "♡ Save to My Collection",
                key="save_slip",
                use_container_width=True,
            ):
                slip_item = {
                    "type": "Gratitude",
                    "text": pulled["text"],
                    "mood": None,
                }

                if slip_item not in st.session_state["favourites"]:
                    st.session_state["favourites"].append(slip_item)
                    st.toast("Saved to your little collection! ♡")
                else:
                    st.toast("This slip is already in your collection! ♡")

        # ----- Add a slip -----
        st.markdown(
            '<div class="section-title" style="font-size:1.5rem;">'
            "Add a little slip ✍️</div>",
            unsafe_allow_html=True,
        )

        with st.form("gratitude_form", clear_on_submit=True):
            slip_text = st.text_input(
                "What are you grateful for today?",
                max_chars=140,
                placeholder=st.session_state["jar_prompt"]
                or "e.g. the warm sun on my window",
            )
            slip_submit = st.form_submit_button(
                "Drop it in the jar 🫙",
                use_container_width=True,
            )

        if slip_submit:
            clean_text = slip_text.strip()

            if not clean_text:
                st.warning("Write a tiny something first. Even one word counts. ♡")
            else:
                st.session_state["gratitude_jar"].append(
                    {
                        "text": clean_text,
                        "date": get_local_now().date().isoformat(),
                    }
                )
                st.session_state["jar_flash"] = True
                st.session_state["jar_just_added"] = True
                st.rerun()

    with right:
        week_cutoff = (get_local_now().date() - timedelta(days=6)).isoformat()
        slips_this_week = sum(1 for e in jar if e["date"] >= week_cutoff)

        jar_stat1, jar_stat2 = st.columns(2)
        jar_stat1.metric("In the jar 🫙", len(jar))
        jar_stat2.metric("This week", slips_this_week)

        # ----- Need inspiration? -----
        st.button(
            "Need a little inspiration? 💭",
            key="new_prompt",
            on_click=new_prompt,
            use_container_width=True,
        )

        if st.session_state["jar_prompt"]:
            st.markdown(
                note_card(
                    "A little prompt 💭",
                    st.session_state["jar_prompt"],
                    theme="gratitude",
                    tilt="1deg",
                ),
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class="mini-card">
                <div class="mini-card-title">🫙 Why a gratitude jar?</div>
                <div class="mini-card-text">
                    Noticing small good things helps them stick. On a
                    harder day, your jar is a pocket of proof that
                    there are lovely things around you.
                </div>
            </div>
            <div class="mini-card">
                <div class="mini-card-title">🌷 Keep it tiny</div>
                <div class="mini-card-text">
                    A warm drink, a kind text, a good song. Small slips
                    count just as much as big ones.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----- Look inside / export / empty -----
        if jar:
            with st.expander("Look inside the jar 🔍"):
                for slip_index in range(len(jar) - 1, -1, -1):
                    slip = jar[slip_index]
                    slip_text_col, slip_btn_col = st.columns([4, 1])

                    slip_text_col.markdown(
                        '<div class="mini-card-text">'
                        f"♡ {html.escape(slip['text'])}<br>"
                        f"<small>{html.escape(pretty_iso(slip['date']))}</small>"
                        "</div>",
                        unsafe_allow_html=True,
                    )
                    slip_btn_col.button(
                        "✕",
                        key=f"remove_slip_{slip_index}",
                        on_click=remove_slip,
                        args=(slip_index,),
                        help="Remove this slip",
                        use_container_width=True,
                    )

            st.download_button(
                "Download my jar 📥",
                data=jar_export_text(jar),
                file_name="my_gratitude_jar.txt",
                mime="text/plain",
                key="download_jar",
                use_container_width=True,
            )

            st.button(
                "Empty the jar",
                key="empty_jar",
                on_click=empty_jar,
                use_container_width=True,
            )

# =============================
# TAB 6: MUSIC CORNER
# =============================
with music_tab:
    if st.session_state["music_added"]:
        st.session_state["music_added"] = False
        st.toast("Playlist added to your music corner! 🎧")

    st.markdown(
        '<div class="section-title">Your little music corner 🎧</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tiny-note">Pick a mood, press play, and let a little '
        "record spin for you. ♡</div>",
        unsafe_allow_html=True,
    )

    # ----- Now playing -----
    now = find_track(st.session_state["now_playing"])

    if now:
        now_left, now_right = st.columns([1, 1.7], gap="large")

        with now_left:
            st.markdown(now_playing_html(now), unsafe_allow_html=True)
            st.button(
                "Stop ■",
                key="stop_music",
                on_click=stop_track,
                use_container_width=True,
            )

        with now_right:
            now_embed = get_spotify_embed_url(now["url"])
            if now_embed:
                st.iframe(now_embed, height=352)
                st.caption("Press play inside the player. Spotify doesn't allow autoplay. ♡")
            else:
                st.warning("That link can't be played here. Try opening it on Spotify.")
    else:
        st.markdown(
            note_card(
                "Nothing playing yet 🎶",
                "Press Play on any record below, or hit Surprise me and "
                "let the bunny choose. ♡",
                theme="default",
                tilt="-1deg",
            ),
            unsafe_allow_html=True,
        )

    recent_tracks = [
        t for t in (find_track(r) for r in st.session_state["music_recent"]) if t
    ]
    if recent_tracks:
        recent_chips = "".join(
            f'<span class="chip" style="--c1:{t["c1"]};--c2:{t["c2"]};">'
            f'{html.escape(t["emoji"])} {html.escape(t["title"])}</span>'
            for t in recent_tracks
        )
        st.markdown(
            f'<div class="recent-row">Recently played:{recent_chips}</div>',
            unsafe_allow_html=True,
        )

    # ----- Filters -----
    filter_options = ["All 🎵", "♡ Favourites"] + MUSIC_MOODS
    chosen_filter = st.pills(
        "Browse by mood",
        filter_options,
        default="All 🎵",
        key="music_filter",
        label_visibility="collapsed",
    ) or "All 🎵"

    search_col, shuffle_col = st.columns([2.4, 1], gap="medium")

    with search_col:
        search_text = st.text_input(
            "Search the music corner",
            placeholder="Search by name or vibe... 🔍",
            label_visibility="collapsed",
            key="music_search",
        )

    with shuffle_col:
        st.button(
            "Surprise me 🎲",
            key="surprise_music",
            on_click=surprise_track,
            use_container_width=True,
        )

    # ----- Apply filters -----
    visible = all_tracks()

    if chosen_filter == "♡ Favourites":
        visible = [t for t in visible if t["id"] in st.session_state["music_favs"]]
    elif chosen_filter in MUSIC_MOODS:
        visible = [t for t in visible if chosen_filter in t["moods"]]

    query = search_text.strip().lower()
    if query:
        visible = [
            t for t in visible
            if query in (t["title"] + " " + t["desc"] + " " + " ".join(t["vibes"])).lower()
        ]

    # ----- Playlist cards (two per row) -----
    if not visible:
        st.markdown(
            note_card(
                "Nothing here yet 🌷",
                "No playlists match that. Try another mood, clear the "
                "search, or add your own below. ♡",
                theme="default",
                tilt="1deg",
            ),
            unsafe_allow_html=True,
        )
    else:
        for start in range(0, len(visible), 2):
            row_cols = st.columns(2, gap="large")

            for col, track in zip(row_cols, visible[start:start + 2]):
                with col:
                    is_playing = st.session_state["now_playing"] == track["id"]
                    is_fav = track["id"] in st.session_state["music_favs"]

                    st.markdown(
                        music_card_html(track, is_playing),
                        unsafe_allow_html=True,
                    )

                    b1, b2, b3 = st.columns([1.3, 1, 1.4])

                    with b1:
                        if is_playing:
                            st.button(
                                "Stop ■",
                                key=f"stop_{track['id']}",
                                on_click=stop_track,
                                use_container_width=True,
                            )
                        else:
                            st.button(
                                "▶ Play",
                                key=f"play_{track['id']}",
                                on_click=play_track,
                                args=(track["id"],),
                                use_container_width=True,
                            )

                    with b2:
                        st.button(
                            "♥" if is_fav else "♡",
                            key=f"fav_{track['id']}",
                            on_click=toggle_fav,
                            args=(track["id"],),
                            use_container_width=True,
                            help="Remove from favourites" if is_fav else "Save to favourites",
                        )

                    with b3:
                        st.link_button(
                            "Spotify ↗",
                            track["url"],
                            key=f"open_{track['id']}",
                            use_container_width=True,
                        )

    # ----- Add your own -----
    st.divider()
    st.markdown(
        '<div class="section-title" style="font-size:1.5rem;">'
        "Add your own playlist ♡</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tiny-note">Paste any Spotify track, album, artist or '
        "playlist link and it becomes a little record of its own.</div>",
        unsafe_allow_html=True,
    )

    with st.form("add_playlist_form", clear_on_submit=True):
        form_left, form_right = st.columns(2, gap="large")

        with form_left:
            new_title = st.text_input(
                "Name it",
                max_chars=40,
                placeholder="e.g. Sunday morning mix",
            )
            new_link = st.text_input(
                "Spotify link",
                placeholder="https://open.spotify.com/playlist/...",
            )

        with form_right:
            new_emoji = st.selectbox("Cover emoji", COVER_EMOJIS)
            new_mood = st.selectbox("Mood", MUSIC_MOODS)
            new_vibes = st.text_input(
                "Vibe words (optional, comma separated)",
                placeholder="cosy, rainy, hopeful",
            )

        add_clicked = st.form_submit_button(
            "Add to my music corner 🎶",
            use_container_width=True,
        )

    if add_clicked:
        embed = get_spotify_embed_url(new_link)
        title = new_title.strip()

        if not title:
            st.error("Give your playlist a little name first. ♡")
        elif not embed:
            st.error(
                "I couldn't recognise that Spotify link. Copy a track, "
                "album, artist or playlist link from Spotify."
            )
        else:
            clean_url = embed.replace("/embed/", "/")
            already = any(t["url"] == clean_url for t in all_tracks())

            if already:
                st.warning("That one is already in your music corner. ♡")
            else:
                vibes = [
                    v.strip()[:24] for v in new_vibes.split(",") if v.strip()
                ][:3] or ["your own pick"]
                c1, c2 = MOOD_COVERS[new_mood]

                st.session_state["my_playlists"].append(
                    dict(
                        id=f"my-{zlib.crc32(clean_url.encode('utf-8')):08x}",
                        title=title,
                        emoji=new_emoji,
                        desc="One of your own picks ♡",
                        vibes=vibes,
                        moods=[new_mood],
                        url=clean_url,
                        c1=c1, c2=c2, custom=True,
                    )
                )
                st.session_state["music_added"] = True
                st.rerun()

    if st.session_state["my_playlists"]:
        with st.expander("Manage my playlists 🌱"):
            for mine in st.session_state["my_playlists"]:
                manage_name, manage_btn = st.columns([3, 1])
                manage_name.markdown(
                    f"{html.escape(mine['emoji'])} **{html.escape(mine['title'])}**"
                )
                manage_btn.button(
                    "Remove",
                    key=f"remove_{mine['id']}",
                    on_click=remove_playlist,
                    args=(mine["id"],),
                    use_container_width=True,
                )

# =============================
# TAB 7: MY COLLECTION
# =============================
with collection_tab:
    st.markdown(
        '<div class="section-title">Your little collection ♡</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tiny-note">All the little things you chose to keep.</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state["favourites"]:
        st.markdown(
            note_card(
                "A little space waiting for you 🌷",
                "Nothing here just yet. Save a message, affirmation, or "
                "gratitude slip you love, and it will find a home here. ♡",
                theme="default",
                tilt="-1deg",
            ),
            unsafe_allow_html=True,
        )
    else:
        for index, item in enumerate(st.session_state["favourites"]):
            item_mood = item.get("mood")
            item_theme = item_mood or (
                "gratitude" if item["type"] == "Gratitude" else "affirmation"
            )

            st.markdown(
                note_card(
                    f"{item['type']} ♡",
                    item["text"],
                    theme=item_theme,
                    tilt=tilt_for(item["text"]),
                    footer=item_mood,
                ),
                unsafe_allow_html=True,
            )

            if st.button("Remove ♡", key=f"remove_favourite_{index}"):
                st.session_state["favourites"].pop(index)
                st.rerun()

        st.write("")
        if st.button("Clear my collection", key="clear_collection"):
            st.session_state["favourites"] = []
            st.rerun()

# =============================
# TAB 8: TINY ADVENTURES
# =============================
with adventure_tab:
    # Celebration runs on the rerun right after "I did it!" is clicked.
    if st.session_state["celebrate"]:
        st.session_state["celebrate"] = False
        total_done = len(st.session_state["completed_adventures"])

        if total_done % 5 == 0:
            st.snow()
            st.toast(f"{total_done} tiny adventures! You're on a roll ❄️♡")
        else:
            st.balloons()
            st.toast(random.choice([
                "Look at you go! 🎈",
                "Tiny win unlocked! ✨",
                "So proud of you! ♡",
                "That counts, and it's wonderful. 🌷",
            ]))

    st.markdown(
        '<div class="section-title">Tiny adventures 🍓</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tiny-note">Little things to make an ordinary day '
        'feel special.</div>',
        unsafe_allow_html=True,
    )

    adventures = {
        "Cozy 🧸": [
            ("Make a cozy drink", "Prepare your favourite tea, coffee, or hot chocolate and enjoy it without distractions."),
            ("Have a little reading moment", "Read a few pages of a book, a poem, or an article you've been saving."),
            ("Create a comfort playlist", "Gather five songs that make you feel safe, calm, or happy."),
            ("Have a window moment", "Sit by a window for five minutes and notice the world outside."),
        ],
        "Creative 🎨": [
            ("Make a tiny mood board", "Collect five pictures, colours, or words that match your current mood."),
            ("Write a little note", "Write a kind note to your future self."),
            ("Doodle something silly", "Draw a bunny, a flower, or anything at all. It doesn't need to be perfect."),
            ("Capture a little moment", "Take a photo of something ordinary that you find beautiful."),
        ],
        "Outdoorsy 🌷": [
            ("Take a little walk", "Walk for ten minutes and notice three things you haven't paid attention to before."),
            ("Find something blooming", "Look for a flower, a leaf, or a tiny patch of green."),
            ("Watch the sky", "Spend a few minutes noticing the clouds, colours, or changing light."),
            ("Explore a new route", "If it's safe and convenient, take a different route on your next short walk."),
        ],
        "Self-care 🫧": [
            ("Take a proper stretch break", "Stretch gently for five minutes and give your eyes a break from the screen."),
            ("Have a digital pause", "Put your phone away for ten minutes and let your mind wander."),
            ("Reset one tiny space", "Tidy just your desk, bedside table, or one small corner."),
            ("Give yourself some credit", "Write down one thing you handled well today, however small."),
        ],
        "Something new ✨": [
            ("Learn one random thing", "Look up a curious question you've always wondered about."),
            ("Try a new recipe idea", "Find a simple recipe you'd like to try sometime."),
            ("Listen outside your usual taste", "Play one song from a genre you don't usually listen to."),
            ("Make a mini bucket list", "Write down three small things you'd love to do this month."),
        ],
    }

    left, right = st.columns([1.5, 1], gap="large")

    with left:
        st.markdown(
            note_card(
                "A little adventure awaits... 🌱",
                "No big plans required. Pick a tiny activity, take your "
                "time, and make a little room for joy. ♡",
                theme="adventure",
                tilt="-1deg",
            ),
            unsafe_allow_html=True,
        )

        category = st.selectbox(
            "What kind of adventure are you in the mood for?",
            list(adventures.keys()),
            key="adventure_category",
        )

        adventure_picked = False
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Surprise me! 🎲",
                key="surprise_adventure",
                use_container_width=True,
            ):
                st.session_state["current_adventure"] = (
                    category,
                    random.choice(adventures[category]),
                )
                adventure_picked = True

        with col2:
            if st.button(
                "A totally random one ✨",
                key="random_adventure",
                use_container_width=True,
            ):
                random_category = random.choice(list(adventures.keys()))
                st.session_state["current_adventure"] = (
                    random_category,
                    random.choice(adventures[random_category]),
                )
                adventure_picked = True

        if st.session_state["current_adventure"] is not None:
            adventure_category, adventure = st.session_state["current_adventure"]
            adventure_title, adventure_description = adventure

            st.markdown(
                note_card(
                    f"{adventure_title} ♡",
                    adventure_description,
                    theme="adventure",
                    tilt=tilt_for(adventure_title),
                    animate=adventure_picked,
                    footer=adventure_category,
                ),
                unsafe_allow_html=True,
            )

            adventure_key = (adventure_category, adventure_title)

            if adventure_key in st.session_state["completed_adventures"]:
                st.success("You've completed this tiny adventure! Look at you. ♡")
            elif st.button("I did it! ♡", key="complete_adventure"):
                st.session_state["completed_adventures"].append(adventure_key)
                st.session_state["celebrate"] = True
                st.rerun()

    with right:
        st.markdown(
            """
            <div class="mini-card">
                <div class="mini-card-title">🍓 Keep it tiny</div>
                <div class="mini-card-text">
                    An adventure doesn't have to be a big trip.
                    A new song or a different walking route counts, too.
                </div>
            </div>
            <div class="mini-card">
                <div class="mini-card-title">☁️ No pressure</div>
                <div class="mini-card-text">
                    Choose something that suits your energy today.
                    You can always try another activity later.
                </div>
            </div>
            <div class="mini-card">
                <div class="mini-card-title">🌷 Your tiny wins</div>
                <div class="mini-card-text">
                    Every small thing you do for yourself is worth celebrating.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        completed = st.session_state["completed_adventures"]
        st.metric("Tiny adventures completed ♡", len(completed))

        if completed:
            with st.expander("See your little wins 🌱"):
                for completed_category, completed_title in completed:
                    st.markdown(
                        f"- ♡ {html.escape(completed_title)} "
                        f"*({html.escape(completed_category)})*"
                    )

                if st.button("Clear my tiny wins", key="clear_adventures"):
                    st.session_state["completed_adventures"] = []
                    st.rerun()
        else:
            st.caption("Your little wins will appear here. Every small step counts! ♡")

# =============================
# HERO (rendered last so the bunny level is always up to date)
# =============================
hero_slot.markdown(build_hero_html(), unsafe_allow_html=True)

# =============================
# FOOTER
# =============================
st.markdown(
    """
    <div class="footer">
        made with ♡, a little Python, and a bunny
        <br>
        ୨୧ take care of yourself ୨୧
        <div class="footer-support">
            If today feels really heavy, it's okay to reach out to someone
            you trust or a local support line. You deserve company, too. ♡
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)