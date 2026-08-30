# Russia postsecondary admission difficulty

Ranks Russian postsecondary schools and broad fields by the academic level they
admit. The current pass covers universities; score-gated СПО colleges belong in
the intended scope but have not yet been collected. Nothing here reflects
research output or reputation.

## The admission system

Almost every route into a Russian bachelor's or specialist programme runs on
one score. School leavers sit the ЕГЭ in their final year, each subject marked
out of 100, and a university admits on the total of the three or four subjects
its programme names. It then publishes ranked competition lists, so a place is
won against the other applicants rather than against a fixed bar.

A place is either бюджетное, paid by the state, or платное, paid by the
student, and the two are separate competitions with separate results.
For the same exact program the required ЕГЭ subjects and 0–100 scales are
normally the same on both routes, but the paid list can therefore close lower.
That is not admission without a gate: the applicant still has to meet the
program's minimums and win a place on the paid list. Paid intake can also
include applicants eligible to sit the university's own entrance tests.

The budget places are not one competition either. Olympiad winners take theirs
without sitting an exam at all, and the quotas — целевой приём for an employer
who has signed the student, особая квота for orphans and the disabled, and
since 2023 отдельная квота for the families of serving soldiers — each run
their own ranking at their own bar. The monitoring counted them separately
until 2017 and has published one blended number since.

| Route | What it ranks on | 2017 | 2025 |
| --- | --- | ---: | ---: |
| Общий конкурс | ЕГЭ total, minus achievement points | 216,545 | — |
| Олимпиады (БВИ) | An olympiad result; no exam is sat | 4,016 | 9,207 |
| Особая квота | ЕГЭ, ranked inside the quota | 12,103 | — |
| Целевой приём | ЕГЭ, ranked inside the employer's quota | 37,326 | — |
| **Бюджетные места** | | **269,994** | **357,439** |
| Платные места | ЕГЭ total, or the university's own test | 156,271 | 227,429 |
| **Full-time first degree** | | **426,265** | **584,868** |

`coverage.py` writes `data/source-coverage.tsv`, which records what each
downloaded page publishes, including the columns the ranking does not read.

## How ЕГЭ scores work

ЕГЭ is a family of subject exams, not one test with subtests. Russian,
profile-level mathematics, physics, chemistry, biology, history, geography,
social studies, literature, informatics and foreign languages each produce
their own score. A degree program names the three or four subjects it accepts,
then ranks applicants on their sum. Basic-level mathematics is a school-leaving
exam and is not the mathematics score used for university admission.

Within a subject, tasks first produce a `primary score` under that year's
marking rubric. FIPI converts it to a `test score` on the admission scale,
normally 0–100. The conversion and maximum primary score differ by subject and
can change by year. A university may add up to ten points for individual
achievements, so an applicant usually competes on 300 or 400 ЕГЭ points plus
those additions. The HSE monitoring divides that total by the number of
subjects and removes the additions where the admission list identifies them.

The downloaded FIPI index links 82 subject reports for 2019–2025. `fetch/fipi.py`
downloads all of them by default, including separate 2025 language reports.
Some reports publish a full primary- or test-score chart, while others publish
only broad score bands or summary shares; downloading every report does not
turn the missing charts into distributions.

## What one published average means

HSE publishes arithmetic means, not medians, at two levels: one for a whole
institution and one for each institution–field pair. Its fields are 66 broad
families rather than exact degree programs.

The field file is crossed, not two separate summaries: a row identifies a
year, institution, funding route and broad field. It therefore has, for
example, a distinct `budget × Physics` mean and headcount. It does not identify
the exact degree program, its required subjects or its closing score. A broad
field can pool programs with different accepted ЕГЭ combinations, so budget
and paid means are on the same per-subject 0–100 scale but are not necessarily
means of exactly the same exams.

For example, MIPT's 2025 budget row reports a 97.6 mean over 1,092 admits. Of
those, 582 were БВИ olympiad admits for whom HSE inserted a placeholder 100.
Removing those placeholders leaves 510 exam-taking admits with a 94.8612 mean.
MIPT's paid row reports 90.9 over another 143 admits. The field download also
separates its budget intake into Mathematics (98.6, 196 admits), Physics (97.4,
560), Informatics and Computer Engineering (97.7, 251), Chemical and
Biotechnology (98.2, 50), and Electronics and Communications (93.8, 35). These
are still group means, not individual-score distributions; 90.9 and 94.8612
describe admitted cohorts, not their lower admission gates.

For the two public ability tables, each route–field exam-taker mean is used as
if it were that subgroup's median and repeated for its exam-taking headcount.
БВИ seats form a separate subgroup at the top of the scale. The school value is
the seat-weighted median across every such subgroup, and the school–major value
is the same median within one broad field. This is a declared approximation:
the source contains no individual scores from which to calculate a real
median. School seat counts in those outputs come from the field file too, so
they exclude the roughly 2% of intake for which HSE publishes no field row.

## Current coverage gaps

The monitoring is a survey of full-time first-degree places won on the ЕГЭ.
It leaves out среднее профессиональное образование: colleges and техникумы that
take students after grades 9 or 11 and rank oversubscribed programs on the
school-certificate average. That is a GPA-gated postsecondary route and belongs
in this comparison. The current files contain none of its schools, intake or
grade distributions. They also omit part-time study, master's programs, and
military, police and arts institutions excluded by the monitoring. Admission
to a university on a college diploma or its own exam is inside the headcount
and outside the published ЕГЭ mean.

## The source

