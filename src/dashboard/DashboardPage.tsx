import TrendChartPanel from "../components/TrendChartPanel";
import DartConnectLogo from "../components/DartConnectLogo";
import { PLAYER } from "../data/performances";

const NAV = [
  { label: "Dashboard", active: true },
  { label: "Matches" },
  { label: "Competing" },
  { label: "Fan Alerts" },
  { label: "Player Library" },
];

const PERF_TILES = [
  { label: "Social", value: "—" },
  { label: "DartBot", value: "—" },
  { label: "Lobbies", value: "—" },
  { label: "Events", value: "—" },
  { label: "League (S)", value: "—" },
  { label: "League (T)", value: "38.14", highlight: true },
];

const UPCOMING = [
  { date: "Tue 01 Dec 26", home: true, time: "7:30 PM", vs: "George Keeley DC", venue: "Whiskey Town · New York" },
  { date: "Tue 08 Dec 26", home: false, time: "7:30 PM", vs: "Bust For Daddy", venue: "Storehouse · New York" },
  { date: "Tue 15 Dec 26", home: true, time: "7:30 PM", vs: "Just The Three Bulls", venue: "Whiskey Town · New York" },
];

const BAR_HEIGHTS = [8, 12, 10, 14, 9, 36];

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col bg-coolblue-500 font-sans text-blue-900">
      <header className="bg-gradient-to-r from-blue-500 via-blue-600 to-blue-500 pb-6 xl:pb-16">
        <div className="mx-auto max-w-screen-2xl px-4 py-4 xl:py-2">
          <div className="flex items-center justify-between">
            <a href="#" className="flex items-center" aria-label="DartConnect home">
              <DartConnectLogo className="h-11 w-auto sm:h-12 xl:h-14" />
            </a>
            <button type="button" className="flex items-center text-blue-100 outline-none">
              <span className="mr-3 inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-400 text-sm font-bold text-white">
                WG
              </span>
              <span className="hidden flex-col items-start md:flex">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-yellow-500">
                  Free Trial
                </span>
                <span className="text-sm font-semibold">William Guerrand</span>
              </span>
            </button>
          </div>
          <nav className="mt-5 hidden gap-7 xl:flex">
            {NAV.map((item) => (
              <a
                key={item.label}
                href="#"
                className={`font-montserrat text-lg font-semibold ${
                  item.active ? "text-blue-200" : "text-white hover:text-blue-300"
                }`}
              >
                <span className="block pb-1">{item.label}</span>
                <span className={`flex h-1 w-full ${item.active ? "bg-blue-400" : "bg-transparent"}`} />
              </a>
            ))}
            <div className="h-10 w-px self-center bg-blue-400" />
            <a
              href="#"
              className="inline-flex items-center self-center rounded-md border border-yellow-400 bg-yellow-500 px-3 py-2 font-montserrat text-lg font-semibold text-blue-700 shadow-md"
            >
              Tournaments / Leagues
              <span className="ml-2 rounded bg-blue-700 px-1.5 py-0.5 text-[10px] font-extrabold text-yellow-300">
                NEW
              </span>
            </a>
          </nav>
        </div>
      </header>

      <main className="z-10 -mt-8 flex-grow pb-10 xl:-mt-20">
        <div className="mx-auto w-full max-w-screen-2xl space-y-4 px-4">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <UserCard />
            <CompetitionCard />
          </div>

          <LeagueSection />

          <section className="space-y-4">
            <div className="flex flex-col lg:flex-row lg:items-center lg:gap-3">
              <h2 className="font-montserrat text-3xl font-bold text-blue-500 md:text-4xl">
                My Performance
              </h2>
              <span className="hidden h-1.5 w-1.5 rounded-full bg-blue-500 lg:inline-flex" />
              <span className="text-2xl font-normal text-blue-500">Fall Season</span>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="hidden text-sm lg:inline">Filter by</span>
              <select className="h-10 rounded-md bg-blue-400 px-3 text-sm font-bold text-white">
                <option>90 Days</option>
                <option>30 Days</option>
                <option>All Time</option>
              </select>
              <span className="hidden text-sm lg:inline">and</span>
              <select className="h-10 rounded-md bg-blue-400 px-3 text-sm font-bold text-white">
                <option>Singles 501 SIDO</option>
              </select>
              <button
                type="button"
                disabled
                className="h-10 cursor-not-allowed rounded-md bg-red-500 px-4 text-sm font-bold text-white opacity-60"
              >
                Filters Applied
              </button>
            </div>

            <TrendChartPanel />

            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
              {PERF_TILES.map((t) => (
                <div
                  key={t.label}
                  className={`rounded-md px-3 py-4 shadow ${
                    t.highlight ? "bg-yellow-500 text-blue-900" : "bg-blue-500 text-white"
                  }`}
                >
                  <div className="text-xs font-semibold uppercase opacity-90">{t.label}</div>
                  <div className="font-montserrat text-2xl font-bold">{t.value}</div>
                </div>
              ))}
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-md bg-white p-4 shadow xl:p-5">
                <h3 className="font-montserrat text-lg font-bold text-blue-500">
                  My DartConnect Average (DCA)
                </h3>
                <p className="text-sm text-blue-400">Singles 501 SIDO · All Time</p>
                <div className="mt-6 flex h-44 items-end justify-around gap-1 border-b border-coolblue-300 pb-2">
                  {BAR_HEIGHTS.map((h, i) => (
                    <div
                      key={i}
                      className={`w-10 rounded-t-sm ${i === 5 ? "bg-[#f8d583]" : "bg-coolblue-300"}`}
                      style={{ height: `${h * 4}px` }}
                    />
                  ))}
                </div>
                <p className="mt-2 text-center text-xs font-bold text-blue-400">
                  Online vs In-Person Performance
                </p>
              </div>
              <div className="rounded-md bg-white p-4 shadow xl:p-5">
                <h3 className="font-montserrat text-lg font-bold text-blue-500">My Activity</h3>
                <p className="text-sm text-blue-400">Singles 501 SIDO · All Time</p>
                <div className="mx-auto mt-6 flex h-44 w-44 items-center justify-center rounded-full border-[10px] border-[#577387] text-center text-sm font-bold leading-snug text-blue-500">
                  League Team
                  <br />
                  100%
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer className="mt-8 border-t-4 border-red-500 bg-[#16273A] px-4 py-10 text-white">
        <div className="mx-auto flex max-w-screen-2xl flex-wrap items-start justify-between gap-6">
          <div>
            <p className="text-sm text-white/80">
              TV scoring, registration, performance and player tools on DartConnect.
            </p>
            <p className="mt-4 text-xs text-white/60">© 2026 DartConnect. All rights reserved.</p>
            <p className="text-xs font-semibold text-white/80">Perfect Your Game</p>
            <p className="mt-2 text-[10px] text-white/40">
              Vision prototype · William Guerrand · not affiliated with DartConnect
            </p>
          </div>
          <button
            type="button"
            className="rounded-full bg-white px-4 py-2 font-montserrat text-xs font-bold uppercase tracking-wide text-[#16273A] shadow"
          >
            More DartConnect
          </button>
        </div>
      </footer>
    </div>
  );
}

