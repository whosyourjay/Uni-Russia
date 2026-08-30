# Russia postsecondary admission difficulty

Ranks Russian postsecondary schools and broad fields by the academic level they
admit. The ranked pass covers universities; the official 2023 СПО institution
monitoring is also downloaded and parsed, but cannot yet be placed on the same
seat-weighted scale because its public school pages omit admission headcounts.
Nothing here reflects research output or reputation.

## The admission system

School leavers ordinarily sit the ЕГЭ in their final year, each subject marked
out of 100. A programme names three or four subjects and ranks applicants on
their total. The same programme normally asks for the same subjects whether a
student seeks a state-funded or paid place. `Бюджетные места` and `Платные
места` are therefore funding pools, not different tests; separate ranked lists
let the paid list close lower.

Admission basis and funding are separate axes. БВИ olympiad winners enter
without an entrance examination. Applicants in the target, special and
separate budget quotas compete in separate lists, but normally still use ЕГЭ
or an authorized university entrance test. Some vocational graduates, foreign
applicants and other eligible categories may take a university's own tests,
and some programmes add creative, professional or physical tests. The latest
HSE table puts university-test admits in the headcount but does not count them
separately and excludes their test results from its ЕГЭ average.

The monitoring does count its two funding pools consistently:

| Funding pool | 2017 admitted | 2025 admitted |
| --- | ---: | ---: |
| State-funded | 269,994 | 357,439 |
| Paid | 156,271 | 227,429 |
| **Full-time first degree** | **426,265** | **584,868** |

It does not offer a complete current partition by admission basis. In 2017 it
separately printed 216,545 general-competition, 4,016 БВИ, 12,103 special-quota
and 37,326 targeted admits. In 2025 it prints 9,207 БВИ admits but blends the
other budget competitions. Counts of university-test and additional-test
admits remain unknown. Broader ministry totals use different populations and
must not be inserted as if they were unclassified rows of this table.

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

For example, MIPT's 2025 budget row reports a 97.6 mean beside 1,092 admits. Of
those, 582 were БВИ olympiad admits for whom HSE inserted a placeholder 100.
Algebraically removing those placeholders leaves 510 non-БВИ seats with a
94.8612 group proxy. The current table cannot prove that all 510 are ЕГЭ takers,
because it does not separate any university-test admits from that headcount.
MIPT's paid row reports 90.9 over another 143 admits. The field download also
separates its budget intake into Mathematics (98.6, 196 admits), Physics (97.4,
560), Informatics and Computer Engineering (97.7, 251), Chemical and
Biotechnology (98.2, 50), and Electronics and Communications (93.8, 35). These
are still group means, not individual-score distributions; 90.9 and 94.8612
describe admitted cohorts, not their lower admission gates.

For the two public ability tables, each funding–field de-placeholdered mean is
used as if it were that subgroup's median and repeated for its non-БВИ
headcount.
The school value is the seat-weighted median across those subgroups, and the
school–major value is the same median within one broad field. БВИ seats have no
ЕГЭ score, so they stay in `seats` and `olympiad_seats` but not the numeric
median; `scored_seats` is the common output name for seats assigned that proxy,
not a count of people whose individual ЕГЭ scores were observed. The true ЕГЭ
score denominator is unpublished. This is a declared approximation: the source
contains no individual scores from which to calculate a real median. School
seat counts in those outputs come from the field file too, so they exclude the
roughly 2% of intake for which HSE publishes no field row.

## Current coverage gaps

The 2023 СПО monitoring index contains 4,424 colleges and техникумы. Their
standardized institution pages publish overall, budget and paid mean
school-certificate grades, the share of entrants at grade 4 or above,
applications per 100 budget places, current enrollment and broad fields
offered. They do not publish admitted headcounts, programme-level grades or a
full certificate-grade distribution. Current enrollment is retained as stock,
never relabeled as admission seats, and offered fields receive no invented
score. National СПО bulletins supply intake and one grade threshold, but cannot
connect either to an individual school.

The remaining omissions include part-time study, master's programmes, and
military, police and arts institutions excluded by HSE. Some of those sectors
cannot currently be counted on the same full-time first-degree scope, much less
scored. Admission to a university on a college diploma or its own exam is
inside HSE's headcount and outside its published ЕГЭ mean.

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
  olympiad winners retained without a numeric ability and marked explicitly for
  the top-route comparison.
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
- `data/spo-institutions.tsv`: one 2023 СПО institution per row, with published
  certificate-grade indicators and blank admission-count columns where the
  source supplies no count.
- `data/spo-fields.tsv`: broad fields offered by each СПО institution. Its score
  and admitted-student columns are deliberately blank because the public page
  does not cross its GPA indicators with fields.

## Rebuilding

    ./rebuild.sh

Set `PYTHON` to use a different interpreter. `parse/fipi.py` needs Poppler's
`pdftotext` and `pdftocairo`. The commands run separately as well:

    python3 -m fetch.hse            # 60 rating pages, half an hour cold
    python3 -m fetch.fipi           # all 82 linked subject reports
    python3 -m fetch.spo 2023       # standardized СПО institution pages
    python3 -m parse.hse            # data/admissions-*.tsv
    python3 -m parse.fipi           # national counts and report coverage
    python3 -m parse.spo            # school-level СПО GPA and offered fields
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