HSE has published the Мониторинг качества приема every year since 2010. It
collects the admission lists off every university's own site, recomputes one
number per admitted student — the competition total divided by the number of
subjects counted, with achievement points taken out where they are visible —
and averages that into a score per university and per field of study. It
covers every institution admitting on the ЕГЭ, excluding the military and
performing-arts ones, and only full-time first-degree places.

`fetch/hse.py` downloads both report families for every year the site indexes,
2011 through 2025, and `parse/hse.py` reads them into `data/admissions-*.tsv`,
809 universities across 66 укрупнённые группы in 2025 alone. Captions are
reworded almost every year, and each average is reprinted beside two decoys —
the same average with the achievement points left in, and the score of the
weakest admitted student — so `parse.hse` matches a column by the role its
caption describes rather than by its text. Several years also link a table
already filtered to universities above a size, which `fetch.hse` drops.

The monitoring gives a student admitted without exams a nominal 100 in every
subject. That is a placeholder, not a measurement, and at the most selective
universities it moves the average by several points, so `lib/admissions.py`
takes those students back out of the average and leaves them in the headcount.
The model calls the exam-taker average `scored_mean` internally. Public ranking
tables export only its percentile, not the raw score.

One more number rides along with the score and cannot be taken out. A Russian
university adds up to ten points for individual achievements — a gold medal, a
sports rank, a school essay — and the monitoring subtracts them only where the
admission list shows them. In 2025 it could not for 95 universities holding
41,407 budget places, a twelfth of the total, and their averages carry those
points. `id_deducted` marks which rows those are.

## Placing a score on the cohort

FIPI's reports contain national distributions for single subjects only. The
parser recovers 36 subject-year tables with shares in the bands 0–20, 21–40,
41–60, 61–80 and 81–100, plus the full vector test-score curve for Russian in
2023. Historical rows printed in later reports extend the observations to
2017, producing 37 subject-year distributions through 2023.

`cohort.py` linearly interpolates each subject CDF and takes their equal-weight
mean within a year. This empirical marginal CDF places HSE's per-subject score;
it is not an observed distribution of three- or four-subject combined scores,
and it does not adjust for the subjects an exact program requires. Years with
no distribution use the nearest observed year: 2011–2016 use 2017, and
2024–2025 use 2023. Sparse years remain sparse—2017 has History only, 2022 has
Informatics only, and 2023 has Informatics and Russian.

`data/cohort-model.tsv` records that carry and the contributing subjects.
`data/cohort-steps.tsv` holds the resulting annual CDF, and every public
`ability` value passes through `lib/percentile.py`. MIPT's 2025 weighted-median
score proxy of 96.6537 becomes the 98.487th percentile on the carried 2023
reference. The 655,000 people who sat compulsory Russian in 2025 remain the
population count in `assessment-pool.tsv`; seat counts no longer construct the
percentile curve.

## Outputs

- `rankings/ability-universities.tsv`: one latest-year row per school, with
  `school`, automatic `school_en`, the route–field seat-weighted median expressed
  as percentile ability, and seat counts. Raw ЕГЭ means are not exported.
- `rankings/ability-majors.tsv`: the same columns for each school and broad HSE
  field, adding `major` and automatic `major_en` labels and taking the weighted
  median over that field's routes. The source is coarser than a true major even
  though the common output schema calls the column `major`.
- `rankings/route_ability.tsv`: the same allocations split by route, with
  olympiad winners as their own route at the top of the scale.
- `rankings/ability-spread.png`: what a school summary covers, and how the
  olympiad route concentrates at the top.
- `data/admissions-universities.tsv`, `data/admissions-fields.tsv`: the parsed
  monitoring, 2011–2025.
- `data/ege-national.tsv`: compulsory-Russian participants and the national
  mean per year.
- `data/ege-report-coverage.tsv`: all 82 downloaded subject reports, their
  parsed participant counts and means, and the pages carrying primary-score,
  test-score or broad-band distributions. It is an audit of what FIPI
  published, not a claim that every chart has numerical data behind it.
- `data/ege-score-distributions.tsv`: recovered single-subject empirical CDFs
  with their report, year and extraction method.
- `data/cohort-steps.tsv`, `data/cohort-model.tsv`: the annual reference CDF
  and the observed year and subjects behind it.
- `data/source-coverage.tsv`: what each of the 60 downloaded pages publishes,
  year by year, including columns the ranking does not read.

## Rebuilding

    ./rebuild.sh

Set `PYTHON` to use a different interpreter. `parse/fipi.py` needs Poppler's
`pdftotext` and `pdftocairo`. The commands run separately as well:

    python3 -m fetch.hse            # 60 rating pages, half an hour cold
    python3 -m fetch.fipi           # all 82 linked subject reports
    python3 -m parse.hse            # data/admissions-*.tsv
    python3 -m parse.fipi           # national counts and report coverage
    python3 coverage.py             # data/source-coverage.tsv
    python3 cohort.py               # annual empirical CDF and assessment pool
    python3 translate_names.py      # refresh the Google Translate label cache
    python3 rank.py                 # school and school-major ability tables
    python3 route_ability.py        # rankings/route_ability.tsv
    python3 plot.py                 # rankings/ability-spread.png
    python3 -m unittest discover

English labels come from the local generated `data/name-english.tsv` cache.
`rank.py` stays offline; run `translate_names.py` when that cache needs filling
or refreshing.

`fetch.hse` takes years as arguments and `fetch.fipi` takes subject names, so
one year or one subject can be refreshed alone; `--force` downloads a fresh
copy of what is already present.