function UserCard() {
  return (
    <div className="flex h-full flex-col rounded-md border-2 border-blue-500 bg-gradient-to-b from-blue-200 via-white to-white p-4 shadow xl:p-5">
      <div className="mb-2 flex">
        <img
          src="https://cdn.dartconnect.com/flags/fr.svg"
          alt=""
          className="mr-3 h-10 w-10 shadow md:h-14 md:w-14"
        />
        <div>
          <div className="text-3xl font-bold leading-none text-blue-900 md:text-4xl">William</div>
          <div className="-ml-0.5 text-4xl font-bold leading-none text-blue-900 md:text-5xl">Guerrand</div>
          <div className="mt-2 hidden items-center gap-3 text-base text-blue-600 md:flex">
            <span>Member Since 2026</span>
            <span className="h-1.5 w-1.5 rounded-full bg-coolblue-500" />
            <span>Member #{PLAYER.memberNumber}</span>
          </div>
        </div>
      </div>
      <div className="mt-auto grid grid-cols-4 gap-2 border-t border-coolblue-300 pt-4 text-center">
        {[
          { k: "Opponents", v: "16" },
          { k: "Matches", v: "7" },
          { k: "Legs", v: "34" },
          { k: "Darts", v: "1,162" },
        ].map((s) => (
          <div key={s.k}>
            <div className="font-montserrat text-2xl font-bold text-blue-500">{s.v}</div>
            <div className="text-sm text-blue-400">{s.k}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CompetitionCard() {
  return (
    <div className="flex h-full flex-col rounded-md border-2 border-blue-500 bg-gradient-to-b from-blue-200 via-white to-white p-4 shadow xl:p-5">
      <h2 className="font-montserrat text-lg font-bold text-blue-500">Competition Average</h2>
      <p className="mt-1 text-sm text-blue-400">Singles 501 SIDO</p>
      <div className="mt-6 flex flex-1 flex-col items-center justify-center rounded border border-dashed border-coolblue-400 bg-coolblue-200/50 px-4 py-10 text-center">
        <p className="text-sm font-semibold text-blue-500">Not enough legs to generate card</p>
        <p className="mt-1 text-xs text-blue-400">Last 100 Legs · 0</p>
      </div>
    </div>
  );
}

function LeagueSection() {
  return (
    <section className="rounded-md bg-white p-4 shadow xl:p-5">
      <h2 className="font-montserrat text-2xl font-bold text-blue-500">My Upcoming League Matches</h2>
      <h3 className="mt-1 font-montserrat text-lg font-bold text-blue-600">{PLAYER.league}</h3>
      <p className="text-sm font-semibold text-blue-500">{PLAYER.team} (Division: Tue C1)</p>
      <div className="mt-4 grid max-w-lg grid-cols-4 gap-3 text-center">
        {[
          { l: "Rank", v: "8" },
          { l: "Points", v: "35" },
          { l: "3DA", v: "29.15" },
          { l: "MPR", v: "1.21" },
        ].map((x) => (
          <div key={x.l}>
            <div className="font-montserrat text-xl font-bold text-blue-500">{x.v}</div>
            <div className="text-xs font-semibold uppercase text-blue-400">{x.l}</div>
          </div>
        ))}
      </div>
      <ul className="mt-4 divide-y divide-gray-200">
        {UPCOMING.map((m) => (
          <li
            key={m.date}
            className="flex flex-wrap items-center justify-between gap-2 py-3 text-sm text-blue-800"
          >
            <span className="font-semibold">{m.date}</span>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-bold ${
                m.home ? "bg-gray-200 text-gray-700" : "bg-yellow-400 text-blue-900"
              }`}
            >
              {m.home ? "Home" : "Away"}
            </span>
            <span className="rounded bg-gray-100 px-2 py-1 text-xs font-semibold">{m.time}</span>
            <span className="font-semibold">{m.vs}</span>
            <span className="text-blue-400">{m.venue}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}