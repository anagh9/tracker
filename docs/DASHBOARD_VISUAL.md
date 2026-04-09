# Dashboard Redesign - Visual Structure

## Top Navigation
```
⚡ HealthTrack          Welcome back, {{ username }}          [Logout]
```

## Main Dashboard Layout

### 1. Daily Health Score Card (Left - Purple/Blue)
```
┌─────────────────────────────────┐
│   TODAY'S SCORE                 │
│   83/100  🌱                    │
│                                 │
│ 🚀 You're making progress!      │
│                                 │
│ Novice                          │
│ ████░░ 17 to next level         │
└─────────────────────────────────┘
```

### 2. Streaks & Weekly Stats (Right)
```
┌────────────────────┬────────────────────┐
│ DAILY STREAK       │ TRACKERS ACTIVE    │
│ 7 🔥               │ 2 📊                │
│ days active        │ synced today       │
└────────────────────┴────────────────────┘

┌──────────────────────────────────────────┐
│ WEEKLY OVERVIEW                    7 days│
├──────────────────────────────────────────┤
│ Days logged: 6    Total: 47       Avg: 78│
└──────────────────────────────────────────┘
```

### 3. Today's Summary Cards
```
┌──────────────────────┬──────────────────────┐
│ 🔥 CALORIES          │ 📊 HABITS LOGGED    │
│ 300 kcal / 2000      │ 5 entries / 3       │
│ ████░░ 15%           │ ██████ 100%         │
│ View Details →       │ View Details →      │
└──────────────────────┴──────────────────────┘
```

### 4. Smart Insights Section (Left 2/3)

#### Primary Insight
```
┌──────────────────────────────────────────────┐
│ 💪 Habit Warrior                             │
│ You're tracking consistently. Keep pushing!  │
└──────────────────────────────────────────────┘
```

#### Key Insights & Trend
```
┌──────────────────────┬──────────────────────┐
│ KEY INSIGHTS         │ DISCIPLINE RATING    │
├──────────────────────┼──────────────────────┤
│ ✨ Great tracking!   │ 🌟 Excellent        │
│ 💡 Stay consistent   │ 📊 85% Consistent   │
│ 💡 Morning logs best │ 🎯 72% Adherence    │
└──────────────────────┴──────────────────────┘
```

#### Recommendations
```
┌──────────────────────────────────────────────┐
│ RECOMMENDATIONS                              │
├──────────────────────────────────────────────┤
│ 💡 Schedule daily tracking time             │
│ 💡 Review weekly insights for patterns      │
│ 💡 Target 30 consecutive logging days       │
└──────────────────────────────────────────────┘
```

### 5. Sidebar (Right 1/3)

#### Achievements
```
┌──────────────────────────────────┐
│ 🏆 ACHIEVEMENTS                  │
├──────────────────────────────────┤
│ 🗓️ Week Warrior [✓ Unlocked]    │
│    Logged for 7 days             │
│                                  │
│ 🏥 Health Alert [✓ Unlocked]    │
│    Track calories and habits     │
│                                  │
│ 👑 Master [✗ Locked]            │
│    Score 90+ for 7 days          │
└──────────────────────────────────┘
```

#### Strengths & Focus
```
┌──────────────────────────────────┐
│ 💪 STRENGTHS                     │
│  ✅ Consistent daily logging     │
│  ✅ Balanced tracker usage       │
│  ✅ Strong motivation            │
│                                  │
│ 🎯 FOCUS AREAS                   │
│  → Weekend consistency           │
│  → Late-evening tracking         │
└──────────────────────────────────┘
```

#### Progress
```
┌──────────────────────────────────┐
│ 📈 THIS WEEK                     │
│ +15% Better than last week       │
│                                  │
│ ✨ TREND                         │
│ Rising 📈                        │
└──────────────────────────────────┘
```

### 6. Quick Access Trackers (Bottom)
```
┌──────────────────────────┬──────────────────────────┐
│ 🔥 CALORIE TRACKER       │ 📉 HABITS TRACKER        │
│ Track daily intake, get  │ Monitor habits with      │
│ AI suggestions, and      │ daily logging and        │
│ visualize nutrition      │ analytics                │
│ Open Tracker →           │ Open Tracker →           │
└──────────────────────────┴──────────────────────────┘
```

## Sample Score Breakdown

```
Daily Score Calculation: 83/100

├── Calorie Tracking (max 40)
│   ├── Logged today: +20
│   ├── Adherence (15%): +3
│   └── Subtotal: 23 ✓
│
├── Habits Tracking (max 30)
│   ├── Logged today: +20
│   ├── Avoided 2 habits: +10
│   └── Subtotal: 30 ✓
│
├── Consistency Bonus (max 20)
│   ├── 2 trackers active: +20
│   └── Subtotal: 20 ✓
│
├── Streak Bonus (max 10)
│   ├── 7-day streak: +10
│   └── Subtotal: 10 ✓
│
└── TOTAL: 83/100 🌱 (Novice)
```

## Level Progression

```
🌱 Novice          (0-99 points)    [==░░░░░░░░░░░░] 0% to next
🔥 Committed     (100-299 points)    [████░░░░░░░░░░] 40% to next
⛓️ Dedicated     (300-499 points)    [████████░░░░░░] 60% to next
👑 Master        (500+ points)       [████████████░░] 80% to next
```

## Responsive Breakpoints

### Mobile (< 768px)
```
- Single column layout
- Stacked cards
- Score card full width
- Touch-friendly buttons
- 16px padding
```

### Tablet (768px - 1024px)
```
- 2 column grid
- Score → Streaks beside
- Side-by-side tracker cards
- Sidebar below widgets
```

### Desktop (> 1024px)
```
- 3 column layout: Score | Middle | Sidebar
- Full-width insights section
- All parallel display
- Max-width 7xl container
```

## Color Scheme

```
Primary
├── Purple: #A855F7 (Score card gradient start)
├── Blue: #2563EB (Score card gradient end)
└── Slate: #0F172A (Text/neutral)

Tracker Colors
├── Orange: #EA580C (Calorie accent) #FFF7ED bg
├── Blue: #0EA5E9 (Habits accent) #F0F9FF bg
└── Green: #10B981 (Future trackers)

Neutral
├── White: #FFFFFF (Cards)
├── Slate-100: #F1F5F9 (Light bg)
├── Slate-600: #475569 (Secondary text)
└── Slate-900: #0F172A (Primary text)
```

## Interactive Features

- Hover effects on cards (shadow increase, scale 105%)
- Progress bars animate on load
- Smooth transitions (300ms cubic-bezier)
- Gradient animations on hover
- Dropdown/collapse options for detailed views
