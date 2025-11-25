<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Track Course Attendance with Zoom Integration</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .gradient-bg {
      background: radial-gradient(circle at top left, #4f46e5, #0f172a 50%, #020617);
    }
    .card-shadow {
      box-shadow: 0 18px 45px rgba(15, 23, 42, 0.4);
    }
  </style>
</head>
<body class="bg-slate-950 text-slate-50 antialiased">
  <!-- Page wrapper -->
  <div class="min-h-screen gradient-bg flex flex-col">

    <!-- Nav -->
    <header class="w-full border-b border-slate-800/60">
      <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="h-8 w-8 rounded-xl bg-indigo-500/90 flex items-center justify-center text-xs font-bold tracking-tight">
            ZA
          </div>
          <span class="text-sm font-semibold tracking-tight text-slate-100">
            ZoomAttendance.io
          </span>
        </div>
        <nav class="hidden sm:flex items-center gap-6 text-xs font-medium text-slate-300">
          <a href="#features" class="hover:text-white transition-colors">Features</a>
          <a href="#how-it-works" class="hover:text-white transition-colors">How it works</a>
          <a href="#faq" class="hover:text-white transition-colors">FAQ</a>
        </nav>
        <div class="flex items-center gap-3">
          <button class="hidden sm:inline-flex text-xs font-medium px-3 py-1.5 rounded-full border border-slate-600/80 text-slate-200 hover:bg-slate-800/70 transition">
            Sign in
          </button>
          <button class="text-xs font-semibold px-4 py-2 rounded-full bg-indigo-500 hover:bg-indigo-400 text-white transition">
            Start free trial
          </button>
        </div>
      </div>
    </header>

    <!-- Hero -->
    <main class="flex-1">
      <section class="max-w-6xl mx-auto px-4 py-12 lg:py-20 grid lg:grid-cols-[3fr,2fr] gap-10 lg:gap-14 items-center">
        <!-- Hero text -->
        <div>
          <div class="inline-flex items-center gap-2 rounded-full border border-indigo-500/40 bg-indigo-500/10 px-3 py-1 mb-4">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
            <span class="text-[11px] font-medium uppercase tracking-[0.18em] text-indigo-100">
              Designed for live courses
            </span>
          </div>

          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-semibold tracking-tight text-slate-50 mb-4">
            Track Course Attendance<br class="hidden sm:block" />
            with Zoom Integration
          </h1>

          <p class="text-sm sm:text-base text-slate-300 max-w-xl mb-6">
            Monitor participant engagement, sync attendance from Zoom meetings, and generate
            comprehensive reports &mdash; all in one secure platform.
          </p>

          <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mb-6">
            <button class="inline-flex justify-center items-center px-5 py-2.5 rounded-full bg-indigo-500 hover:bg-indigo-400 text-sm font-semibold text-white transition">
              Connect Zoom &amp; get started
            </button>
            <button class="inline-flex justify-center items-center px-5 py-2.5 rounded-full border border-slate-700 text-sm font-medium text-slate-200 hover:bg-slate-900/60 transition">
              Book a 15‑min demo
            </button>
          </div>

          <p class="text-[11px] text-slate-400">
            No credit card required. Secure by design. Ready in under 5 minutes.
          </p>
        </div>

        <!-- Hero card -->
        <div class="relative">
          <div class="absolute inset-0 rounded-3xl bg-indigo-500/30 blur-3xl opacity-60 -z-10"></div>
          <div class="bg-slate-900/90 border border-slate-700/70 rounded-3xl p-5 sm:p-6 card-shadow">
            <div class="flex items-center justify-between mb-4">
              <span class="text-xs font-medium text-slate-300">Today’s live session</span>
              <span class="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-300">
                • Live sync on
              </span>
            </div>

            <div class="mb-4 border border-slate-700/80 rounded-2xl px-4 py-3 bg-slate-900/70">
              <div class="flex items-center justify-between mb-1.5">
                <div>
                  <p class="text-xs font-semibold text-slate-100">
                    Advanced React Bootcamp
                  </p>
                  <p class="text-[11px] text-slate-400">
                    09:00–11:00 &middot; Zoom Meeting #4821
                  </p>
                </div>
                <span class="inline-flex items-center px-2 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-[10px] font-semibold text-emerald-200">
                  Syncing
                </span>
              </div>
              <div class="mt-3 grid grid-cols-3 gap-3 text-[11px] text-slate-300">
                <div>
                  <p class="text-slate-400 mb-0.5">Participants</p>
                  <p class="font-semibold text-slate-50">42 / 50</p>
                </div>
                <div>
                  <p class="text-slate-400 mb-0.5">Avg. attendance</p>
                  <p class="font-semibold text-slate-50">92%</p>
                </div>
                <div>
                  <p class="text-slate-400 mb-0.5">Avg. duration</p>
                  <p class="font-semibold text-slate-50">1h 47m</p>
                </div>
              </div>
            </div>

            <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400 mb-2">
              Live attendance stream
            </p>

            <div class="space-y-2.5 max-h-44 overflow-hidden">
              <div class="flex items-center justify-between text-xs">
                <div class="flex items-center gap-2">
                  <span class="h-6 w-6 rounded-full bg-slate-800 border border-slate-700/90"></span>
                  <div>
                    <p class="text-slate-100 text-[11px] font-medium">Alex Chen</p>
                    <p class="text-[10px] text-slate-400">Joined · 09:01 &nbsp;|&nbsp; Present 94%</p>
                  </div>
                </div>
                <span class="text-[10px] px-2 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                  1h 44m
                </span>
              </div>

              <div class="flex items-center justify-between text-xs">
                <div class="flex items-center gap-2">
                  <span class="h-6 w-6 rounded-full bg-slate-800 border border-slate-700/90"></span>
                  <div>
                    <p class="text-slate-100 text-[11px] font-medium">Maria Lopez</p>
                    <p class="text-[10px] text-slate-400">Rejoined · 09:15 &nbsp;|&nbsp; Present 81%</p>
                  </div>
                </div>
                <span class="text-[10px] px-2 py-1 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30">
                  1h 21m
                </span>
              </div>

              <div class="flex items-center justify-between text-xs">
                <div class="flex items-center gap-2">
                  <span class="h-6 w-6 rounded-full bg-slate-800 border border-slate-700/90"></span>
                  <div>
                    <p class="text-slate-100 text-[11px] font-medium">Samir Patel</p>
                    <p class="text-[10px] text-slate-400">Left early · 10:12 &nbsp;|&nbsp; Present 63%</p>
                  </div>
                </div>
                <span class="text-[10px] px-2 py-1 rounded-full bg-rose-500/10 text-rose-300 border border-rose-500/30">
                  0h 58m
                </span>
              </div>
            </div>

            <div class="mt-4 flex items-center justify-between text-[11px] text-slate-400">
              <span>Auto-saving to attendance report…</span>
              <button class="inline-flex items-center gap-1 text-[11px] font-medium text-indigo-300 hover:text-indigo-200">
                Export CSV
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Features -->
      <section id="features" class="max-w-6xl mx-auto px-4 pb-16">
        <div class="border border-slate-800/70 rounded-3xl bg-slate-950/60 px-5 sm:px-8 py-8 sm:py-10">
          <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-6">
            <div>
              <h2 class="text-xl sm:text-2xl font-semibold text-slate-50 mb-1">
                Everything you need for reliable attendance
              </h2>
              <p class="text-sm text-slate-400 max-w-xl">
                Replace manual exports and spreadsheets with automated Zoom sync, accurate duration tracking,
                and clean CSV reports.
              </p>
            </div>
          </div>

          <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 text-sm">
            <div class="border border-slate-800 rounded-2xl p-4 bg-slate-900/60">
              <p class="text-xs font-semibold text-indigo-300 mb-1">Session Tracking</p>
              <h3 class="text-sm font-semibold text-slate-50 mb-1.5">
                Schedule &amp; auto-sync from Zoom
              </h3>
              <p class="text-sm text-slate-400">
                Schedule sessions once and let Zoom attendance flow in automatically, including late joins and re-joins.
              </p>
            </div>

            <div class="border border-slate-800 rounded-2xl p-4 bg-slate-900/60">
              <p class="text-xs font-semibold text-indigo-300 mb-1">Comprehensive Reports</p>
              <h3 class="text-sm font-semibold text-slate-50 mb-1.5">
                Export CSV in one click
              </h3>
              <p class="text-sm text-slate-400">
                Generate clean CSV files per session, cohort, or course so you can run your own analytics or share with stakeholders.
              </p>
            </div>

            <div class="border border-slate-800 rounded-2xl p-4 bg-slate-900/60">
              <p class="text-xs font-semibold text-indigo-300 mb-1">Secure Access</p>
              <h3 class="text-sm font-semibold text-slate-50 mb-1.5">
                Locked down by default
              </h3>
              <p class="text-sm text-slate-400">
                Role-based access ensures only authorized instructors and admins can view or export attendance data.
              </p>
            </div>

            <div class="border border-slate-800 rounded-2xl p-4 bg-slate-900/60">
              <p class="text-xs font-semibold text-indigo-300 mb-1">Real-time Dashboard</p>
              <h3 class="text-sm font-semibold text-slate-50 mb-1.5">
                See live engagement at a glance
              </h3>
              <p class="text-sm text-slate-400">
                Monitor who is present right now, how long they have been online, and which sessions have drop-off.
              </p>
            </div>

            <div class="border border-slate-800 rounded-2xl p-4 bg-slate-900/60">
              <p class="text-xs font-semibold text-indigo-300 mb-1">Duration Tracking</p>
              <h3 class="text-sm font-semibold text-slate-50 mb-1.5">
                Accurate per-participant time
              </h3>
              <p class="text-sm text-slate-400">
                Track total time attended per participant per session, including multiple joins, for audit-proof records.
              </p>
            </div>

            <div class="border border-slate-800 rounded-2xl p-4 bg-slate-900/60">
              <p class="text-xs font-semibold text-indigo-300 mb-1">Privacy-first</p>
              <h3 class="text-sm font-semibold text-slate-50 mb-1.5">
                Built for compliance
              </h3>
              <p class="text-sm text-slate-400">
                Keep attendance data in a single secure space with clear access controls and export logs.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- How it works -->
      <section id="how-it-works" class="max-w-6xl mx-auto px-4 pb-16">
        <div class="grid lg:grid-cols-[2fr,3fr] gap-8 items-start">
          <div>
            <h2 class="text-xl sm:text-2xl font-semibold text-slate-50 mb-2">
              How it works
            </h2>
            <p class="text-sm text-slate-400 mb-4">
              Go from manual exports to automated tracking in three simple steps.
            </p>
            <ol class="space-y-3 text-sm text-slate-300 list-decimal list-inside">
              <li>
                Connect your Zoom account to authorize secure access to meeting attendance.
              </li>
              <li>
                Create courses and sessions; link each session to the right Zoom meeting.
              </li>
              <li>
                Let attendance sync in real time and export CSV reports whenever you need them.
              </li>
            </ol>
          </div>
          <div class="border border-slate-800 rounded-3xl bg-slate-950/70 p-5 sm:p-6">
            <p class="text-xs font-semibold text-indigo-300 mb-2">
              Example CSV fields
            </p>
            <div class="overflow-x-auto text-[11px]">
              <table class="min-w-full border-separate border-spacing-y-1">
                <thead class="text-slate-400">
                  <tr>
                    <th class="text-left font-medium pr-4 pb-1">participant_name</th>
                    <th class="text-left font-medium pr-4 pb-1">email</th>
                    <th class="text-left font-medium pr-4 pb-1">session_id</th>
                    <th class="text-left font-medium pr-4 pb-1">join_time</th>
                    <th class="text-left font-medium pr-4 pb-1">leave_time</th>
                    <th class="text-left font-medium pb-1">total_minutes</th>
                  </tr>
                </thead>
                <tbody class="text-slate-200">
                  <tr class="bg-slate-900/80">
                    <td class="pr-4 py-1.5">Alex Chen</td>
                    <td class="pr-4 py-1.5">alex@example.com</td>
                    <td class="pr-4 py-1.5">react-bootcamp-01</td>
                    <td class="pr-4 py-1.5">2025-03-21T09:01</td>
                    <td class="pr-4 py-1.5">2025-03-21T10:45</td>
                    <td class="py-1.5">104</td>
                  </tr>
                  <tr class="bg-slate-900/40">
                    <td class="pr-4 py-1.5">Maria Lopez</td>
                    <td class="pr-4 py-1.5">maria@example.com</td>
                    <td class="pr-4 py-1.5">react-bootcamp-01</td>
                    <td class="pr-4 py-1.5">2025-03-21T09:15</td>
                    <td class="pr-4 py-1.5">2025-03-21T10:36</td>
                    <td class="py-1.5">81</td>
                  </tr>
                  <tr class="bg-slate-900/80">
                    <td class="pr-4 py-1.5">Samir Patel</td>
                    <td class="pr-4 py-1.5">samir@example.com</td>
                    <td class="pr-4 py-1.5">react-bootcamp-01</td>
                    <td class="pr-4 py-1.5">2025-03-21T09:02</td>
                    <td class="pr-4 py-1.5">2025-03-21T10:00</td>
                    <td class="py-1.5">58</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p class="mt-3 text-[11px] text-slate-400">
              Use these exports directly in your LMS, payroll, or certification workflows.
            </p>
          </div>
        </div>
      </section>

      <!-- FAQ -->
      <section id="faq" class="max-w-6xl mx-auto px-4 pb-16">
        <div class="border border-slate-800 rounded-3xl bg-slate-950/60 px-5 sm:px-8 py-7 sm:py-9">
          <h2 class="text-xl sm:text-2xl font-semibold text-slate-50 mb-4">
            Frequently asked questions
          </h2>
          <div class="space-y-4 text-sm text-slate-300">
            <div>
              <p class="font-semibold text-slate-100 mb-1">
                Do I need to export attendance from Zoom manually?
              </p>
              <p class="text-slate-400">
                No. Once connected, attendance is synced automatically from your Zoom meetings into the dashboard.
              </p>
            </div>
            <div>
              <p class="font-semibold text-slate-100 mb-1">
                Can I see how long each participant attended?
              </p>
              <p class="text-slate-400">
                Yes. The platform computes total attendance duration per participant for every session, even with multiple joins.
              </p>
            </div>
            <div>
              <p class="font-semibold text-slate-100 mb-1">
                Is attendance data secure?
              </p>
              <p class="text-slate-400">
                Access is protected with authentication and role-based permissions so only authorized users can view or export records.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-800/70">
      <div class="max-w-6xl mx-auto px-4 py-5 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-500">
        <span>&copy; 2025 ZoomAttendance.io. All rights reserved.</span>
        <div class="flex items-center gap-4">
          <a href="#" class="hover:text-slate-300">Privacy</a>
          <a href="#" class="hover:text-slate-300">Terms</a>
          <a href="#" class="hover:text-slate-300">Security</a>
        </div>
      </div>
    </footer>
  </div>
</body>
</html>
